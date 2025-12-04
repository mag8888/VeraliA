# Правильная настройка Railway - ФИНАЛЬНАЯ ИНСТРУКЦИЯ

## Проблема: Dockerfile Path указан неправильно

Вы указали Dockerfile Path: `/client-server/Dockerfile`

Это неправильно! Нужно использовать Root Directory.

## ✅ ПРАВИЛЬНАЯ настройка для Client Server:

### Шаг 1: Settings → Source
- **Root Directory**: `client-server` (без слэша `/`, без пробелов)
- **Сохраните**

### Шаг 2: Settings → Build
- **Builder**: `Dockerfile` (выбрано правильно ✅)
- **Dockerfile Path**: `Dockerfile` (просто `Dockerfile`, БЕЗ пути `/client-server/`)
- **Custom Build Command**: пусто
- **Сохраните**

### Почему так:
- Когда Root Directory = `client-server`, Railway использует `client-server/` как корень
- Dockerfile Path должен быть относительным к Root Directory
- Поэтому просто `Dockerfile`, а не `/client-server/Dockerfile`

## ✅ ПРАВИЛЬНАЯ настройка для Parsing Server:

### Шаг 1: Settings → Source
- **Root Directory**: `parsing-server` (без слэша)
- **Сохраните**

### Шаг 2: Settings → Build
- **Builder**: `Dockerfile`
- **Dockerfile Path**: `Dockerfile` (просто `Dockerfile`)
- **Custom Build Command**: пусто
- **Сохраните**

## Что происходит:

1. Root Directory = `client-server`
   → Railway переходит в `client-server/` директорию

2. Dockerfile Path = `Dockerfile`
   → Railway ищет `Dockerfile` в `client-server/Dockerfile`
   → Находит! ✅

3. Сборка начинается из `client-server/`
   → Команды `COPY . .` копируют файлы из `client-server/`
   → Все работает! ✅

## ❌ НЕПРАВИЛЬНО:

- Root Directory: пусто
- Dockerfile Path: `/client-server/Dockerfile`
→ Railway не понимает, откуда брать файлы

## ✅ ПРАВИЛЬНО:

- Root Directory: `client-server`
- Dockerfile Path: `Dockerfile`
→ Railway все понимает и собирает правильно

## Действия сейчас:

1. **Settings → Source → Root Directory**: `client-server`
2. **Settings → Build → Dockerfile Path**: измените на `Dockerfile` (уберите `/client-server/`)
3. **Сохраните все**
4. Railway автоматически перезапустит деплой

## Проверка в логах:

После правильной настройки в логах должно быть:
```
Root directory: client-server
Dockerfile path: Dockerfile
Building from Dockerfile: client-server/Dockerfile
```

