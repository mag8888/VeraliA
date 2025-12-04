# Настройка Parsing Server на Railway

## Текущая ситуация
Parsing Server не может собраться. Root Directory установлен как `parsing-server`, но есть ошибка при сборке.

## Решение 1: Использовать Dockerfile из parsing-server/ (рекомендуется)

### Настройки Railway для Parsing Server:

1. **Settings → Source:**
   - **Root Directory**: `parsing-server` ✅ (уже установлено правильно)
   - **Сохраните**

2. **Settings → Build:**
   - **Builder**: выберите **"Dockerfile"** (не Railpack, не Nixpacks)
   - **Dockerfile Path**: `Dockerfile` (или оставьте пустым)
   - **Custom Build Command**: оставьте пустым
   - **Сохраните**

3. **Settings → Variables:**
   - **DATABASE_URL**: `${{Postgres.DATABASE_URL}}` ✅ (уже установлено)
   - **PORT**: не нужно (Railway автоматически устанавливает)

4. **Перезапустите деплой:**
   - Deployments → выберите последний failed deployment
   - Нажмите три точки (⋮) → **"Redeploy"**

## Решение 2: Использовать Dockerfile в корне (если Решение 1 не работает)

Если Root Directory не работает:

1. **Settings → Source:**
   - **Root Directory**: оставьте **ПУСТЫМ** (корень проекта)

2. **Settings → Build:**
   - **Builder**: **"Dockerfile"**
   - **Dockerfile Path**: `Dockerfile.parsing` (используйте созданный файл)

3. Перезапустите деплой

## Проверка в логах:

После правильной настройки в логах должно быть:
```
Building from Dockerfile: parsing-server/Dockerfile
Step 1/8 : FROM python:3.11-slim
Step 2/8 : RUN apt-get update...
...
```

## Если ошибка "failed to calculate checksum":

Это может означать проблему с копированием файлов. Проверьте:

1. Что все файлы в `parsing-server/` существуют в GitHub
2. Что `parsing-server/Dockerfile` существует
3. Что `parsing-server/requirements.txt` существует

## Контрольный список для Parsing Server:

- [ ] Root Directory = `parsing-server` (или пусто для Dockerfile в корне)
- [ ] Builder = Dockerfile
- [ ] Dockerfile Path = `Dockerfile` (или `Dockerfile.parsing` для корня)
- [ ] DATABASE_URL установлен
- [ ] Деплой перезапущен

## После успешного деплоя Parsing Server:

1. Сгенерируйте домен для Parsing Server (если нужен публичный доступ)
2. Обновите `PARSING_SERVER_URL` в Client Server Variables

