# Исправление: Parsing Server использует неправильный Dockerfile

## ❌ Проблема:

Parsing Server запускает код Client Server, который требует `TELEGRAM_BOT_TOKEN`.

Ошибка:
```
ValueError: TELEGRAM_BOT_TOKEN обязателен для работы бота
```

Это означает, что Parsing Server использует **неправильный Dockerfile** (Dockerfile вместо Dockerfile.parsing).

---

## 🔍 Причина:

В Railway для Parsing Server настроен **неправильный Dockerfile Path**:
- Используется `Dockerfile` (для Client Server) вместо `Dockerfile.parsing`
- Или Root Directory установлен неправильно

---

## ✅ Решение:

### Проверьте настройки Parsing Server в Railway:

1. **Откройте Parsing Server (VeraliA)** в Railway
2. Перейдите в **Settings → Build**
3. Проверьте настройки:

#### Правильные настройки:

```
Root Directory: (ПУСТО - корень проекта)
Dockerfile Path: Dockerfile.parsing
Builder: Dockerfile
```

#### Неправильные настройки (вызывают ошибку):

```
Root Directory: parsing-server  ❌
Dockerfile Path: Dockerfile  ❌
```

---

## 📋 Шаги для исправления:

### Шаг 1: Проверьте Root Directory

1. **Settings → Build**
2. Поле **"Root Directory"** должно быть **ПУСТЫМ**
3. Если там что-то есть (например, `parsing-server`) → **удалите** значение

### Шаг 2: Проверьте Dockerfile Path

1. В поле **"Dockerfile Path"** должно быть:
   ```
   Dockerfile.parsing
   ```
   
   **НЕ:**
   - `Dockerfile` ❌
   - `/Dockerfile.parsing` ❌ (без ведущего слэша)
   - `parsing-server/Dockerfile` ❌

### Шаг 3: Проверьте Builder

1. **Builder** должен быть: **Dockerfile**
2. **Сохраните** изменения

### Шаг 4: Redeploy

1. После сохранения Railway автоматически перезапустит сервис
2. Или нажмите **"Redeploy"** вручную

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
INFO: Database initialized
INFO: Started server process [1]
INFO: Application startup complete.
```

И **НЕ должно быть** ошибок про `TELEGRAM_BOT_TOKEN`.

---

## ⚠️ Важно:

- **Root Directory** должен быть **ПУСТЫМ** для Parsing Server
- **Dockerfile Path** должен быть **`Dockerfile.parsing`** (без `/` в начале)
- **Builder** должен быть **Dockerfile**

---

## 🎯 Итого:

1. ✅ **Root Directory**: ПУСТО
2. ✅ **Dockerfile Path**: `Dockerfile.parsing`
3. ✅ **Builder**: Dockerfile
4. ✅ **Save** и **Redeploy**

После этого Parsing Server должен работать правильно!


