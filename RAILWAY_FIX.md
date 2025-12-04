# Решение проблемы "Dockerfile does not exist" на Railway

## Для Parsing Server (та же проблема)

Если у Parsing Server та же ошибка, выполните те же шаги, но для Root Directory укажите: `parsing-server`

## Если Root Directory указан, но ошибка остается

### Шаг 1: Проверьте, что Root Directory сохранен

1. Откройте **Settings** сервиса
2. Проверьте поле **Root Directory** - должно быть `client-server` (без слэша)
3. **Нажмите "Save" или "Update"** если есть такая кнопка
4. Убедитесь, что изменения сохранены

### Шаг 2: Перезапустите деплой вручную

1. Перейдите на вкладку **Deployments**
2. Найдите последний failed deployment
3. Нажмите на три точки (⋮) рядом с deployment
4. Выберите **"Redeploy"** или **"Deploy"**
5. Или просто сделайте новый коммит в GitHub - Railway автоматически перезапустит деплой

### Шаг 3: Проверьте логи

1. Нажмите **"View logs"** на failed deployment
2. Проверьте, что Railway видит правильный Root Directory
3. Убедитесь, что Dockerfile найден

### Шаг 4: Альтернативное решение - создайте новый сервис

Если проблема не решается:

1. **Удалите текущий сервис** (Settings → Danger → Delete Service)
2. Создайте новый сервис заново
3. **Сразу после создания** установите Root Directory: `client-server`
4. Сохраните и дождитесь деплоя

### Шаг 5: Проверьте структуру репозитория

Убедитесь, что в GitHub репозитории структура правильная:

```
VeraliA/
├── client-server/
│   ├── Dockerfile  ← должен быть здесь
│   ├── app.py
│   └── requirements.txt
└── parsing-server/
    ├── Dockerfile
    └── ...
```

### Шаг 6: Проверьте настройки Build

1. В Settings найдите раздел **"Build"**
2. Убедитесь, что:
   - **Build Command** - пусто (используется Dockerfile)
   - **Dockerfile Path** - `Dockerfile` (или оставьте пустым)
   - **Root Directory** - `client-server`

## Быстрое решение

1. **Settings** → **Root Directory**: `client-server` (без слэша)
2. **Сохраните**
3. **Deployments** → нажмите **"Redeploy"** или сделайте новый коммит
4. Проверьте логи

## Если ничего не помогает

Попробуйте создать файл `railway.toml` в корне `client-server/`:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "python app.py"
```

Или используйте Nixpacks вместо Dockerfile (Railway автоматически определит Python проект).

