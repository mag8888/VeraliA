# Решение проблем с деплоем на Railway

## Root Directory для разных сервисов

### PostgreSQL (База данных)
- **Root Directory НЕ нужен!** 
- Это встроенный сервис Railway, который использует готовый Docker образ PostgreSQL
- Просто создайте сервис через "Database" → "Add PostgreSQL"

### Client Server и Parsing Server
- **Root Directory ОБЯЗАТЕЛЕН!**
- Для Client Server: `client-server` (без слэша)
- Для Parsing Server: `parsing-server` (без слэша)

## Ошибка: "Dockerfile `Dockerfile` does not exist"

### Проблема
Railway ищет Dockerfile в корне проекта, но у нас Dockerfile находятся в подпапках.

### Решение

1. **Откройте настройки сервиса** (Settings)
2. Найдите раздел **"Root Directory"**
3. Установите правильное значение:
   - Для **Client Server**: `client-server` (без слэша `/` в начале!)
   - Для **Parsing Server**: `parsing-server` (без слэша `/` в начале!)
   
   **Неправильно:** `/client-server` ❌
   **Правильно:** `client-server` ✅
4. **Сохраните изменения**
5. Railway автоматически перезапустит деплой

### Визуальная инструкция:

```
Settings → Root Directory → client-server (или parsing-server)
```

**Важно:** Не используйте слэш в начале! 
- ❌ Неправильно: `/client-server`
- ✅ Правильно: `client-server`

После этого Railway будет искать Dockerfile в указанной директории.

## Другие частые проблемы

### Проблема: Сервис не запускается

**Решение:**
- Проверьте логи в разделе **Deployments** → **View logs**
- Убедитесь, что все переменные окружения установлены
- Проверьте, что `DATABASE_URL` правильно подключен

### Проблема: Ошибка подключения к базе данных

**Решение:**
- Убедитесь, что используется `${{Postgres.DATABASE_URL}}`
- Проверьте, что PostgreSQL сервис запущен
- Убедитесь, что имя сервиса PostgreSQL правильное (например, `Postgres`)

### Проблема: Telegram бот не отвечает

**Решение:**
- Проверьте `TELEGRAM_BOT_TOKEN` в переменных окружения
- Проверьте логи Client Server на наличие ошибок
- Убедитесь, что токен правильный и бот активен

### Проблема: Сервисы не могут связаться друг с другом

**Решение:**
- Используйте публичные домены Railway для связи между сервисами
- Убедитесь, что `PARSING_SERVER_URL` указывает на правильный домен
- Проверьте, что оба сервиса запущены и имеют публичные домены

## Проверка конфигурации

### Правильная структура на Railway:

```
Railway Project: VeraliA
├── Postgres (Database)
│   └── DATABASE_URL (автоматически)
├── Client-Server (Service)
│   ├── Root Directory: client-server ✅
│   ├── Dockerfile найден в client-server/ ✅
│   └── Variables настроены ✅
└── Parsing-Server (Service)
    ├── Root Directory: parsing-server ✅
    ├── Dockerfile найден в parsing-server/ ✅
    └── Variables настроены ✅
```

### Неправильная конфигурация (вызывает ошибку):

```
Client-Server
├── Root Directory: (пусто или /) ❌
└── Railway ищет Dockerfile в корне репозитория ❌
```

