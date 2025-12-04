# Финальный чеклист для успешного деплоя на Railway

## ✅ Проверка настроек Client Server

### 1. Settings → Source
- [ ] **Root Directory**: `client-server` (без слэша `/`, без пробелов)
- [ ] **Source Repo**: `mag8888/VeraliA`
- [ ] **Branch**: `main`
- [ ] **Все сохранено**

### 2. Settings → Build
- [x] **Builder**: `Dockerfile` ✅ (уже правильно)
- [x] **Dockerfile Path**: `Dockerfile` ✅ (уже правильно)
- [ ] **Custom Build Command**: пусто (проверьте)
- [ ] **Все сохранено**

### 3. Settings → Deploy
- [ ] **Custom Start Command**: пусто или `python app.py`
- [ ] **Все сохранено**

### 4. Settings → Variables
- [ ] `TELEGRAM_BOT_TOKEN` = ваш токен
- [ ] `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
- [ ] `PARSING_SERVER_URL` = URL вашего parsing server
- [ ] `MINIAPP_URL` = URL вашего client server + `/miniapp`

## ✅ Проверка настроек Parsing Server

### 1. Settings → Source
- [ ] **Root Directory**: `parsing-server` (без слэша)
- [ ] **Все сохранено**

### 2. Settings → Build
- [ ] **Builder**: `Dockerfile`
- [ ] **Dockerfile Path**: `Dockerfile`
- [ ] **Custom Build Command**: пусто
- [ ] **Все сохранено**

### 3. Settings → Variables
- [ ] `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`

## 🔍 Проверка после настройки

### В логах должно быть:
```
Root directory: client-server
Dockerfile path: Dockerfile
Building from Dockerfile: client-server/Dockerfile
```

### Если видите:
- `Root directory: /` → Root Directory не установлен!
- `Dockerfile path: /client-server/Dockerfile` → Неправильно! Должно быть просто `Dockerfile`

## 🚀 После успешной сборки

1. Проверьте Deploy Logs - приложение должно запуститься
2. Проверьте статус сервиса - должен быть "Running"
3. Настройте переменные окружения
4. Сгенерируйте публичный домен для мини-приложения

## ❌ Если ошибка сохраняется

1. Проверьте, что Root Directory установлен и сохранен
2. Убедитесь, что Dockerfile Path = `Dockerfile` (не `/client-server/Dockerfile`)
3. Перезапустите деплой вручную
4. Проверьте логи - должны показать правильный Root Directory

