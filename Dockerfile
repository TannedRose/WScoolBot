# Dockerfile
FROM python:3.11-slim

# Установка зависимостей ОС (если нужны, например, для psycopg2)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Создание непривилегированного пользователя
RUN addgroup --system app && \
    adduser --system --ingroup app --disabled-password --gecos "" app

# Установка зависимостей Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода с правильными правами
COPY --chown=app:app . .
USER app

# Запуск (по умолчанию — бот)
CMD ["python", "main.py"]