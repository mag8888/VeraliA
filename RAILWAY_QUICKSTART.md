# Railway Quick Start Guide

## Быстрый деплой на Railway

### 1. Подготовка

1. Зайдите на [railway.app](https://railway.app/)
2. Войдите через GitHub
3. Создайте новый проект из репозитория `mag8888/VeraliA`

### 2. Создание сервисов

#### PostgreSQL Database
- **+ New** → **Database** → **Add PostgreSQL**
- Запомните имя сервиса (например: `Postgres`)

#### Client Server
- **+ New** → **GitHub Repo** → выберите `VeraliA`
- **Settings** → **Root Directory**: `client-server`
- Railway автоматически найдет Dockerfile

#### Parsing Server  
- **+ New** → **GitHub Repo** → выберите `VeraliA`
- **Settings** → **Root Directory**: `parsing-server`

### 3. Переменные окружения

#### Client Server Variables:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
DATABASE_URL=${{Postgres.DATABASE_URL}}
PARSING_SERVER_URL=https://parsing-server-production.up.railway.app
MINIAPP_URL=https://client-server-production.up.railway.app/miniapp
PORT=8000
```

#### Parsing Server Variables:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
PORT=8001
```

**Важно:** Замените домены на реальные после генерации!

### 4. Генерация доменов

Для каждого сервиса:
- **Settings** → **Generate Domain**
- Скопируйте полученный URL
- Обновите переменные окружения с реальными URL

### 5. Деплой

Railway автоматически начнет деплой. Проверьте логи в **Deployments**.

## Проверка работы

1. Проверьте логи Client Server - должен быть запущен бот
2. Проверьте логи Parsing Server - должен быть запущен API
3. Протестируйте бота в Telegram

## Полная инструкция

См. [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) для детальной инструкции.

