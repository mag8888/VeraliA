# Финальная проверка настроек Parsing Server

## Текущие настройки (правильно):

✅ **Builder**: Dockerfile
✅ **Dockerfile Path**: `Dockerfile` (правильно!)

## Что еще нужно проверить:

### 1. Root Directory

1. **Settings → Source** (или нажмите "Source" в правом меню)
2. Проверьте поле **"Root Directory"**:
   - Должно быть: `parsing-server` (без слэша `/`)
   - Если пусто или неправильно - введите `parsing-server` и сохраните

### 2. Перезапустите деплой

1. Перейдите на **Deployments**
2. Выберите последний failed deployment
3. Нажмите три точки (⋮) → **"Redeploy"**

## Правильная конфигурация:

### Settings → Source:
- **Root Directory**: `parsing-server` ✅

### Settings → Build:
- **Builder**: Dockerfile ✅
- **Dockerfile Path**: `Dockerfile` ✅ (уже правильно!)

### Settings → Variables:
- **DATABASE_URL**: `${{Postgres.DATABASE_URL}}` ✅

## Как это работает:

1. **Root Directory = `parsing-server`** → Railway использует `parsing-server/` как корень
2. **Dockerfile Path = `Dockerfile`** → Railway ищет `parsing-server/Dockerfile` → находит ✅
3. Dockerfile копирует файлы из текущей директории (которая уже `parsing-server/`)

## Проверка в логах после перезапуска:

Должно быть:
```
Root directory: parsing-server
Dockerfile path: Dockerfile
Building from Dockerfile: parsing-server/Dockerfile
Step 1/8 : FROM python:3.11-slim
Step 2/8 : COPY requirements.txt .
```

А НЕ:
```
COPY client-server/requirements.txt .
```

## Если ошибка сохраняется:

1. Проверьте, что Root Directory = `parsing-server` (без слэша)
2. Убедитесь, что Dockerfile Path = `Dockerfile` (без пути)
3. Проверьте, что `parsing-server/Dockerfile` существует в GitHub
4. Перезапустите деплой вручную

## Контрольный список:

- [ ] Root Directory = `parsing-server` (проверено)
- [ ] Builder = Dockerfile ✅
- [ ] Dockerfile Path = `Dockerfile` ✅ (уже правильно!)
- [ ] DATABASE_URL установлен ✅
- [ ] Деплой перезапущен


