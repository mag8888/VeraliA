FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей (если нужны)
# RUN apt-get update && apt-get install -y \
#     && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директории для загрузок
RUN mkdir -p uploads

# Railway автоматически предоставляет PORT через переменную окружения
EXPOSE 8000

CMD ["python", "app.py"]

