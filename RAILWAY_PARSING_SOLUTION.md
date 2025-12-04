# Решение проблемы Parsing Server

## Проблема
В логах видно: `COPY client-server/requirements.txt .`

Это означает, что Railway использует Dockerfile из корня проекта (для Client Server), а не из `parsing-server/Dockerfile`.

## Решение: Исправьте Dockerfile Path

### Шаг 1: Проверьте настройки

1. Выберите сервис **"pars_VeraliA"** (Parsing Server)
2. **Settings → Source:**
   - **Root Directory**: должно быть `parsing-server` (без слэша)

3. **Settings → Build:**
   - **Builder**: должен быть **"Dockerfile"**
   - **Dockerfile Path**: должно быть просто `Dockerfile` (НЕ `/parsing-server/Dockerfile`)

### Шаг 2: Исправьте Dockerfile Path

1. **Settings → Build → Dockerfile Path**
2. Если там написано `/parsing-server/Dockerfile`:
   - Удалите `/parsing-server/`
   - Оставьте только: `Dockerfile`
3. **Сохраните изменения**

### Шаг 3: Перезапустите деплой

1. **Deployments** → выберите последний failed deployment
2. Нажмите три точки (⋮) → **"Redeploy"**

## Как это работает:

1. **Root Directory = `parsing-server`** → Railway использует `parsing-server/` как корень
2. **Dockerfile Path = `Dockerfile`** → Railway ищет `parsing-server/Dockerfile`
3. Dockerfile копирует файлы из текущей директории (которая уже `parsing-server/`)

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

## Если проблема сохраняется:

### Альтернатива: Используйте Dockerfile.parsing из корня

1. **Settings → Source:**
   - **Root Directory**: оставьте **ПУСТЫМ** (корень проекта)

2. **Settings → Build:**
   - **Dockerfile Path**: `Dockerfile.parsing`

3. Перезапустите деплой

## Контрольный список:

- [ ] Root Directory = `parsing-server` (без слэша)
- [ ] Dockerfile Path = `Dockerfile` (без `/parsing-server/`)
- [ ] Builder = Dockerfile
- [ ] Деплой перезапущен



