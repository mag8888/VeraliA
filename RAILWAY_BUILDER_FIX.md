# Решение проблемы с Builder на Railway

## Проблема
Railway использует Nixpacks (Deprecated), но все еще ищет Dockerfile. Это конфликт.

## Решение 1: Использовать Nixpacks правильно (БЕЗ Dockerfile)

Если Builder = Nixpacks, то Dockerfile НЕ нужен:

1. **Временно переименуйте или удалите Dockerfile:**
   - В GitHub переименуйте `client-server/Dockerfile` в `client-server/Dockerfile.backup`
   - Или удалите его временно
   - Сделайте коммит и push

2. **Settings → Build:**
   - Builder должен быть: **Nixpacks**
   - Custom Build Command: пусто
   - Railway автоматически определит Python проект

3. **Nixpacks автоматически:**
   - Найдет `requirements.txt`
   - Установит зависимости
   - Запустит `app.py`

## Решение 2: Использовать Dockerfile (если есть опция)

Если в настройках Build есть возможность выбрать Builder:

1. **Settings → Build → Builder:**
   - Выберите **"Dockerfile"** (если есть опция)
   - Или удалите выбор Nixpacks

2. **Settings → Build:**
   - Dockerfile Path: `Dockerfile` (или пусто)
   - Custom Build Command: пусто

3. **Settings → Source:**
   - Root Directory: `client-server` ✅ (уже установлено)

## Решение 3: Проверьте, есть ли опция Dockerfile Builder

В настройках Build может быть выпадающий список Builder:
- Nixpacks (Deprecated)
- Dockerfile
- Другие опции

Если есть опция "Dockerfile" - выберите ее.

## Рекомендация

**Используйте Nixpacks БЕЗ Dockerfile:**

1. Переименуйте `client-server/Dockerfile` → `client-server/Dockerfile.backup`
2. Сделайте коммит и push
3. Railway автоматически использует Nixpacks
4. Должно заработать

Nixpacks проще для Python проектов и не требует Dockerfile.

