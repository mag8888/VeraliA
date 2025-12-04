# СРОЧНОЕ ИСПРАВЛЕНИЕ для Parsing Server

## Проблема
Railway использует Dockerfile из корня проекта, который копирует `client-server/`, а не `parsing-server/`.

Ошибка в логах: `"/client-server/requirements.txt": not found`

## Решение: Используйте правильный Dockerfile

### Вариант 1: Использовать Dockerfile из parsing-server/ (РЕКОМЕНДУЕТСЯ)

1. **Settings → Source:**
   - **Root Directory**: `parsing-server` ✅ (уже установлено)

2. **Settings → Build:**
   - **Builder**: **Dockerfile** ✅ (уже установлено)
   - **Dockerfile Path**: измените на просто `Dockerfile` (без `/parsing-server/`)
   - **Сохраните**

3. **Перезапустите деплой**

### Вариант 2: Использовать Dockerfile.parsing из корня

Если Root Directory не работает:

1. **Settings → Source:**
   - **Root Directory**: оставьте **ПУСТЫМ** (корень проекта)

2. **Settings → Build:**
   - **Builder**: **Dockerfile**
   - **Dockerfile Path**: `Dockerfile.parsing`
   - **Сохраните**

3. **Перезапустите деплой**

## Почему ошибка?

В логах видно: `COPY client-server/requirements.txt .`

Это означает, что используется Dockerfile из корня проекта (который для Client Server), а не из `parsing-server/Dockerfile`.

## Правильная настройка:

### Для Parsing Server:
- **Root Directory**: `parsing-server`
- **Dockerfile Path**: `Dockerfile` (просто `Dockerfile`, не `/parsing-server/Dockerfile`)

Когда Root Directory = `parsing-server`:
- Railway использует `parsing-server/` как корень
- Dockerfile Path = `Dockerfile` → Railway ищет `parsing-server/Dockerfile`
- Dockerfile копирует файлы из текущей директории (которая уже `parsing-server/`)

## Проверка в логах:

После исправления должно быть:
```
Building from Dockerfile: parsing-server/Dockerfile
Step 1/8 : FROM python:3.11-slim
Step 2/8 : COPY requirements.txt .
```

А НЕ:
```
COPY client-server/requirements.txt .
```

## Действия сейчас:

1. **Settings → Build → Dockerfile Path**: измените `/parsing-server/Dockerfile` на просто `Dockerfile`
2. **Сохраните**
3. **Перезапустите деплой**



