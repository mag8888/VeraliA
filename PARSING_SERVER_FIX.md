# Исправление ошибки Parsing Server

## ❌ Проблема:

Parsing Server запускает код Client Server, который требует `TELEGRAM_BOT_TOKEN`.

Ошибка:
```
ValueError: TELEGRAM_BOT_TOKEN обязателен для работы бота
```

## 🔍 Причина:

В Railway для Parsing Server используется **неправильный Dockerfile**:
- Используется `Dockerfile` (для Client Server) вместо `Dockerfile.parsing`
- Или Root Directory установлен неправильно

---

## ✅ Решение:

### Проверьте настройки Parsing Server в Railway:

1. **Откройте Parsing Server** в Railway
2. Перейдите в **Settings → Build**
3. Проверьте:
   - **Root Directory**: должно быть **ПУСТО** (корень проекта)
   - **Dockerfile Path**: должно быть **`Dockerfile.parsing`** (НЕ `Dockerfile`!)

### Правильные настройки:

```
Root Directory: (пусто)
Dockerfile Path: Dockerfile.parsing
Builder: Dockerfile
```

### Неправильные настройки (вызывают ошибку):

```
Root Directory: parsing-server  ❌
Dockerfile Path: Dockerfile  ❌
```

---

## 📋 Шаги для исправления:

1. **Settings → Build:**
   - **Root Directory**: удалите значение (оставьте пустым)
   - **Dockerfile Path**: установите `Dockerfile.parsing`
   - **Builder**: выберите `Dockerfile`
   - **Сохраните**

2. **Settings → Variables:**
   - Убедитесь, что есть только:
     ```
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     ```
   - **НЕ добавляйте** `TELEGRAM_BOT_TOKEN` (он нужен только для Client Server)

3. **Redeploy** сервис

---

## ✅ После исправления:

Parsing Server должен:
- ✅ Использовать `Dockerfile.parsing`
- ✅ Копировать файлы из `parsing-server/`
- ✅ Запускать `parsing-server/app.py` (который НЕ требует TELEGRAM_BOT_TOKEN)
- ✅ Работать только с `DATABASE_URL`

---

## 🔍 Проверка:

После деплоя в логах должно быть:
```
Database initialized
Uvicorn running on http://0.0.0.0:XXXXX
```

И **НЕ должно быть** ошибок про `TELEGRAM_BOT_TOKEN`.


