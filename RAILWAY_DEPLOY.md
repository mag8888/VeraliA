# Инструкция по деплою на Railway

Railway - это платформа для деплоя приложений, которая автоматически обрабатывает сборку и развертывание.

## Архитектура на Railway

На Railway нужно создать 3 отдельных сервиса:
1. **PostgreSQL** - база данных (встроенный сервис Railway)
2. **Client Server** - Telegram бот и мини-приложение
3. **Parsing Server** - сервер парсинга Instagram

## Шаг 1: Регистрация и создание проекта

1. Зайдите на [Railway.app](https://railway.app/)
2. Войдите через GitHub аккаунт
3. Нажмите **"New Project"**
4. Выберите **"Deploy from GitHub repo"**
5. Выберите репозиторий `mag8888/VeraliA`

## Шаг 2: Создание базы данных PostgreSQL

1. В созданном проекте нажмите **"+ New"**
2. Выберите **"Database"** → **"Add PostgreSQL"**
3. Railway автоматически создаст PostgreSQL сервис
4. Запомните название сервиса (например: `Postgres`)

## Шаг 3: Создание Client Server

1. В проекте нажмите **"+ New"**
2. Выберите **"GitHub Repo"** → выберите `VeraliA`
3. В настройках сервиса:
   - **Root Directory**: `client-server`
   - **Build Command**: (оставить пустым, используется Dockerfile)
   - **Start Command**: (оставить пустым, используется Dockerfile)

4. Railway автоматически обнаружит `Dockerfile` в `client-server/`

## Шаг 4: Создание Parsing Server

1. В проекте нажмите **"+ New"**
2. Выберите **"GitHub Repo"** → выберите `VeraliA`
3. В настройках сервиса:
   - **Root Directory**: `parsing-server`
   - **Build Command**: (оставить пустым)
   - **Start Command**: (оставить пустым)

## Шаг 5: Настройка переменных окружения

### Для Client Server:

В настройках сервиса Client Server → **Variables**:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=${{Postgres.DATABASE_URL}}
PARSING_SERVER_URL=${{Parsing-Server.RAILWAY_PUBLIC_DOMAIN}}
MINIAPP_URL=${{Client-Server.RAILWAY_PUBLIC_DOMAIN}}/miniapp
PORT=8000
```

**Важно:**
- `${{Postgres.DATABASE_URL}}` - Railway автоматически подставит URL базы данных
- `${{Parsing-Server.RAILWAY_PUBLIC_DOMAIN}}` - замените на реальное имя вашего сервиса парсинга
- `${{Client-Server.RAILWAY_PUBLIC_DOMAIN}}` - замените на реальное имя вашего клиентского сервиса

### Для Parsing Server:

В настройках сервиса Parsing Server → **Variables**:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
PORT=8001
```

## Шаг 6: Настройка публичных доменов

1. Для **Client Server**:
   - Settings → **Generate Domain**
   - Скопируйте полученный URL (например: `client-server-production.up.railway.app`)
   - Обновите `MINIAPP_URL` в переменных окружения: `https://client-server-production.up.railway.app/miniapp`

2. Для **Parsing Server**:
   - Settings → **Generate Domain** (опционально, если нужен публичный доступ)
   - Или используйте внутренний Railway URL для связи между сервисами

## Шаг 7: Настройка внутренних URL (для связи сервисов)

Railway предоставляет внутренние URL для связи между сервисами:

- В Client Server используйте: `${{Parsing-Server.RAILWAY_PRIVATE_DOMAIN}}` или `${{Parsing-Server.RAILWAY_PUBLIC_DOMAIN}}`
- Формат: `https://parsing-server-production.up.railway.app`

## Шаг 8: Деплой

1. Railway автоматически начнет деплой после настройки
2. Проверьте логи в разделе **Deployments**
3. Убедитесь, что все сервисы запущены (зеленый индикатор)

## Шаг 9: Проверка работы

1. Проверьте логи Client Server - должен быть запущен Telegram бот
2. Проверьте логи Parsing Server - должен быть запущен API сервер
3. Проверьте подключение к базе данных в логах обоих сервисов

## Обновление переменных окружения

После генерации доменов обновите:

**Client Server → Variables:**
```env
PARSING_SERVER_URL=https://your-parsing-server-domain.up.railway.app
MINIAPP_URL=https://your-client-server-domain.up.railway.app/miniapp
```

## Troubleshooting

### Проблема: Сервис не запускается

- Проверьте логи в разделе **Deployments**
- Убедитесь, что все переменные окружения установлены
- Проверьте, что DATABASE_URL правильно подключен

### Проблема: Ошибка подключения к базе данных

- Убедитесь, что используется `${{Postgres.DATABASE_URL}}`
- Проверьте, что PostgreSQL сервис запущен

### Проблема: Telegram бот не отвечает

- Проверьте `TELEGRAM_BOT_TOKEN` в переменных окружения
- Проверьте логи Client Server на наличие ошибок

### Проблема: Сервисы не могут связаться друг с другом

- Используйте публичные домены Railway для связи между сервисами
- Или настройте Railway Service Mesh (для платных планов)

## Структура проекта на Railway

```
Railway Project: VeraliA
├── Postgres (Database)
│   └── DATABASE_URL (автоматически)
├── Client-Server (Service)
│   ├── Root: client-server/
│   ├── Dockerfile
│   └── Variables:
│       ├── TELEGRAM_BOT_TOKEN
│       ├── DATABASE_URL
│       ├── PARSING_SERVER_URL
│       └── MINIAPP_URL
└── Parsing-Server (Service)
    ├── Root: parsing-server/
    ├── Dockerfile
    └── Variables:
        ├── DATABASE_URL
        └── PORT
```

## Полезные ссылки

- [Railway Documentation](https://docs.railway.app/)
- [Railway Variables](https://docs.railway.app/develop/variables)
- [Railway Networking](https://docs.railway.app/develop/networking)

