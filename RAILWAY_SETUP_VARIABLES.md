# Настройка Railway: Dockerfile из корня + Variables

## ✅ Решение

Используем Dockerfile из корня проекта, все настройки через Variables в Railway.

---

## 🔧 Client Server

### Settings → Source:
- **Root Directory**: **ОСТАВЬТЕ ПУСТЫМ** (корень проекта)

### Settings → Build:
- **Builder**: **Dockerfile**
- **Dockerfile Path**: `Dockerfile`

### Settings → Variables:
```
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
DATABASE_URL=${{Postgres.DATABASE_URL}}
PARSING_SERVER_URL=https://parsing-server-production.up.railway.app
MINIAPP_URL=https://client-server-production.up.railway.app/miniapp
```

**Примечание:** `PORT` НЕ нужно указывать — Railway устанавливает его автоматически!

---

## 🔧 Parsing Server

### Settings → Source:
- **Root Directory**: **ОСТАВЬТЕ ПУСТЫМ** (корень проекта)

### Settings → Build:
- **Builder**: **Dockerfile**
- **Dockerfile Path**: `Dockerfile.parsing`

### Settings → Variables:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

**Примечание:** `PORT` НЕ нужно указывать — Railway устанавливает его автоматически!

---

## 📋 Шаги:

1. **Client Server:**
   - Root Directory: **ПУСТО**
   - Dockerfile Path: `Dockerfile`
   - Добавьте Variables (см. выше)

2. **Parsing Server:**
   - Root Directory: **ПУСТО**
   - Dockerfile Path: `Dockerfile.parsing`
   - Добавьте Variables (см. выше)

3. **Сохраните** и **Redeploy**

---

## ✅ Преимущества:

- ✅ Все Dockerfile в корне проекта
- ✅ Не нужно менять Root Directory
- ✅ Все настройки через Variables
- ✅ Проще управление

---

## 🔍 Проверка:

После деплоя проверьте логи:
- Client Server должен запуститься на порту, который Railway назначил автоматически
- Parsing Server должен запуститься на порту, который Railway назначил автоматически

## 📖 Подробнее о PORT:

См. файл `RAILWAY_PORT_SETUP.md` для детальной информации о настройке PORT.

