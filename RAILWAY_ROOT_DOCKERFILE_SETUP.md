# Настройка Railway с Dockerfile из корня проекта

## Подход: Dockerfile в корне + переменные окружения

Используем Dockerfile из корня проекта для обоих сервисов, настраивая их через переменные окружения.

## Для Client Server:

### Настройки Railway:

1. **Settings → Source:**
   - **Root Directory**: оставьте **ПУСТЫМ** (корень проекта)

2. **Settings → Build:**
   - **Builder**: **Dockerfile**
   - **Dockerfile Path**: `Dockerfile` (использует Dockerfile из корня)
   - **Сохраните**

3. **Settings → Variables:**
   - `TELEGRAM_BOT_TOKEN` - ваш токен
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
   - `PARSING_SERVER_URL` - URL parsing server
   - `MINIAPP_URL` - URL мини-приложения
   - `SERVICE_TYPE=client` (опционально, если нужна универсальность)

## Для Parsing Server:

### Настройки Railway:

1. **Settings → Source:**
   - **Root Directory**: оставьте **ПУСТЫМ** (корень проекта)

2. **Settings → Build:**
   - **Builder**: **Dockerfile**
   - **Dockerfile Path**: `Dockerfile.parsing` (использует специальный Dockerfile для parsing)
   - **Сохраните**

3. **Settings → Variables:**
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
   - `SERVICE_TYPE=parsing` (опционально)

## Преимущества:

- ✅ Все Dockerfile в корне проекта
- ✅ Не нужно настраивать Root Directory
- ✅ Проще управление
- ✅ Настройка через переменные окружения

## Структура:

```
VeraliA/
├── Dockerfile              # Для Client Server
├── Dockerfile.parsing      # Для Parsing Server
├── client-server/
│   ├── app.py
│   └── requirements.txt
└── parsing-server/
    ├── app.py
    └── requirements.txt
```

## Настройка в Railway:

### Client Server:
- Root Directory: **ПУСТО**
- Dockerfile Path: `Dockerfile`

### Parsing Server:
- Root Directory: **ПУСТО**
- Dockerfile Path: `Dockerfile.parsing`

## После настройки:

1. Railway найдет Dockerfile в корне проекта
2. Соберет образ по указанному Dockerfile
3. Запустит приложение с переменными окружения


