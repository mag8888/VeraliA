# Решение проблемы "Dockerfile does not exist" на Railway

## Если Root Directory установлен правильно, но ошибка остается

### Проблема
Railway не находит Dockerfile даже после установки Root Directory.

### Решения

## Решение 1: Проверьте настройки Build в Railway

1. Откройте **Settings** → раздел **"Build"**
2. Убедитесь, что:
   - **Build Command** - **ПУСТО** (оставьте пустым)
   - **Dockerfile Path** - `Dockerfile` (или оставьте пустым, Railway должен найти автоматически)
   - **Root Directory** - `client-server` (для Client Server) или `parsing-server` (для Parsing Server)

## Решение 2: Явно укажите Dockerfile Path

1. В Settings → **Build**
2. В поле **"Dockerfile Path"** укажите: `Dockerfile`
3. Сохраните изменения
4. Перезапустите деплой

## Решение 3: Проверьте, что Dockerfile в правильном формате

Убедитесь, что Dockerfile:
- Начинается с `FROM ...`
- Не имеет скрытых символов
- Имеет правильную кодировку (UTF-8)

Проверьте локально:
```bash
cd client-server
head -1 Dockerfile  # Должно показать: FROM python:3.11-slim
```

## Решение 4: Пересоздайте сервис с нуля

Если ничего не помогает:

1. **Удалите сервис полностью:**
   - Settings → **Danger** → **Delete Service**

2. **Создайте новый сервис:**
   - + New → GitHub Repo → выберите `VeraliA`
   
3. **Сразу после создания:**
   - Settings → **Root Directory**: `client-server` (или `parsing-server`)
   - Settings → **Build** → **Dockerfile Path**: `Dockerfile`
   - Сохраните

4. **Дождитесь автоматического деплоя**

## Решение 5: Используйте Nixpacks (альтернатива)

Если Dockerfile не работает, Railway может автоматически определить проект:

1. **Удалите Root Directory** (оставьте пустым)
2. Railway автоматически определит Python проект
3. Но лучше использовать Dockerfile для полного контроля

## Решение 6: Проверьте GitHub репозиторий

Убедитесь, что в GitHub:
1. Dockerfile действительно существует в `client-server/Dockerfile`
2. Файл не пустой
3. Последний коммит загружен в GitHub

Проверьте на GitHub:
- https://github.com/mag8888/VeraliA/tree/main/client-server/Dockerfile
- https://github.com/mag8888/VeraliA/tree/main/parsing-server/Dockerfile

## Решение 7: Используйте railway.toml явно

Файл `railway.toml` уже существует в каждой директории. Railway должен его подхватить автоматически.

Если не работает, попробуйте создать `.railway/railway.toml` в корне проекта:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "client-server/Dockerfile"  # для client-server
```

Но лучше использовать Root Directory.

## Диагностика

### Проверьте логи Railway

1. Нажмите **"View logs"** на failed deployment
2. Ищите строки:
   - "Building from Dockerfile..."
   - "Dockerfile path: ..."
   - "Root directory: ..."
3. Проверьте, что Railway видит правильный путь

### Проверьте структуру в GitHub

Убедитесь, что структура такая:
```
VeraliA/
├── client-server/
│   ├── Dockerfile  ← должен быть здесь
│   ├── app.py
│   └── requirements.txt
└── parsing-server/
    ├── Dockerfile  ← должен быть здесь
    └── ...
```

## Быстрый чеклист

- [ ] Root Directory установлен: `client-server` (без слэша)
- [ ] Dockerfile существует в `client-server/Dockerfile`
- [ ] Build Command - пусто
- [ ] Dockerfile Path - `Dockerfile` (или пусто)
- [ ] Изменения сохранены
- [ ] Деплой перезапущен
- [ ] Проверены логи Railway

## Если все еще не работает

Создайте issue на GitHub или попробуйте:
1. Использовать другой builder (Nixpacks)
2. Создать сервис заново
3. Проверить, нет ли проблем с доступом Railway к репозиторию

