# Финальные шаги для успешного деплоя на Railway

## Текущая ситуация
Все конфигурационные файлы созданы, но Railway все еще ищет Dockerfile.

## КРИТИЧЕСКИ ВАЖНО: Измените Builder в UI Railway

### Пошаговая инструкция:

1. **Откройте Railway.app** в браузере
2. **Выберите ваш проект** "VeraliA"
3. **Выберите сервис** "VeraliA" (Client Server)
4. **Перейдите в Settings**
5. **Нажмите "Build"** в правом меню
6. **Найдите раздел "Builder"**
7. **Нажмите на текущий Builder** (вероятно "Nixpacks")
8. **В выпадающем меню выберите "Railpack"** (помечен как "Default")
9. **Сохраните изменения**

## После изменения Builder:

1. **Перейдите на Deployments**
2. **Нажмите три точки (⋮)** у последнего deployment
3. **Выберите "Redeploy"**
4. **Проверьте логи**

## Что должно быть в логах:

✅ **Правильно (с Railpack):**
```
Using Railpack
Detected Python project
Installing dependencies from requirements.txt
Starting application: python app.py
```

❌ **Неправильно (все еще ищет Dockerfile):**
```
Dockerfile 'Dockerfile' does not exist
```

## Если Builder не меняется:

### Пересоздайте сервис:

1. **Settings** → **Danger** → **Delete Service**
2. **Создайте новый сервис** из GitHub репозитория
3. **Сразу после создания:**
   - **Settings** → **Source** → **Root Directory**: `client-server`
   - **Settings** → **Build** → **Builder**: выберите **Railpack**
   - **Сохраните**
4. Дождитесь автоматического деплоя

## Контрольный список:

- [ ] Builder в UI изменен на Railpack
- [ ] Root Directory = `client-server`
- [ ] Custom Build Command = пусто
- [ ] Деплой перезапущен
- [ ] Проверены логи (должно быть "Using Railpack")

## После успешного деплоя:

1. **Настройте переменные окружения:**
   - `TELEGRAM_BOT_TOKEN`
   - `DATABASE_URL`
   - `PARSING_SERVER_URL`
   - `MINIAPP_URL`

2. **Сгенерируйте публичный домен** для мини-приложения

3. **Проверьте работу сервиса**

## Помощь

Если проблема сохраняется после изменения Builder на Railpack:
- Проверьте логи детально
- Убедитесь, что Root Directory установлен правильно
- Попробуйте пересоздать сервис

