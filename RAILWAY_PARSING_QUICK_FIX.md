# Быстрое решение для Parsing Server

## Текущая ситуация
- ✅ Root Directory = `parsing-server` (правильно)
- ✅ DATABASE_URL установлен в Variables
- ❌ Деплой падает при сборке

## Решение: Настройте Builder

### Шаг 1: Откройте настройки Build

1. Выберите сервис **"pars_VeraliA"** (Parsing Server)
2. **Settings** → нажмите **"Build"** в правом меню
3. Найдите раздел **"Builder"**

### Шаг 2: Измените Builder на Dockerfile

1. В разделе **"Builder"** должна быть карточка
2. **Нажмите на карточку** - откроется выпадающее меню
3. Выберите **"Dockerfile"** (не Railpack, не Nixpacks)
4. **Сохраните изменения**

### Шаг 3: Проверьте Dockerfile Path

1. В разделе Build найдите **"Dockerfile Path"**
2. Должно быть: `Dockerfile` (или оставьте пустым)
3. **Сохраните**

### Шаг 4: Перезапустите деплой

1. Перейдите на **Deployments**
2. Выберите последний failed deployment
3. Нажмите три точки (⋮) → **"Redeploy"**

## Проверка в логах:

После правильной настройки должно быть:
```
Building from Dockerfile: parsing-server/Dockerfile
Step 1/8 : FROM python:3.11-slim
Step 2/8 : RUN apt-get update...
```

## Если Builder уже Dockerfile, но ошибка сохраняется:

### Проверьте Root Directory еще раз:

1. **Settings → Source**
2. Проверьте **Root Directory**:
   - Должно быть: `parsing-server` (без слэша `/`)
   - Если есть слэш `/parsing-server` - уберите его
   - **Сохраните**

### Проверьте, что Dockerfile существует:

1. Убедитесь, что в GitHub есть файл `parsing-server/Dockerfile`
2. Проверьте: https://github.com/mag8888/VeraliA/tree/main/parsing-server/Dockerfile

## Контрольный список:

- [ ] Builder = Dockerfile (проверено визуально)
- [ ] Root Directory = `parsing-server` (без слэша)
- [ ] Dockerfile Path = `Dockerfile` (или пусто)
- [ ] DATABASE_URL установлен ✅
- [ ] Деплой перезапущен

## После успешного деплоя:

1. Parsing Server должен запуститься на порту 8001
2. Обновите `PARSING_SERVER_URL` в Client Server Variables
3. Протестируйте связь между сервисами

