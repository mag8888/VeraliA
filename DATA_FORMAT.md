# Формат данных Instagram профиля

## Структура данных в базе данных

При анализе Instagram профиля сохраняются следующие данные:

```json
{
    "id": 1,
    "username": "example_user",
    "followers": 125000,
    "following": 450,
    "posts_count": 320,
    "bio": "Content creator | Travel enthusiast | Follow for daily updates",
    "engagement_rate": 0.045,
    "screenshot_path": "uploads/example_user_20240101_120000.jpg",
    "analyzed_at": "2024-01-01T12:00:00",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
}
```

## Описание полей

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Уникальный идентификатор записи |
| `username` | String | Username Instagram пользователя (уникальный) |
| `followers` | Integer | Количество подписчиков |
| `following` | Integer | Количество подписок |
| `posts_count` | Integer | Количество публикаций |
| `bio` | String (nullable) | Биография профиля |
| `engagement_rate` | Float (nullable) | Engagement rate (0-1), вычисляется автоматически |
| `screenshot_path` | String (nullable) | Путь к сохраненному скриншоту |
| `analyzed_at` | DateTime | Дата и время последнего анализа |
| `created_at` | DateTime | Дата создания записи |
| `updated_at` | DateTime | Дата последнего обновления |

## Пример скриншота

Скриншот должен содержать:
- Статистику профиля (подписчики, подписки, публикации)
- Биографию (опционально)
- Другие видимые метрики

### Рекомендации по скриншоту:
- Высокое качество изображения
- Хорошая читаемость текста
- Видны все основные метрики
- Формат: JPG, PNG

## API Response Format

### GET /api/data/{username}

```json
{
    "username": "example_user",
    "followers": 125000,
    "following": 450,
    "posts_count": 320,
    "bio": "Content creator | Travel enthusiast",
    "engagement_rate": 0.045,
    "analyzed_at": "2024-01-01T12:00:00",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
}
```

### POST /api/analyze

**Request:**
- `username` (form-data): string
- `screenshot` (file): image file

**Response:**
```json
{
    "status": "success",
    "message": "Данные успешно сохранены",
    "data": {
        "username": "example_user",
        "followers": 125000,
        "following": 450,
        "posts_count": 320,
        "bio": "Content creator",
        "engagement_rate": 0.045,
        "analyzed_at": "2024-01-01T12:00:00"
    }
}
```

