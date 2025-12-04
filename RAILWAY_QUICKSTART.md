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
- **Root Directory НЕ нужен!** Это встроенный сервис базы данных

#### Client Server
- **+ New** → **GitHub Repo** → выберите `VeraliA`
- **ВАЖНО!** После создания:
  - **Settings** → **Root Directory**: `client-server` (без слэша `/`!)
  - Сохраните изменения
- Railway автоматически найдет Dockerfile в `client-server/`

#### Parsing Server  
- **+ New** → **GitHub Repo** → выберите `VeraliA`
- **ВАЖНО!** После создания:
  - **Settings** → **Root Directory**: `parsing-server` (без слэша `/`!)
  - Сохраните изменения
- Railway автоматически найдет Dockerfile в `parsing-server/`

### 3. Переменные окружения

#### Client Server Variables:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
DATABASE_URL=${{Postgres.DATABASE_URL}}
PARSING_SERVER_URL=https://parsing-server-production.up.railway.app
MINIAPP_URL=https://client-server-production.up.railway.app/miniapp
```

**Важно:**
- `PORT` - **НЕ нужно указывать вручную!** Railway автоматически устанавливает переменную `PORT` (может быть 8080, 8000 или другой порт, который вы указали при создании сервиса)
- `MINIAPP_URL` - это публичный HTTPS URL вашего **клиентского сервера** + `/miniapp`
- Это URL, который открывается при нажатии на кнопку мини-приложения в Telegram боте
- Должен быть HTTPS (Railway предоставляет автоматически)

#### Parsing Server Variables:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

**Важно:**
- `PORT` - **НЕ нужно указывать вручную!** Railway автоматически устанавливает переменную `PORT`

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

## Решение проблем

Если видите ошибку "Dockerfile does not exist":
1. Откройте **Settings** сервиса
2. Установите **Root Directory**: `client-server` или `parsing-server`
3. Сохраните и перезапустите деплой

См. [RAILWAY_TROUBLESHOOTING.md](./RAILWAY_TROUBLESHOOTING.md) для решения проблем.

## Полная инструкция

См. [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) для детальной инструкции.

