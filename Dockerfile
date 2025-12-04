# Dockerfile в корне для теста
# Этот файл создан для диагностики проблемы Railway
# Обычно используется Dockerfile из client-server/ или parsing-server/

FROM python:3.11-slim

WORKDIR /app

# Копирование и установка зависимостей
COPY client-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY client-server/ .

# Создание директории для загрузок
RUN mkdir -p uploads

# Railway автоматически предоставляет PORT через переменную окружения
EXPOSE 8000

CMD ["python", "app.py"]

