# Правильная настройка Root Directory на Railway

## Проблема: "context canceled" при сборке

Ошибка возникает, когда Dockerfile в корне пытается копировать файлы из подпапок, но контекст сборки неправильный.

## Решение: Используйте Root Directory правильно

### Для Client Server:

1. **Settings** → **Source** → **Root Directory**: `client-server`
2. **Settings** → **Build** → **Custom Build Command**: пусто
3. **Settings** → **Build** → **Dockerfile Path**: `Dockerfile` (или пусто)
4. Railway будет использовать `client-server/Dockerfile`

### Для Parsing Server:

1. **Settings** → **Source** → **Root Directory**: `parsing-server`
2. **Settings** → **Build** → **Custom Build Command**: пусто
3. **Settings** → **Build** → **Dockerfile Path**: `Dockerfile` (или пусто)
4. Railway будет использовать `parsing-server/Dockerfile`

## Почему это важно:

Когда Root Directory = `client-server`:
- Railway использует `client-server/` как корень сборки
- Dockerfile в `client-server/Dockerfile` работает правильно
- Команды `COPY . .` копируют файлы из `client-server/`

Когда Root Directory пустой (корень проекта):
- Railway использует весь репозиторий как контекст
- Dockerfile должен копировать из подпапок: `COPY client-server/ .`
- Это может вызывать проблемы с контекстом

## Рекомендация:

**Всегда используйте Root Directory!**

Для Client Server: `client-server`
Для Parsing Server: `parsing-server`

## Если Root Directory не работает:

1. Убедитесь, что значение сохранено (нет слэша `/` в начале)
2. Перезапустите деплой после установки Root Directory
3. Проверьте логи - должно быть "Root directory: client-server"

