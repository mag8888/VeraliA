import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import aiohttp
from dotenv import load_dotenv
from cloudinary_storage import upload_image_from_bytes, get_example_urls, upload_examples_from_local
import re

load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не установлен! Установите переменную окружения в Railway.")
    raise ValueError("TELEGRAM_BOT_TOKEN обязателен для работы бота")

# Railway автоматически предоставляет PORT через переменную окружения
PORT = int(os.getenv("PORT", 8000))
# URL для связи с parsing server (Railway или локальный)
PARSING_SERVER_URL = os.getenv("PARSING_SERVER_URL", f"http://localhost:8001")
# Убеждаемся, что URL содержит протокол
if PARSING_SERVER_URL and not PARSING_SERVER_URL.startswith(('http://', 'https://')):
    PARSING_SERVER_URL = f"https://{PARSING_SERVER_URL}"
# URL мини-приложения (должен быть HTTPS для Telegram WebApp)
MINIAPP_URL = os.getenv("MINIAPP_URL", f"http://localhost:{PORT}/miniapp")

# Настройка хранилища
UPLOADS_DIR = "uploads"
EXAMPLES_DIR = "examples"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(EXAMPLES_DIR, exist_ok=True)

# Настройка Cloudinary (опционально)
USE_CLOUDINARY = os.getenv("USE_CLOUDINARY", "false").lower() == "true"
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if USE_CLOUDINARY and not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    logger.warning("Cloudinary не настроен полностью. Используется локальное хранилище.")
    USE_CLOUDINARY = False

# Инициализация Telegram бота
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


def extract_username_from_text(text: str) -> str:
    """
    Извлекает username Instagram из текста.
    Поддерживает:
    - URL: https://www.instagram.com/username?igsh=...
    - URL: https://www.instagram.com/username/
    - URL: https://www.instagram.com/username
    - @username
    - username
    """
    text = text.strip()
    
    # Если это URL Instagram
    if 'instagram.com' in text:
        # Извлекаем username из URL (игнорируем query параметры и слэши)
        match = re.search(r'instagram\.com/([^/?&#]+)', text)
        if match:
            username = match.group(1)
            # Удаляем возможные слэши и пробелы
            username = username.strip('/').strip()
            return username
    
    # Если начинается с @
    if text.startswith('@'):
        username = text[1:]
        # Удаляем возможные слэши и пробелы
        username = username.strip('/').strip()
        return username
    
    # Удаляем слэши, пробелы и другие символы
    username = text.strip('/').strip()
    
    return username


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - запуск бота
    logger.info("Starting Telegram bot...")
    
    # Загружаем примеры в Cloudinary при первом запуске (если используется Cloudinary)
    if USE_CLOUDINARY:
        logger.info("Проверка примеров скриншотов в Cloudinary...")
        try:
            upload_result = upload_examples_from_local(EXAMPLES_DIR)
            if upload_result.get("success") and upload_result.get("examples"):
                logger.info(f"Примеры загружены в Cloudinary: {len(upload_result['examples'])} файлов")
            else:
                existing_examples = get_example_urls()
                if existing_examples:
                    logger.info(f"Примеры уже есть в Cloudinary: {len(existing_examples)} файлов")
                else:
                    logger.warning("Примеры не найдены. Добавьте скриншоты в client-server/examples/")
        except Exception as e:
            logger.error(f"Ошибка при загрузке примеров: {e}")
    
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    logger.info("Telegram bot started successfully")
    yield
    # Shutdown - остановка бота
    logger.info("Stopping Telegram bot...")
    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()
    logger.info("Telegram bot stopped")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    # Проверяем параметры команды /start
    args = context.args
    if args and len(args) > 0:
        command = args[0]
        if command.startswith('upload_'):
            # Обработка команды из мини-приложения
            parts = command.split('_')
            if len(parts) >= 3:
                screenshot_type = parts[1]  # main_page или stats
                username = '_'.join(parts[2:])  # username может содержать подчеркивания
                
                context.user_data['username'] = username
                context.user_data['screenshot_type'] = screenshot_type
                
                keyboard = [
                    [
                        InlineKeyboardButton("📱 Главная страница", callback_data="upload_main_page"),
                        InlineKeyboardButton("📊 Статистика", callback_data="upload_stats")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                type_name = "главной страницы" if screenshot_type == 'main_page' else "статистики"
                await update.message.reply_text(
                    f"✅ Username получен: {username}\n\n"
                    f"Готов к загрузке скриншота {type_name}.\n"
                    f"Выберите тип скриншота или отправьте фото:",
                    reply_markup=reply_markup
                )
                return
    
    keyboard = [
        [InlineKeyboardButton(
            "📊 Открыть мини-приложение",
            web_app=WebAppInfo(url=MINIAPP_URL)
        )],
        [InlineKeyboardButton("📈 Анализ Instagram", callback_data="analyze_instagram")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Добро пожаловать в Verali!\n\n"
        "Я помогу вам анализировать Instagram профили.\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )


async def analyze_instagram_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки анализа Instagram"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("📱 Главная страница", callback_data="upload_main_page"),
            InlineKeyboardButton("📊 Статистика", callback_data="upload_stats")
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_upload")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📸 Выберите тип скриншота для загрузки:\n\n"
        "• 📱 Главная страница - скриншот профиля с основной информацией\n"
        "• 📊 Статистика - скриншот профессиональной панели\n\n"
        "Сначала отправьте username пользователя, затем выберите тип скриншота.",
        reply_markup=reply_markup
    )
    
    # Отправляем примеры скриншотов
    if USE_CLOUDINARY:
        # Получаем примеры из Cloudinary
        example_urls = get_example_urls()
        if example_urls:
            captions = [
                "📸 Пример скриншота 1:\nСкриншот профиля Instagram с основной статистикой",
                "📸 Пример скриншота 2:\nСкриншот профессиональной панели Instagram"
            ]
            for i, url in enumerate(example_urls[:2], 1):
                try:
                    await query.message.reply_photo(
                        photo=url,
                        caption=captions[i-1] if i <= len(captions) else f"📸 Пример скриншота {i}"
                    )
                except Exception as e:
                    logger.error(f"Error sending example {i} from Cloudinary: {e}")
        else:
            logger.warning("Примеры не найдены в Cloudinary. Используем локальные файлы.")
            # Fallback на локальные файлы
            examples_dir = EXAMPLES_DIR
            if os.path.exists(examples_dir):
                example_files = [f for f in os.listdir(examples_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if example_files:
                    for i, filename in enumerate(example_files[:2], 1):
                        example_path = os.path.join(examples_dir, filename)
                        if os.path.exists(example_path):
                            try:
                                with open(example_path, 'rb') as photo:
                                    await query.message.reply_photo(
                                        photo=photo,
                                        caption=f"📸 Пример скриншота {i}:\n{'Скриншот профиля Instagram с основной статистикой' if i == 1 else 'Скриншот профессиональной панели Instagram'}"
                                    )
                            except Exception as e:
                                logger.error(f"Error sending example {i}: {e}")
    else:
        # Получаем примеры из локального хранилища
        examples_dir = "examples"
        if os.path.exists(examples_dir):
            example_files = [f for f in os.listdir(examples_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if example_files:
                # Отправляем первый пример
                example_path = os.path.join(examples_dir, example_files[0])
                if os.path.exists(example_path):
                    try:
                        with open(example_path, 'rb') as photo:
                            await query.message.reply_photo(
                                photo=photo,
                                caption="📸 Пример скриншота 1:\nСкриншот профиля Instagram с основной статистикой"
                            )
                    except Exception as e:
                        logger.error(f"Error sending example 1: {e}")
                
                # Отправляем второй пример, если есть
                if len(example_files) > 1:
                    example_path = os.path.join(examples_dir, example_files[1])
                    if os.path.exists(example_path):
                        try:
                            with open(example_path, 'rb') as photo:
                                await query.message.reply_photo(
                                    photo=photo,
                                    caption="📸 Пример скриншота 2:\nСкриншот профессиональной панели Instagram"
                                )
                        except Exception as e:
                            logger.error(f"Error sending example 2: {e}")
    
    # Удаляем это сообщение, так как теперь показываем кнопки выше


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text.strip()
    
    # Извлекаем username из текста (может быть URL, @username или просто username)
    username = extract_username_from_text(text)
    
    # Сохраняем username в контексте пользователя
    context.user_data['username'] = username
    context.user_data['screenshot_type'] = None  # Сброс типа скриншота
    
    keyboard = [
        [
            InlineKeyboardButton("📱 Главная страница", callback_data="upload_main_page"),
            InlineKeyboardButton("📊 Статистика", callback_data="upload_stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Username получен: {username}\n\n"
        "Теперь выберите тип скриншота для загрузки:",
        reply_markup=reply_markup
    )


async def upload_main_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки загрузки главной страницы"""
    query = update.callback_query
    await query.answer()
    
    username = context.user_data.get('username')
    if not username:
        await query.edit_message_text(
            "❌ Сначала отправьте username пользователя Instagram."
        )
        return
    
    context.user_data['screenshot_type'] = 'main_page'
    
    await query.edit_message_text(
        f"📱 Загрузка главной страницы для: {username}\n\n"
        "Отправьте скриншот главной страницы профиля Instagram.\n"
        "Скриншот должен содержать:\n"
        "• Аватар профиля\n"
        "• Количество публикаций, подписчиков, подписок\n"
        "• Биографию"
    )


async def upload_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки загрузки статистики"""
    query = update.callback_query
    await query.answer()
    
    username = context.user_data.get('username')
    if not username:
        await query.edit_message_text(
            "❌ Сначала отправьте username пользователя Instagram."
        )
        return
    
    context.user_data['screenshot_type'] = 'stats'
    
    await query.edit_message_text(
        f"📊 Загрузка статистики для: {username}\n\n"
        "Отправьте скриншот профессиональной панели Instagram.\n"
        "Скриншот должен содержать:\n"
        "• Просмотры профиля\n"
        "• Взаимодействия\n"
        "• Новые подписчики\n"
        "• Детальную статистику"
    )


async def cancel_upload_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки отмены"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['username'] = None
    context.user_data['screenshot_type'] = None
    
    await query.edit_message_text(
        "❌ Загрузка отменена.\n\n"
        "Используйте /start для начала работы."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий (скриншотов)"""
    username = context.user_data.get('username')
    screenshot_type = context.user_data.get('screenshot_type')
    
    if not username:
        await update.message.reply_text(
            "❌ Сначала отправьте username пользователя Instagram."
        )
        return
    
    if not screenshot_type:
        keyboard = [
            [
                InlineKeyboardButton("📱 Главная страница", callback_data="upload_main_page"),
                InlineKeyboardButton("📊 Статистика", callback_data="upload_stats")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ Выберите тип скриншота перед отправкой:",
            reply_markup=reply_markup
        )
        return
    
    # Получаем файл
    photo = update.message.photo[-1]  # Берем фото наибольшего размера
    file = await telegram_app.bot.get_file(photo.file_id)
    
    # Скачиваем файл
    file_bytes = await file.download_as_bytearray()
    file_path = None
    cloudinary_url = None
    
    if USE_CLOUDINARY:
        # Загружаем в Cloudinary
        public_id = f"verali/uploads/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = upload_image_from_bytes(file_bytes, folder="verali/uploads", public_id=public_id)
        if result.get("success"):
            cloudinary_url = result.get("url")
            logger.info(f"Изображение загружено в Cloudinary: {cloudinary_url}")
        else:
            logger.error(f"Ошибка загрузки в Cloudinary: {result.get('error')}")
            # Fallback на локальное хранилище
            file_path = os.path.join(UPLOADS_DIR, f"{username}_{photo.file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
    else:
        # Сохраняем локально
        file_path = os.path.join(UPLOADS_DIR, f"{username}_{photo.file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
    
    # Отправляем запрос на сервер парсинга
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('username', username)
            
            # Используем файл из Cloudinary или локального хранилища
            if cloudinary_url:
                # Если файл в Cloudinary, отправляем URL
                data.add_field('screenshot_url', cloudinary_url)
                # Также отправляем файл для парсинга
                data.add_field('screenshot', file_bytes, filename=f'{username}.jpg', content_type='image/jpeg')
            elif file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    data.add_field('screenshot', f, filename=f'{username}.jpg')
            else:
                # Отправляем байты напрямую
                data.add_field('screenshot', file_bytes, filename=f'{username}.jpg', content_type='image/jpeg')
                
            # Формируем правильный URL для парсинга
            parse_url = f"{PARSING_SERVER_URL}/api/analyze"
            if not parse_url.startswith(('http://', 'https://')):
                parse_url = f"https://{parse_url}"
            
            logger.info(f"Отправка запроса на парсинг: {parse_url}")
            
            async with session.post(
                parse_url,
                data=data
            ) as response:
                    if response.status == 200:
                        result = await response.json()
                        screenshot_type_name = "главной страницы" if screenshot_type == 'main_page' else "статистики"
                        await update.message.reply_text(
                            f"✅ Скриншот {screenshot_type_name} загружен!\n\n"
                            f"📊 Данные сохранены для пользователя: {username}\n\n"
                            "Откройте мини-приложение для просмотра статистики."
                        )
                        # Сброс типа скриншота после успешной загрузки
                        context.user_data['screenshot_type'] = None
                    else:
                        error_text = await response.text()
                        await update.message.reply_text(
                            f"❌ Ошибка при анализе: {error_text}"
                        )
    except Exception as e:
        logger.error(f"Error sending to parsing server: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при отправке данных на сервер парсинга."
        )


# Регистрация обработчиков
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CallbackQueryHandler(analyze_instagram_callback, pattern="^analyze_instagram$"))
telegram_app.add_handler(CallbackQueryHandler(upload_main_page_callback, pattern="^upload_main_page$"))
telegram_app.add_handler(CallbackQueryHandler(upload_stats_callback, pattern="^upload_stats$"))
telegram_app.add_handler(CallbackQueryHandler(cancel_upload_callback, pattern="^cancel_upload$"))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))


# FastAPI приложение с lifespan
app = FastAPI(title="Verali Client Server", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


# FastAPI маршруты
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Verali Client Server</title>
        </head>
        <body>
            <h1>Verali Client Server</h1>
            <p>Сервер работает корректно</p>
        </body>
    </html>
    """


@app.get("/miniapp", response_class=HTMLResponse)
async def miniapp(request: Request):
    """Мини-приложение для отображения данных"""
    # Получаем username бота через API
    try:
        bot_info = await telegram_app.bot.get_me()
        bot_username = bot_info.username
    except Exception as e:
        logger.error(f"Ошибка получения username бота: {e}")
        bot_username = BOT_USERNAME
    
    return templates.TemplateResponse("miniapp.html", {
        "request": request,
        "bot_username": bot_username
    })


@app.post("/api/upload-screenshot")
async def upload_screenshot_from_miniapp(
    request: Request,
    username: str = Form(...),
    screenshot_type: str = Form(...),
    screenshot: UploadFile = File(...)
):
    """API endpoint для загрузки скриншотов из мини-приложения"""
    try:
        # Извлекаем username из текста (может быть URL)
        username = extract_username_from_text(username)
        # Читаем файл
        file_bytes = await screenshot.read()
        
        # Загружаем в Cloudinary или локально
        file_path = None
        cloudinary_url = None
        
        if USE_CLOUDINARY:
            # Загружаем в Cloudinary
            public_id = f"verali/uploads/{username}_{screenshot_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = upload_image_from_bytes(file_bytes, folder="verali/uploads", public_id=public_id)
            if result.get("success"):
                cloudinary_url = result.get("url")
                logger.info(f"Изображение загружено в Cloudinary: {cloudinary_url}")
            else:
                logger.error(f"Ошибка загрузки в Cloudinary: {result.get('error')}")
                # Fallback на локальное хранилище
                file_path = os.path.join(UPLOADS_DIR, f"{username}_{screenshot_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
        else:
            # Сохраняем локально
            file_path = os.path.join(UPLOADS_DIR, f"{username}_{screenshot_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
        
        # Отправляем на сервер парсинга
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('username', username)
            data.add_field('screenshot_type', screenshot_type)
            
            # Используем файл из Cloudinary или локального хранилища
            if cloudinary_url:
                data.add_field('screenshot_url', cloudinary_url)
                data.add_field('screenshot', file_bytes, filename=f'{username}_{screenshot_type}.jpg', content_type='image/jpeg')
            elif file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    data.add_field('screenshot', f, filename=f'{username}_{screenshot_type}.jpg')
            else:
                data.add_field('screenshot', file_bytes, filename=f'{username}_{screenshot_type}.jpg', content_type='image/jpeg')
            
            # Формируем правильный URL для парсинга
            parse_url = f"{PARSING_SERVER_URL}/api/analyze"
            if not parse_url.startswith(('http://', 'https://')):
                parse_url = f"https://{parse_url}"
            
            logger.info(f"Отправка запроса на парсинг: {parse_url}")
            
            async with session.post(
                parse_url,
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return JSONResponse({
                        "success": True,
                        "message": f"Скриншот {screenshot_type} загружен и обработан",
                        "data": result
                    })
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка парсинга: {error_text}")
                    return JSONResponse(
                        {"success": False, "error": f"Ошибка обработки: {error_text}"},
                        status_code=response.status
                    )
    
    except Exception as e:
        logger.error(f"Ошибка загрузки скриншота: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


@app.get("/api/data/{username}")
async def get_user_data(username: str):
    """Получение данных пользователя из базы"""
    try:
        async with aiohttp.ClientSession() as session:
            # Формируем правильный URL
            data_url = f"{PARSING_SERVER_URL}/api/data/{username}"
            if not data_url.startswith(('http://', 'https://')):
                data_url = f"https://{data_url}"
            
            async with session.get(data_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/users")
async def get_all_users():
    """Получение списка всех пользователей"""
    try:
        async with aiohttp.ClientSession() as session:
            # Формируем правильный URL
            users_url = f"{PARSING_SERVER_URL}/api/users"
            if not users_url.startswith(('http://', 'https://')):
                users_url = f"https://{users_url}"
            
            async with session.get(users_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []


if __name__ == "__main__":
    import uvicorn
    # Запускаем FastAPI сервер (бот запустится через lifespan)
    uvicorn.run(app, host="0.0.0.0", port=PORT)

