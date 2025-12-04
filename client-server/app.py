import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import aiohttp
from dotenv import load_dotenv

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
# URL мини-приложения (должен быть HTTPS для Telegram WebApp)
MINIAPP_URL = os.getenv("MINIAPP_URL", f"http://localhost:{PORT}/miniapp")

# Настройка хранилища
UPLOADS_DIR = "uploads"
EXAMPLES_DIR = "examples"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(EXAMPLES_DIR, exist_ok=True)

# Инициализация Telegram бота
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - запуск бота
    logger.info("Starting Telegram bot...")
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
    
    await query.edit_message_text(
        "📸 Для анализа Instagram профиля:\n\n"
        "1. Отправьте username пользователя (например: @username или username)\n"
        "2. Отправьте скриншот статистики профиля\n\n"
        "Сейчас покажу примеры скриншотов..."
    )
    
    # Отправляем примеры скриншотов
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
    
    await query.message.reply_text(
        "✅ Теперь отправьте username пользователя, а затем скриншот его статистики."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text.strip()
    
    # Проверяем, является ли сообщение username
    if text.startswith('@'):
        username = text[1:]
    else:
        username = text
    
    # Сохраняем username в контексте пользователя
    context.user_data['username'] = username
    
    await update.message.reply_text(
        f"✅ Username получен: {username}\n\n"
        "Теперь отправьте скриншот статистики профиля.\n"
        "Скриншот должен содержать информацию о подписчиках, подписках и публикациях."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий (скриншотов)"""
    username = context.user_data.get('username')
    
    if not username:
        await update.message.reply_text(
            "❌ Сначала отправьте username пользователя Instagram."
        )
        return
    
    # Получаем файл
    photo = update.message.photo[-1]  # Берем фото наибольшего размера
    file = await telegram_app.bot.get_file(photo.file_id)
    
    # Скачиваем файл
    file_path = os.path.join(UPLOADS_DIR, f"{username}_{photo.file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
    await file.download_to_drive(file_path)
    
    # Отправляем запрос на сервер парсинга
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('username', username)
                data.add_field('screenshot', f, filename=f'{photo.file_id}.jpg')
                
                async with session.post(
                    f"{PARSING_SERVER_URL}/api/analyze",
                    data=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        await update.message.reply_text(
                            f"✅ Анализ завершен!\n\n"
                            f"📊 Данные сохранены для пользователя: {username}\n\n"
                            "Откройте мини-приложение для просмотра статистики."
                        )
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
    return templates.TemplateResponse("miniapp.html", {"request": request})


@app.get("/api/data/{username}")
async def get_user_data(username: str):
    """Получение данных пользователя из базы"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{PARSING_SERVER_URL}/api/data/{username}"
            ) as response:
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
            async with session.get(f"{PARSING_SERVER_URL}/api/users") as response:
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

