# Настройка Railpack на Railway

## Что такое Railpack?

Railpack - это новый builder от Railway, который заменяет Nixpacks (Deprecated). Он автоматически определяет тип проекта и собирает его.

## Преимущества Railpack:

- ✅ Новый и поддерживаемый (Nixpacks Deprecated)
- ✅ Автоматическое определение Python проекта
- ✅ Быстрее чем Nixpacks
- ✅ Не требует Dockerfile
- ✅ Простая настройка

## Настройка в UI Railway:

### Шаг 1: Измените Builder на Railpack

1. **Settings** → нажмите **"Build"** в правом меню
2. Найдите раздел **"Builder"**
3. Откройте выпадающее меню
4. **Выберите "Railpack"** (помечен как "Default")
5. **Сохраните изменения**

### Шаг 2: Проверьте настройки

После выбора Railpack:
- **Root Directory**: `client-server` (должно быть установлено)
- **Custom Build Command**: пусто
- **Dockerfile Path**: не нужно (Railpack не использует Dockerfile)

### Шаг 3: Перезапустите деплой

1. Перейдите на **Deployments**
2. Выберите последний deployment
3. Нажмите три точки (⋮) → **"Redeploy"**

## Как работает Railpack:

1. **Автоматическое определение:**
   - Railpack видит `requirements.txt` в `client-server/`
   - Определяет, что это Python проект
   - Автоматически настраивает окружение

2. **Установка зависимостей:**
   - Читает `requirements.txt`
   - Устанавливает все зависимости через pip

3. **Запуск приложения:**
   - Запускает `python app.py` (из railpack.toml или по умолчанию)

## Конфигурационные файлы:

Я создал:
- `railway.json` - указывает использовать Railpack
- `railpack.toml` - конфигурация для Railpack (опционально)

Railpack может работать и без этих файлов, автоматически определяя проект.

## Проверка в логах:

После деплоя с Railpack в логах должно быть:
```
Using Railpack
Detected Python project
Installing dependencies from requirements.txt
Starting application: python app.py
```

## Если проблема сохраняется:

1. Убедитесь, что Builder изменен на Railpack в UI
2. Проверьте, что Root Directory = `client-server`
3. Перезапустите деплой вручную
4. Проверьте логи - должны показать использование Railpack

## Отличия от Nixpacks:

- Railpack - новый, поддерживаемый
- Nixpacks - Deprecated (устаревший)
- Railpack быстрее и надежнее
- Railpack лучше определяет проекты

