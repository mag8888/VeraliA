# Пошаговая настройка Variables в Railway

## Для Client Server

### Шаг 1: Откройте Variables

1. Выберите сервис **"VeraliA"** (Client Server)
2. Перейдите на вкладку **"Variables"** (или Settings → Variables)

### Шаг 2: Добавьте переменные

Нажмите **"+ New Variable"** и добавьте каждую переменную:

#### 1. TELEGRAM_BOT_TOKEN (ОБЯЗАТЕЛЬНО)

- **Key**: `TELEGRAM_BOT_TOKEN`
- **Value**: ваш токен от [@BotFather](https://t.me/BotFather)
  - Откройте Telegram → [@BotFather](https://t.me/BotFather)
  - Отправьте `/newbot` или используйте существующего бота
  - Скопируйте токен (формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
  - Вставьте в поле Value
- **Нажмите "Add"**

#### 2. DATABASE_URL

- **Key**: `DATABASE_URL`
- **Value**: `${{Postgres.DATABASE_URL}}`
  - Замените `Postgres` на имя вашего PostgreSQL сервиса
  - Если сервис называется `Postgres` - используйте как есть
  - Если другое имя - замените на правильное
- **Нажмите "Add"**

**Как узнать имя PostgreSQL сервиса:**
- Посмотрите в списке сервисов проекта
- Имя будет написано на карточке PostgreSQL

#### 3. PARSING_SERVER_URL

- **Key**: `PARSING_SERVER_URL`
- **Value**: 
  - Если Parsing Server еще не создан: `http://localhost:8001` (временно)
  - Если Parsing Server создан: `https://ваш-parsing-server.up.railway.app`
- **Нажмите "Add"**

**Как получить URL Parsing Server:**
1. Выберите сервис Parsing Server
2. Settings → Networking → Generate Domain
3. Скопируйте URL
4. Используйте в `PARSING_SERVER_URL`

#### 4. MINIAPP_URL

- **Key**: `MINIAPP_URL`
- **Value**: `https://ваш-client-server.up.railway.app/miniapp`
  - Замените на реальный URL вашего Client Server
- **Нажмите "Add"**

**Как получить URL Client Server:**
1. Settings → Networking → Generate Domain
2. Скопируйте URL (например: `verali-client-production.up.railway.app`)
3. Добавьте `/miniapp` в конец
4. Используйте: `https://verali-client-production.up.railway.app/miniapp`

#### 5. PORT (НЕ НУЖНО!)

- **НЕ добавляйте PORT вручную!**
- Railway автоматически устанавливает переменную `PORT`
- Код автоматически прочитает ее

## Для Parsing Server

### Шаг 1: Откройте Variables

1. Выберите сервис **"pars_VeraliA"** (Parsing Server)
2. Перейдите на вкладку **"Variables"**

### Шаг 2: Добавьте переменную

#### DATABASE_URL

- **Key**: `DATABASE_URL`
- **Value**: `${{Postgres.DATABASE_URL}}`
  - Замените `Postgres` на имя вашего PostgreSQL сервиса
- **Нажмите "Add"**

## Использование переменных Railway (${{...}})

Railway позволяет ссылаться на переменные других сервисов:

### Формат:
```
${{ServiceName.VARIABLE_NAME}}
```

### Примеры:

1. **DATABASE_URL из PostgreSQL:**
   ```
   ${{Postgres.DATABASE_URL}}
   ```
   - `Postgres` - имя сервиса PostgreSQL
   - `DATABASE_URL` - переменная, которую Railway создает автоматически

2. **Если PostgreSQL называется по-другому:**
   ```
   ${{PostgreSQL.DATABASE_URL}}
   ```
   или
   ```
   ${{db.DATABASE_URL}}
   ```
   - Используйте реальное имя вашего сервиса

### Как узнать имя сервиса:

1. Посмотрите в списке сервисов проекта
2. Имя написано на карточке сервиса
3. Используйте это имя в `${{...}}`

## Проверка переменных

### После добавления переменных:

1. Railway автоматически перезапустит сервис
2. Проверьте логи - не должно быть ошибок про отсутствующие переменные
3. Для Client Server - проверьте, что бот запустился

### Если переменная не работает:

1. Проверьте имя сервиса в `${{...}}`
2. Убедитесь, что PostgreSQL сервис запущен
3. Проверьте, что нет опечаток в имени переменной

## Минимальный набор для запуска:

### Client Server (минимум):
- ✅ `TELEGRAM_BOT_TOKEN` - обязательно
- ✅ `DATABASE_URL` - обязательно (если используете базу)
- ⚠️ `PARSING_SERVER_URL` - можно добавить позже
- ⚠️ `MINIAPP_URL` - можно добавить после генерации домена

### Parsing Server (минимум):
- ✅ `DATABASE_URL` - обязательно

## Пример полной настройки:

### Client Server Variables:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
DATABASE_URL=${{Postgres.DATABASE_URL}}
PARSING_SERVER_URL=https://parsing-server-production.up.railway.app
MINIAPP_URL=https://client-server-production.up.railway.app/miniapp
```

### Parsing Server Variables:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

## Важно:

- Не используйте кавычки в значениях переменных
- Не добавляйте пробелы в начале или конце значения
- `${{...}}` работает только для переменных Railway (DATABASE_URL, RAILWAY_PUBLIC_DOMAIN и т.д.)

