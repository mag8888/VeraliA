# Dockerfile в корне проекта для Client Server
# Используется когда Root Directory не установлен

FROM python:3.11-slim

WORKDIR /app

# Копирование requirements.txt из client-server
COPY client-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего содержимого client-server
COPY client-server/ .

# Создание директории для загрузок
RUN mkdir -p uploads

# Railway автоматически предоставляет PORT через переменную окружения
EXPOSE 8000

CMD ["python", "app.py"]

