# СРОЧНОЕ РЕШЕНИЕ: Dockerfile не найден

## Проблема
Railway показывает ошибку: `Dockerfile 'Dockerfile' does not exist`

## Проверка 1: Убедитесь, что Root Directory установлен

1. Откройте **Settings** → **Source**
2. Проверьте поле **"Root Directory"**
3. Должно быть: `client-server` (без слэша `/`, без пробелов)
4. Если пусто или неправильно - введите `client-server` и **СОХРАНИТЕ**

## Проверка 2: Проверьте настройки Build

1. **Settings** → **Build**
2. **Custom Build Command**: должно быть **ПУСТО**
3. **Dockerfile Path**: `Dockerfile` (или пусто)
4. **Сохраните**

## Проверка 3: Проверьте GitHub

Убедитесь, что Dockerfile существует в GitHub:
- Откройте: https://github.com/mag8888/VeraliA/tree/main/client-server
- Должен быть файл `Dockerfile`

## Решение: Пересоздайте сервис (100% работает)

### Шаг 1: Удалите текущий сервис
1. **Settings** → прокрутите вниз до раздела **"Danger"**
2. Нажмите **"Delete Service"**
3. Подтвердите удаление

### Шаг 2: Создайте новый сервис
1. В проекте нажмите **"+ New"**
2. Выберите **"GitHub Repo"**
3. Выберите репозиторий `mag8888/VeraliA`

### Шаг 3: СРАЗУ после создания (ВАЖНО!)
**До того как Railway начнет первый деплой:**

1. Откройте **Settings** → **Source**
2. Установите **Root Directory**: `client-server`
3. **Сохраните** (нажмите кнопку сохранения если есть)

4. Откройте **Settings** → **Build**
5. Убедитесь, что **Custom Build Command** пусто
6. **Dockerfile Path**: `Dockerfile` (или оставьте пустым)
7. **Сохраните**

8. Дождитесь автоматического деплоя

## Альтернатива: Используйте Nixpacks

Если Dockerfile не работает:

1. **Settings** → **Source** → **Root Directory**: оставьте **ПУСТЫМ**
2. **Settings** → **Build** → **Custom Build Command**: оставьте **ПУСТЫМ**
3. Railway автоматически определит Python проект
4. Но лучше использовать Dockerfile

## Проверка после пересоздания

В логах должно быть:
```
Root directory: client-server
Building from Dockerfile: Dockerfile
```

Если видите:
```
Root directory: /
```
→ Root Directory не установлен!

## Если все еще не работает

1. Проверьте, что в GitHub файл существует:
   - https://github.com/mag8888/VeraliA/blob/main/client-server/Dockerfile

2. Сделайте новый коммит (даже пустой) чтобы Railway обновил репозиторий:
   ```bash
   git commit --allow-empty -m "Trigger Railway rebuild"
   git push
   ```

3. Проверьте логи Railway - должно показать правильный Root Directory

