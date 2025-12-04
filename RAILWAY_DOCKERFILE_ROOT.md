# Настройка Railway с Dockerfile в корне проекта

## Решение: Dockerfile в корне проекта

Этот подход использует Dockerfile в корне проекта, который копирует файлы из `client-server/`.

## Настройка Railway

### Шаг 1: Удалите старый сервис (если есть)

1. Settings → Danger → Delete Service

### Шаг 2: Создайте новый сервис

1. + New → GitHub Repo → выберите `mag8888/VeraliA`

### Шаг 3: Настройки (СРАЗУ после создания)

#### Settings → Source:
- **Root Directory**: оставьте **ПУСТЫМ** (корень проекта)
- **Сохраните**

#### Settings → Build:
- **Builder**: выберите **"Dockerfile"** (не Railpack, не Nixpacks)
- **Dockerfile Path**: `Dockerfile` (или оставьте пустым)
- **Custom Build Command**: оставьте пустым
- **Сохраните**

### Шаг 4: Дождитесь деплоя

Railway автоматически:
1. Найдет `Dockerfile` в корне проекта
2. Соберет образ по Dockerfile
3. Запустит приложение

## Как работает Dockerfile в корне:

```dockerfile
# Копирует requirements.txt из client-server/
COPY client-server/requirements.txt .

# Устанавливает зависимости
RUN pip install -r requirements.txt

# Копирует весь client-server/
COPY client-server/ .

# Запускает приложение
CMD ["python", "app.py"]
```

## Проверка в логах:

После деплоя в логах должно быть:
```
Building from Dockerfile: Dockerfile
Step 1/6 : FROM python:3.11-slim
Step 2/6 : WORKDIR /app
Step 3/6 : COPY client-server/requirements.txt .
...
```

## Преимущества этого подхода:

- ✅ Не нужно настраивать Root Directory
- ✅ Dockerfile в корне - стандартный подход
- ✅ Полный контроль над сборкой
- ✅ Работает надежно

## Если ошибка сохраняется:

1. Проверьте, что Builder = Dockerfile (не Railpack)
2. Проверьте, что Root Directory ПУСТОЙ
3. Проверьте, что Dockerfile существует в корне проекта
4. Перезапустите деплой

## Для Parsing Server:

Создайте аналогичный Dockerfile в корне для parsing-server или используйте тот же подход с Root Directory = `parsing-server` и Dockerfile в `parsing-server/Dockerfile`.

