# Настройка Nixpacks на Railway

## Проблема
Railway все еще ищет Dockerfile, даже когда Builder = Nixpacks.

## Решение: Явная конфигурация Nixpacks

Я создал файл `railway.json` с явным указанием использовать Nixpacks:

```json
{
  "build": {
    "builder": "NIXPACKS"
  }
}
```

## Что это делает:

1. **railway.json в корне проекта** - Railway будет использовать Nixpacks для всего проекта
2. **railway.json в client-server/** - Railway будет использовать Nixpacks для client-server

## После этого:

1. Railway автоматически перезапустит деплой
2. Должен использовать Nixpacks вместо поиска Dockerfile
3. Nixpacks автоматически определит Python проект

## Проверка в логах:

После деплоя в логах должно быть:
```
Using Nixpacks
Detected Python project
Installing dependencies...
```

## Если проблема сохраняется:

1. **Settings → Build → Builder:**
   - Убедитесь, что выбран **Nixpacks** (не Dockerfile)
   - Если есть опция выбора - выберите Nixpacks явно

2. **Проверьте railway.json:**
   - Файл должен быть в корне проекта
   - Или в `client-server/railway.json`

3. **Перезапустите деплой вручную:**
   - Deployments → выберите последний deployment
   - Нажмите три точки (⋮) → Redeploy

## Альтернатива: Создайте nixpacks.toml

Если railway.json не работает, создайте `nixpacks.toml`:

```toml
[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "python app.py"
```

Но обычно railway.json достаточно.

