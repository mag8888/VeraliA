# Исправление: DATABASE_URL использует внутренний хост

## ❌ Проблема:

В Variables для Parsing Server установлены:
- `DATABASE_PUBLIC_URL`: `postgresql://...@yamanote.proxy.rlwy.net:32013/railway` ✅ (публичный URL)
- `DATABASE_URL`: `postgresql://...@postgres.railway.internal:5432/railway` ❌ (внутренний URL)

Код использует `DATABASE_URL`, который использует внутренний хост `postgres.railway.internal`, который не работает.

---

## ✅ Решение:

### Замените значение DATABASE_URL на значение из DATABASE_PUBLIC_URL

1. **Parsing Server (VeraliA)** → **Settings** → **Variables**
2. Найдите переменную `DATABASE_PUBLIC_URL`
3. **Скопируйте** её значение (полный URL с `yamanote.proxy.rlwy.net`)
4. Найдите переменную `DATABASE_URL`
5. Нажмите на неё для редактирования
6. **Удалите** текущее значение (с `postgres.railway.internal`)
7. **Вставьте** скопированное значение из `DATABASE_PUBLIC_URL`
8. **Сохраните** (галочка ✓)
9. **Redeploy** Parsing Server

---

## 📋 Пошаговая инструкция:

1. **Parsing Server (VeraliA)** → **Settings** → **Variables**
2. Найдите `DATABASE_PUBLIC_URL`
3. **Скопируйте** значение: `postgresql://postgres:password@yamanote.proxy.rlwy.net:32013/railway`
4. Найдите `DATABASE_URL`
5. **Нажмите** на значение для редактирования
6. **Удалите** старое значение: `postgresql://...@postgres.railway.internal:5432/railway`
7. **Вставьте** новое значение из `DATABASE_PUBLIC_URL`: `postgresql://postgres:password@yamanote.proxy.rlwy.net:32013/railway`
8. **Сохраните** (галочка ✓)
9. **Redeploy** Parsing Server

---

## ✅ После исправления:

В Variables должно быть:
- `DATABASE_PUBLIC_URL`: `postgresql://...@yamanote.proxy.rlwy.net:32013/railway`
- `DATABASE_URL`: `postgresql://...@yamanote.proxy.rlwy.net:32013/railway` ✅ (теперь публичный URL)

В логах должно появиться:
```
INFO: Database initialized
INFO: Started server process [1]
INFO: Application startup complete.
```

---

## 🔍 Почему это важно:

- **Внутренний хост** (`postgres.railway.internal`) работает только внутри одного проекта Railway
- **Публичный хост** (`yamanote.proxy.rlwy.net`) работает из любого места
- Код использует `DATABASE_URL`, поэтому нужно установить публичный URL

---

## ⚠️ Альтернатива:

Если не хотите менять `DATABASE_URL`, можно изменить код, чтобы использовать `DATABASE_PUBLIC_URL`:

1. В `parsing-server/database.py` измените:
   ```python
   DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL", "...")
   ```

Но проще просто заменить значение `DATABASE_URL` на значение из `DATABASE_PUBLIC_URL`.

---

## 🎯 Итого:

1. ✅ Скопируйте значение `DATABASE_PUBLIC_URL`
2. ✅ Замените значение `DATABASE_URL` на скопированное
3. ✅ Сохраните и Redeploy

После этого подключение должно работать!

