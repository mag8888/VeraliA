# КРИТИЧНО: Проверка Builder в UI Railway

## Проблема сохраняется
Railway все еще показывает ошибку: `Dockerfile 'Dockerfile' does not exist`

Это означает, что **Builder в UI НЕ изменен на Railpack**.

## Как проверить текущий Builder:

1. **Settings** → нажмите **"Build"** в правом меню
2. Найдите раздел **"Builder"**
3. Посмотрите, что там написано:
   - Если написано **"Nixpacks"** → нужно изменить на Railpack
   - Если написано **"Dockerfile"** → нужно изменить на Railpack
   - Если написано **"Railpack"** → все правильно, но нужно проверить другие настройки

## Как изменить Builder на Railpack:

1. **Settings** → **Build**
2. Найдите раздел **"Builder"**
3. Должна быть карточка с текущим Builder
4. **Нажмите на эту карточку** - откроется выпадающее меню
5. В меню выберите **"Railpack"** (помечен как "Default")
6. **Сохраните изменения**

## Если Builder уже Railpack, но ошибка сохраняется:

### Проверьте Root Directory:

1. **Settings** → **Source**
2. Проверьте **Root Directory**:
   - Должно быть: `client-server` (без слэша `/`)
   - Если пусто или неправильно - введите `client-server` и сохраните

### Проверьте, нет ли Dockerfile:

1. Убедитесь, что в `client-server/` нет файла `Dockerfile`
2. Если есть `Dockerfile.backup` - это нормально
3. Railway не должен искать Dockerfile при использовании Railpack

### Перезапустите деплой:

1. **Deployments** → выберите последний deployment
2. Нажмите три точки (⋮) → **"Redeploy"**

## Визуальная проверка:

### Правильные настройки:
- ✅ Builder: **Railpack** (Default)
- ✅ Root Directory: `client-server`
- ✅ Custom Build Command: пусто
- ✅ Dockerfile НЕ существует в `client-server/`

### Неправильные настройки:
- ❌ Builder: Nixpacks или Dockerfile
- ❌ Root Directory: пусто или `/client-server`
- ❌ Dockerfile существует в `client-server/`

## Если ничего не помогает:

### Вариант 1: Пересоздайте сервис заново

Следуйте инструкции в `RAILWAY_RECREATE_GUIDE.md`

### Вариант 2: Свяжитесь с поддержкой Railway

Возможно, есть проблема с платформой или вашим аккаунтом.

## Контрольный список:

- [ ] Builder в UI = Railpack (проверено визуально)
- [ ] Root Directory = `client-server` (проверено)
- [ ] Dockerfile НЕ существует (проверено)
- [ ] Деплой перезапущен (выполнено)
- [ ] Проверены логи (все еще ошибка)

Если все пункты выполнены, но ошибка сохраняется - попробуйте пересоздать сервис.

