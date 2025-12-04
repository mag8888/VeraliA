# КРИТИЧНО: Railway все еще ищет Dockerfile

## Проблема
Railway продолжает искать Dockerfile, даже после настройки Railpack.

## Причина
Builder в UI Railway НЕ изменен на Railpack. Настройки UI имеют приоритет над конфигурационными файлами.

## РЕШЕНИЕ: Измените Builder в UI Railway

### Шаг 1: Откройте настройки Build

1. В Railway откройте ваш проект
2. Выберите сервис "VeraliA" (Client Server)
3. Перейдите в **Settings**
4. Нажмите **"Build"** в правом меню (или прокрутите до раздела Build)

### Шаг 2: Измените Builder на Railpack

1. Найдите раздел **"Builder"**
2. Должна быть карточка с текущим Builder (вероятно "Nixpacks" или что-то связанное с Dockerfile)
3. **Нажмите на эту карточку** - откроется выпадающее меню
4. В выпадающем меню выберите **"Railpack"** (помечен как "Default")
5. **Сохраните изменения** (если есть кнопка Save)

### Шаг 3: Проверьте настройки

После изменения Builder на Railpack:
- **Builder**: должен быть "Railpack" (не Nixpacks, не Dockerfile)
- **Root Directory**: `client-server` (должно быть установлено)
- **Custom Build Command**: пусто
- **Dockerfile Path**: не должно быть (или игнорируется)

### Шаг 4: Перезапустите деплой

1. Перейдите на вкладку **Deployments**
2. Найдите последний failed deployment
3. Нажмите на три точки (⋮) рядом с deployment
4. Выберите **"Redeploy"**
5. Или дождитесь автоматического перезапуска

## Проверка в логах

После изменения Builder на Railpack в логах должно быть:
```
Using Railpack
Detected Python project
Installing dependencies from requirements.txt
```

А НЕ:
```
Dockerfile 'Dockerfile' does not exist
```

## Если Builder не меняется в UI

### Вариант 1: Пересоздайте сервис

1. **Settings** → прокрутите вниз → **Danger** → **Delete Service**
2. Создайте новый сервис из GitHub репозитория
3. **Сразу после создания:**
   - **Settings** → **Source** → **Root Directory**: `client-server`
   - **Settings** → **Build** → **Builder**: выберите **Railpack**
   - Сохраните
4. Дождитесь автоматического деплоя

### Вариант 2: Проверьте, что нет Dockerfile

1. Убедитесь, что в `client-server/` нет файла `Dockerfile`
2. Если есть `Dockerfile.backup` - это нормально
3. Railway не должен искать Dockerfile при использовании Railpack

## Важно

**Builder ДОЛЖЕН быть изменен в UI Railway!**

Конфигурационные файлы (railway.json, railpack.toml) не помогут, если Builder в UI не изменен на Railpack.

## Контрольный список

- [ ] Builder в UI изменен на Railpack ✅
- [ ] Root Directory = `client-server` ✅
- [ ] Dockerfile НЕ существует в `client-server/` ✅
- [ ] requirements.txt существует ✅
- [ ] Деплой перезапущен ✅

