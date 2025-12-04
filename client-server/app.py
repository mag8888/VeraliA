import os
import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
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

# Уменьшаем уровень логирования для httpx и telegram, чтобы не засорять логи рутинными запросами
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)

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
    
    # Устанавливаем команды бота (кнопки в меню)
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("profile", "Мои профили")
    ]
    await telegram_app.bot.set_my_commands(commands)
    
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
            
            # Увеличиваем таймаут для парсинга
            timeout = aiohttp.ClientTimeout(total=120)  # 2 минуты
                
            try:
                async with session.post(
                    parse_url,
                    data=data,
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        screenshot_type_name = "главной страницы" if screenshot_type == 'main_page' else "статистики"
                        
                        # Отправляем уведомление с кнопками
                        keyboard = [
                            [
                                InlineKeyboardButton("📱 Посмотреть в приложении", web_app=WebAppInfo(url=MINIAPP_URL)),
                                InlineKeyboardButton("📊 Посмотреть в боте", callback_data=f"view_profile_{username}")
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await update.message.reply_text(
                            f"✅ Анализ вашего профиля завершен!\n\n"
                            f"📊 Данные сохранены для пользователя: @{username}\n\n"
                            f"Скриншот {screenshot_type_name} успешно обработан.",
                            reply_markup=reply_markup
                        )
                        # Сброс типа скриншота после успешной загрузки
                        context.user_data['screenshot_type'] = None
                    else:
                        error_text = await response.text()
                        try:
                            error_json = await response.json()
                            error_message = error_json.get('message', error_json.get('detail', error_text))
                        except:
                            error_message = error_text
                        
                        await update.message.reply_text(
                            f"❌ Ошибка при анализе: {error_message}"
                        )
            except aiohttp.ClientError as e:
                logger.error(f"Ошибка соединения с parsing server: {e}")
                await update.message.reply_text(
                    f"❌ Parsing Server недоступен. Проверьте настройки PARSING_SERVER_URL."
                )
    except Exception as e:
        logger.error(f"Error sending to parsing server: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при отправке данных на сервер парсинга."
        )


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /profile - показывает список загруженных профилей"""
    try:
        # Получаем список всех профилей из Parsing Server
        async with aiohttp.ClientSession() as session:
            users_url = f"{PARSING_SERVER_URL}/api/users"
            if not users_url.startswith(('http://', 'https://')):
                users_url = f"https://{users_url}"
            
            async with session.get(users_url) as response:
                if response.status == 200:
                    data = await response.json()
                    profiles = data.get('users', [])
                    
                    if not profiles:
                        await update.message.reply_text(
                            "📭 У вас пока нет загруженных профилей.\n\n"
                            "Используйте команду /start для начала анализа."
                        )
                        return
                    
                    # Формируем сообщение со списком профилей
                    message = f"📊 Ваши профили ({len(profiles)}):\n\n"
                    
                    # Создаем кнопки для каждого профиля
                    keyboard = []
                    for i, profile in enumerate(profiles[:10], 1):  # Показываем максимум 10 профилей
                        username = profile.get('username', 'N/A')
                        followers = profile.get('followers', 0)
                        posts_count = profile.get('posts_count', 0)
                        engagement_rate = profile.get('engagement_rate', 0)
                        
                        # Форматируем данные
                        followers_str = f"{followers:,}" if followers < 1000 else f"{followers/1000:.1f}K"
                        er_str = f"{engagement_rate * 100:.1f}%" if engagement_rate else "N/A"
                        
                        message += (
                            f"{i}. @{username}\n"
                            f"   👥 {followers_str} • 📸 {posts_count} • 📈 {er_str}\n\n"
                        )
                        
                        # Добавляем кнопку для просмотра профиля
                        keyboard.append([
                            InlineKeyboardButton(
                                f"📊 @{username}",
                                callback_data=f"view_profile_{username}"
                            )
                        ])
                    
                    if len(profiles) > 10:
                        message += f"\n... и еще {len(profiles) - 10} профилей"
                    
                    # Добавляем кнопку для открытия мини-приложения
                    keyboard.append([
                        InlineKeyboardButton(
                            "📱 Открыть мини-приложение",
                            web_app=WebAppInfo(url=MINIAPP_URL)
                        )
                    ])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        message,
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text(
                        "❌ Не удалось загрузить список профилей. Попробуйте позже."
                    )
    except Exception as e:
        logger.error(f"Ошибка при получении списка профилей: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при загрузке списка профилей."
        )


async def view_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки просмотра профиля в боте"""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем username из callback_data (формат: view_profile_{username})
    callback_data = query.data
    username = callback_data.replace("view_profile_", "")
    
    try:
        # Получаем данные из Parsing Server
        async with aiohttp.ClientSession() as session:
            data_url = f"{PARSING_SERVER_URL}/api/data/{username}"
            if not data_url.startswith(('http://', 'https://')):
                data_url = f"https://{data_url}"
            
            async with session.get(data_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Формируем сообщение с данными профиля
                    profile_data = data.get('data', {})
                    followers = profile_data.get('followers', 0)
                    following = profile_data.get('following', 0)
                    posts_count = profile_data.get('posts_count', 0)
                    bio = profile_data.get('bio', 'Не указано')
                    engagement_rate = profile_data.get('engagement_rate', 0)
                    
                    message = (
                        f"📊 Профиль: @{username}\n\n"
                        f"👥 Подписчики: {followers:,}\n"
                        f"👤 Подписки: {following:,}\n"
                        f"📸 Публикации: {posts_count:,}\n"
                        f"📈 Engagement Rate: {engagement_rate * 100:.2f}%\n\n"
                        f"📝 О себе:\n{bio}\n\n"
                        f"📱 Для детального отчета откройте мини-приложение"
                    )
                    
                    keyboard = [
                        [InlineKeyboardButton("📱 Открыть мини-приложение", web_app=WebAppInfo(url=MINIAPP_URL))]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(message, reply_markup=reply_markup)
                else:
                    await query.edit_message_text(
                        f"❌ Не удалось загрузить данные для профиля @{username}"
                    )
    except Exception as e:
        logger.error(f"Ошибка при получении данных профиля: {e}")
        await query.edit_message_text(
            f"❌ Произошла ошибка при загрузке данных профиля."
        )


telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("profile", profile_command))
telegram_app.add_handler(CallbackQueryHandler(analyze_instagram_callback, pattern="^analyze_instagram$"))
telegram_app.add_handler(CallbackQueryHandler(upload_main_page_callback, pattern="^upload_main_page$"))
telegram_app.add_handler(CallbackQueryHandler(upload_stats_callback, pattern="^upload_stats$"))
telegram_app.add_handler(CallbackQueryHandler(cancel_upload_callback, pattern="^cancel_upload$"))
telegram_app.add_handler(CallbackQueryHandler(view_profile_callback, pattern="^view_profile_"))
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


@app.post("/api/send-notification")
async def send_notification(
    user_id: int = Form(...),
    username: str = Form(...)
):
    """Отправка уведомления пользователю после завершения парсинга"""
    try:
        keyboard = [
            [
                InlineKeyboardButton("📱 Посмотреть в приложении", web_app=WebAppInfo(url=MINIAPP_URL)),
                InlineKeyboardButton("📊 Посмотреть в боте", callback_data=f"view_profile_{username}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await telegram_app.bot.send_message(
            chat_id=user_id,
            text=f"✅ Анализ вашего профиля завершен!\n\n"
                 f"📊 Данные сохранены для пользователя: @{username}\n\n"
                 f"Откройте мини-приложение или бота для просмотра результатов.",
            reply_markup=reply_markup
        )
        
        return JSONResponse({"success": True, "message": "Уведомление отправлено"})
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


async def process_screenshot_analysis(username: str, screenshot_type: str, file_bytes: bytes, file_path: str = None, cloudinary_url: str = None, user_id: int = None):
    """Асинхронная обработка скриншота в фоне с отправкой уведомления"""
    try:
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
            
            logger.info(f"Начало фоновой обработки для {username}...")
            
            # Увеличиваем таймаут для парсинга (может занять время, особенно с GPT)
            timeout = aiohttp.ClientTimeout(total=300)  # 5 минут для GPT анализа
            
            try:
                async with session.post(
                    parse_url,
                    data=data,
                    timeout=timeout
                ) as response:
                    logger.info(f"Получен ответ от Parsing Server: статус {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Анализ завершен для {username}")
                        
                        # Отправляем уведомление пользователю, если указан user_id
                        if user_id:
                            try:
                                keyboard = [
                                    [
                                        InlineKeyboardButton("📱 Посмотреть в приложении", web_app=WebAppInfo(url=MINIAPP_URL)),
                                        InlineKeyboardButton("📊 Посмотреть в боте", callback_data=f"view_profile_{username}")
                                    ]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                
                                await telegram_app.bot.send_message(
                                    chat_id=user_id,
                                    text=f"✅ Анализ вашего профиля завершен!\n\n"
                                         f"📊 Данные сохранены для пользователя: @{username}\n\n"
                                         f"Откройте мини-приложение или бота для просмотра результатов.",
                                    reply_markup=reply_markup
                                )
                                logger.info(f"Уведомление отправлено пользователю {user_id}")
                            except Exception as e:
                                logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
                        
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка парсинга: {error_text}")
                        
                        # Отправляем уведомление об ошибке
                        if user_id:
                            try:
                                await telegram_app.bot.send_message(
                                    chat_id=user_id,
                                    text=f"❌ Произошла ошибка при анализе профиля @{username}.\n\n"
                                         f"Попробуйте загрузить скриншот еще раз."
                                )
                            except Exception as e:
                                logger.error(f"Ошибка отправки уведомления об ошибке: {e}")
            except asyncio.TimeoutError as e:
                logger.error(f"Таймаут при обращении к Parsing Server: {e}")
                if user_id:
                    try:
                        await telegram_app.bot.send_message(
                            chat_id=user_id,
                            text=f"⏱ Анализ профиля @{username} занимает больше времени, чем ожидалось.\n\n"
                                 f"Мы продолжим обработку в фоне и отправим уведомление, когда анализ будет завершен."
                        )
                    except Exception as e2:
                        logger.error(f"Ошибка отправки уведомления о таймауте: {e2}")
            except aiohttp.ClientError as e:
                logger.error(f"Ошибка соединения с parsing server: {e}")
                if user_id:
                    try:
                        await telegram_app.bot.send_message(
                            chat_id=user_id,
                            text=f"❌ Ошибка соединения с сервером анализа.\n\n"
                                 f"Попробуйте позже."
                        )
                    except Exception as e2:
                        logger.error(f"Ошибка отправки уведомления об ошибке соединения: {e2}")
    except Exception as e:
        logger.error(f"Ошибка фоновой обработки скриншота: {e}")
        if user_id:
            try:
                await telegram_app.bot.send_message(
                    chat_id=user_id,
                    text=f"❌ Произошла ошибка при обработке скриншота для @{username}.\n\n"
                         f"Попробуйте загрузить скриншот еще раз."
                )
            except Exception as e2:
                logger.error(f"Ошибка отправки уведомления об ошибке: {e2}")


@app.post("/api/upload-screenshot")
async def upload_screenshot_from_miniapp(
    background_tasks: BackgroundTasks,
    request: Request,
    username: str = Form(...),
    screenshot_type: str = Form(...),
    screenshot: UploadFile = File(...),
    user_id: int = Form(None)  # Опциональный user_id из Telegram WebApp
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
        
        # Запускаем обработку в фоне
        background_tasks.add_task(
            process_screenshot_analysis,
            username=username,
            screenshot_type=screenshot_type,
            file_bytes=file_bytes,
            file_path=file_path,
            cloudinary_url=cloudinary_url,
            user_id=user_id
        )
        
        # Сразу возвращаем ответ, что файл принят
        return JSONResponse({
            "success": True,
            "message": "Скриншот принят в обработку. Анализ может занять некоторое время.",
            "processing": True,
            "username": username
        })
    
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


@app.get("/api/report/{username}")
async def get_user_report(username: str):
    """Получение детального отчета по профилю"""
    try:
        async with aiohttp.ClientSession() as session:
            # Формируем правильный URL
            report_url = f"{PARSING_SERVER_URL}/api/report/{username}"
            if not report_url.startswith(('http://', 'https://')):
                report_url = f"https://{report_url}"
            
            async with session.get(report_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        logger.error(f"Error fetching report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/create-screenshot/{username}")
async def create_screenshot_endpoint(username: str):
    """
    Создает скриншот Instagram профиля автоматически
    
    Args:
        username: Username Instagram профиля или URL
        
    Returns:
        dict: Результат создания скриншота
    """
    try:
        # Извлекаем username
        username = extract_username_from_text(username)
        
        async with aiohttp.ClientSession() as session:
            # Формируем правильный URL
            screenshot_url = f"{PARSING_SERVER_URL}/api/screenshot/{username}"
            if not screenshot_url.startswith(('http://', 'https://')):
                screenshot_url = f"https://{screenshot_url}"
            
            logger.info(f"Запрос на создание скриншота: {screenshot_url}")
            
            async with session.post(screenshot_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status == 200:
                    result = await response.json()
                    return JSONResponse(result)
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка создания скриншота: {error_text}")
                    return JSONResponse(
                        {"success": False, "error": error_text},
                        status_code=response.status
                    )
    except Exception as e:
        logger.error(f"Ошибка при создании скриншота: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )


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
                    data = await response.json()
                    # Обеспечиваем совместимость с форматом {"users": [...]}
                    if isinstance(data, list):
                        return {"users": data}
                    # Если уже есть users, возвращаем как есть
                    if "users" in data:
                        return data
                    # Иначе оборачиваем в users
                    return {"users": [data] if isinstance(data, dict) else data}
                else:
                    return {"users": []}
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return {"users": []}


if __name__ == "__main__":
    import uvicorn
    # Запускаем FastAPI сервер (бот запустится через lifespan)
    uvicorn.run(app, host="0.0.0.0", port=PORT)

