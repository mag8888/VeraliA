# Настройка переменных окружения в Railway

## Проблема
Приложение собралось успешно, но не может запуститься из-за отсутствия `TELEGRAM_BOT_TOKEN`.

## Решение: Добавить переменные окружения

### Шаг 1: Откройте настройки Variables

1. В Railway выберите сервис "VeraliA" (Client Server)
2. Перейдите в **Settings**
3. Нажмите **"Variables"** в правом меню (или вкладка "Variables")

### Шаг 2: Добавьте переменные для Client Server

Нажмите **"+ New Variable"** и добавьте каждую переменную:

#### 1. TELEGRAM_BOT_TOKEN
- **Key**: `TELEGRAM_BOT_TOKEN`
- **Value**: ваш токен от [@BotFather](https://t.me/BotFather)
- **Нажмите "Add"**

#### 2. DATABASE_URL
- **Key**: `DATABASE_URL`
- **Value**: `${{Postgres.DATABASE_URL}}` (замените `Postgres` на имя вашего PostgreSQL сервиса)
- **Нажмите "Add"**

#### 3. PARSING_SERVER_URL
- **Key**: `PARSING_SERVER_URL`
- **Value**: `https://ваш-parsing-server.up.railway.app` (замените на реальный URL после создания Parsing Server)
- **Нажмите "Add"**

#### 4. MINIAPP_URL
- **Key**: `MINIAPP_URL`
- **Value**: `https://ваш-client-server.up.railway.app/miniapp` (замените на реальный URL после генерации домена)
- **Нажмите "Add"**

### Шаг 3: Генерация домена для Client Server

1. **Settings** → **Networking**
2. Нажмите **"Generate Domain"**
3. Скопируйте полученный URL (например: `verali-client-production.up.railway.app`)
4. Обновите переменную `MINIAPP_URL`: `https://verali-client-production.up.railway.app/miniapp`

### Шаг 4: Переменные для Parsing Server

После создания Parsing Server:

1. Выберите сервис Parsing Server
2. **Settings** → **Variables**
3. Добавьте:
   - **Key**: `DATABASE_URL`
   - **Value**: `${{Postgres.DATABASE_URL}}`

### Шаг 5: Обновление PARSING_SERVER_URL

После создания Parsing Server и генерации домена:

1. Скопируйте URL Parsing Server
2. В Client Server → **Variables** → обновите `PARSING_SERVER_URL`

## После добавления переменных:

1. Railway автоматически перезапустит сервис
2. Проверьте логи - должно быть:
   ```
   Application started
   Bot is running
   ```

## Как получить TELEGRAM_BOT_TOKEN:

1. Откройте Telegram
2. Найдите [@BotFather](https://t.me/BotFather)
3. Отправьте команду `/newbot`
4. Следуйте инструкциям
5. Скопируйте полученный токен
6. Вставьте в переменную `TELEGRAM_BOT_TOKEN` в Railway

## Проверка переменных:

После добавления всех переменных:
- ✅ TELEGRAM_BOT_TOKEN установлен
- ✅ DATABASE_URL установлен (из PostgreSQL)
- ✅ PARSING_SERVER_URL установлен (после создания Parsing Server)
- ✅ MINIAPP_URL установлен (после генерации домена)

## Если ошибка сохраняется:

1. Проверьте, что токен правильный (без пробелов, без кавычек)
2. Убедитесь, что переменная сохранена
3. Перезапустите сервис вручную: Deployments → Redeploy

