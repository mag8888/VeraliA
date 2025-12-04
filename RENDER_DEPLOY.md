# Деплой на Render.com (альтернатива Railway)

## Преимущества Render:
- ✅ Проще настройка
- ✅ Бесплатный план
- ✅ Автоматический деплой из GitHub
- ✅ Не требует Dockerfile (автоматическое определение)

## Шаг 1: Регистрация

1. Зайдите на [render.com](https://render.com)
2. Зарегистрируйтесь через GitHub
3. Подтвердите email

## Шаг 2: Создание Web Service

1. Нажмите **"New +"** → **"Web Service"**
2. Выберите репозиторий `mag8888/VeraliA`
3. Настройки:
   - **Name**: `verali-client` (или любое имя)
   - **Region**: выберите ближайший
   - **Branch**: `main`
   - **Root Directory**: `client-server`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
4. Нажмите **"Create Web Service"**

## Шаг 3: Настройка переменных окружения

1. В настройках сервиса → **Environment**
2. Добавьте переменные:
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен_бота
   DATABASE_URL=postgresql://... (если используете Render PostgreSQL)
   PARSING_SERVER_URL=https://ваш-parsing-server.onrender.com
   MINIAPP_URL=https://ваш-client.onrender.com/miniapp
   PORT=8000
   ```

## Шаг 4: Создание PostgreSQL (если нужно)

1. **New +** → **PostgreSQL**
2. Назовите базу данных
3. Скопируйте **Internal Database URL**
4. Используйте в переменных окружения Client Server

## Шаг 5: Создание Parsing Server

1. **New +** → **Web Service**
2. Те же настройки, но:
   - **Root Directory**: `parsing-server`
   - **Name**: `verali-parsing`

## Преимущества перед Railway:

- Не нужно настраивать Builder
- Автоматическое определение Python проекта
- Проще настройка Root Directory
- Бесплатный план с хорошими лимитами

