# КРИТИЧНО: Настройка Builder в UI Railway

## Проблема
Railway все еще ищет Dockerfile, даже после создания railway.json и nixpacks.toml.

## Причина
Настройки Builder в UI Railway могут переопределять конфигурационные файлы.

## РЕШЕНИЕ: Измените Builder в UI

### Шаг 1: Откройте настройки Build

1. **Settings** → нажмите **"Build"** в правом меню
2. Найдите раздел **"Builder"**

### Шаг 2: Измените Builder на Nixpacks

1. В разделе **"Builder"** должно быть выпадающее меню
2. Сейчас там, вероятно, выбрано что-то связанное с Dockerfile
3. **Выберите "Nixpacks"** из выпадающего меню
4. **Сохраните изменения**

### Шаг 3: Проверьте настройки

После изменения Builder на Nixpacks:
- **Custom Build Command**: должно быть пусто
- **Dockerfile Path**: не должно быть (или игнорируется)
- **Root Directory**: `client-server` (должно быть установлено)

### Шаг 4: Перезапустите деплой

1. Перейдите на **Deployments**
2. Выберите последний failed deployment
3. Нажмите три точки (⋮) → **"Redeploy"**
4. Или дождитесь автоматического перезапуска

## Альтернатива: Если нет опции Nixpacks в UI

Если в UI нет опции выбора Builder:

1. **Удалите все конфигурационные файлы** (railway.json, nixpacks.toml)
2. **Убедитесь, что Dockerfile НЕ существует** (переименован в .backup)
3. Railway должен автоматически использовать Nixpacks по умолчанию

## Проверка в логах

После изменения Builder на Nixpacks в логах должно быть:
```
Using Nixpacks
Detected Python project
Installing dependencies...
```

А НЕ:
```
Dockerfile 'Dockerfile' does not exist
```

## Важно

**Настройки в UI имеют приоритет над конфигурационными файлами!**

Поэтому нужно явно изменить Builder в UI на Nixpacks.

