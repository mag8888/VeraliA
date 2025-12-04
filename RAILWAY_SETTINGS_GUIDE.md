# Пошаговая инструкция по настройке Railway Settings

## Для Client Server

### 1. Раздел "Source"
- **Source Repo**: `mag8888/VeraliA` (должно быть подключено)
- **Root Directory**: `client-server` (без слэша `/`)
- **Branch**: `main` (или ваша ветка)

### 2. Раздел "Build"
- **Custom Build Command**: **ПУСТО** (удалите `npm run build` если там что-то есть)
- **Dockerfile Path**: `Dockerfile` (или оставьте пустым)
- **Watch Paths**: можно оставить пустым или добавить `client-server/**`
- **Use Metal Build Environment**: выключено (OFF)

### 3. Раздел "Deploy"
- **Start Command**: можно оставить пустым (используется из Dockerfile)
- **Restart Policy**: можно оставить по умолчанию

### 4. Раздел "Variables"
Добавьте переменные окружения:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
DATABASE_URL=${{Postgres.DATABASE_URL}}
PARSING_SERVER_URL=https://ваш-parsing-server.up.railway.app
MINIAPP_URL=https://ваш-client-server.up.railway.app/miniapp
```

## Для Parsing Server

### 1. Раздел "Source"
- **Source Repo**: `mag8888/VeraliA` (должно быть подключено)
- **Root Directory**: `parsing-server` (без слэша `/`)
- **Branch**: `main` (или ваша ветка)

### 2. Раздел "Build"
- **Custom Build Command**: **ПУСТО**
- **Dockerfile Path**: `Dockerfile` (или оставьте пустым)
- **Watch Paths**: можно оставить пустым или добавить `parsing-server/**`
- **Use Metal Build Environment**: выключено (OFF)

### 3. Раздел "Deploy"
- **Start Command**: можно оставить пустым (используется из Dockerfile)
- **Restart Policy**: можно оставить по умолчанию

### 4. Раздел "Variables"
Добавьте переменные окружения:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

## Важно!

### ❌ НЕ указывайте:
- Custom Build Command для Dockerfile проектов (оставьте пустым)
- npm команды для Python проектов
- Root Directory со слэшем `/client-server` (неправильно)

### ✅ Правильно:
- Root Directory: `client-server` (без слэша)
- Custom Build Command: пусто
- Dockerfile Path: `Dockerfile` или пусто

## После настройки

1. **Сохраните все изменения**
2. Перейдите на вкладку **Deployments**
3. Нажмите **"Redeploy"** или дождитесь автоматического деплоя
4. Проверьте логи в **"View logs"**

## Если ошибка "Dockerfile does not exist"

1. Проверьте, что Root Directory установлен правильно
2. Убедитесь, что Custom Build Command пусто
3. Проверьте логи - Railway должен показать путь к Dockerfile
4. Если не помогает - пересоздайте сервис

