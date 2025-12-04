# Полная инструкция по пересозданию сервера на Railway

## Подготовка к пересозданию

Все конфигурационные файлы уже созданы и готовы. Следуйте этой инструкции шаг за шагом.

## Шаг 1: Удаление старого сервиса

1. Откройте Railway.app
2. Выберите проект "VeraliA"
3. Найдите сервис "VeraliA" (Client Server)
4. **Settings** → прокрутите вниз
5. Найдите раздел **"Danger"** (красный)
6. Нажмите **"Delete Service"**
7. Подтвердите удаление

## Шаг 2: Создание базы данных PostgreSQL (если еще нет)

1. В проекте нажмите **"+ New"**
2. Выберите **"Database"** → **"Add PostgreSQL"**
3. Запомните имя сервиса (например: `Postgres`)
4. **Root Directory НЕ нужен** для базы данных

## Шаг 3: Создание Client Server

1. В проекте нажмите **"+ New"**
2. Выберите **"GitHub Repo"** → выберите `mag8888/VeraliA`
3. **СРАЗУ после создания** (до первого деплоя):

### 3.1. Настройка Source:
   - **Settings** → **Source** (или нажмите "Source" в правом меню)
   - **Root Directory**: введите `client-server` (без слэша `/`)
   - **Сохраните** (если есть кнопка)

### 3.2. Настройка Build:
   - **Settings** → **Build** (или нажмите "Build" в правом меню)
   - **Builder**: нажмите на текущий Builder → выберите **"Railpack"** (помечен как "Default")
   - **Custom Build Command**: оставьте пустым
   - **Сохраните**

### 3.3. Настройка Variables (после успешного деплоя):
   - **Settings** → **Variables**
   - Добавьте переменные:
     ```
     TELEGRAM_BOT_TOKEN=ваш_токен_бота
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     PARSING_SERVER_URL=https://ваш-parsing-server.up.railway.app
     MINIAPP_URL=https://ваш-client-server.up.railway.app/miniapp
     ```
   - **Важно:** Замените URL на реальные после генерации доменов

## Шаг 4: Создание Parsing Server

1. В проекте нажмите **"+ New"**
2. Выберите **"GitHub Repo"** → выберите `mag8888/VeraliA`
3. **СРАЗУ после создания**:

### 4.1. Настройка Source:
   - **Settings** → **Source**
   - **Root Directory**: введите `parsing-server` (без слэша `/`)
   - **Сохраните**

### 4.2. Настройка Build:
   - **Settings** → **Build**
   - **Builder**: выберите **"Railpack"**
   - **Custom Build Command**: оставьте пустым
   - **Сохраните**

### 4.3. Настройка Variables:
   - **Settings** → **Variables**
   - Добавьте:
     ```
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     ```

## Шаг 5: Генерация доменов

### Для Client Server:
1. **Settings** → **Networking**
2. Нажмите **"Generate Domain"**
3. Скопируйте полученный URL (например: `client-server-production.up.railway.app`)
4. Обновите переменную `MINIAPP_URL`: `https://client-server-production.up.railway.app/miniapp`

### Для Parsing Server:
1. **Settings** → **Networking**
2. Нажмите **"Generate Domain"** (опционально, если нужен публичный доступ)
3. Скопируйте URL
4. Обновите `PARSING_SERVER_URL` в Client Server

## Шаг 6: Проверка деплоя

### Проверьте логи:

**Client Server:**
- Должно быть: `Using Railpack`
- Должно быть: `Detected Python project`
- Должно быть: `Installing dependencies from requirements.txt`

**Parsing Server:**
- Аналогично Client Server

### Если видите ошибку:
- `Dockerfile 'Dockerfile' does not exist` → Builder не изменен на Railpack
- Проверьте настройки Build еще раз

## Контрольный список после пересоздания:

### Client Server:
- [ ] Root Directory = `client-server`
- [ ] Builder = Railpack
- [ ] Custom Build Command = пусто
- [ ] Variables настроены
- [ ] Домен сгенерирован
- [ ] Деплой успешен

### Parsing Server:
- [ ] Root Directory = `parsing-server`
- [ ] Builder = Railpack
- [ ] Custom Build Command = пусто
- [ ] Variables настроены
- [ ] Деплой успешен

### PostgreSQL:
- [ ] Сервис создан
- [ ] DATABASE_URL доступен

## Важные моменты:

1. **Root Directory** должен быть установлен СРАЗУ после создания сервиса
2. **Builder** должен быть изменен на Railpack СРАЗУ
3. **Variables** можно настроить после успешного деплоя
4. **Домены** генерируются после успешного деплоя

## Если что-то пошло не так:

1. Проверьте логи в Build Logs
2. Убедитесь, что Root Directory установлен правильно
3. Убедитесь, что Builder = Railpack
4. Перезапустите деплой вручную

## После успешного деплоя:

1. Проверьте работу сервисов
2. Настройте переменные окружения
3. Протестируйте Telegram бота
4. Проверьте мини-приложение

