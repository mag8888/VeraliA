# Решение проблемы с Dockerfile

## Проблема была:
Railway использовал Dockerfile из корня проекта, который пытался копировать `client-server/requirements.txt`, но это не работало, потому что Root Directory уже установлен как `client-server`.

## Решение:
Удален Dockerfile из корня проекта. Теперь Railway будет использовать правильный Dockerfile из `client-server/Dockerfile`, который:
- Копирует `requirements.txt` напрямую (без пути `client-server/`)
- Копирует все файлы из текущей директории (которая уже `client-server/`)
- Работает правильно с Root Directory = `client-server`

## Правильная структура:

```
VeraliA/
├── client-server/
│   ├── Dockerfile  ← используется этот
│   ├── app.py
│   └── requirements.txt
└── parsing-server/
    ├── Dockerfile
    └── ...
```

## Настройки Railway:

### Client Server:
- **Root Directory**: `client-server`
- **Dockerfile Path**: `Dockerfile`
- Railway автоматически найдет `client-server/Dockerfile`

### Parsing Server:
- **Root Directory**: `parsing-server`
- **Dockerfile Path**: `Dockerfile`
- Railway автоматически найдет `parsing-server/Dockerfile`

## После удаления Dockerfile из корня:

Railway автоматически перезапустит деплой и должен использовать правильный Dockerfile из `client-server/`, который будет работать корректно.

