FROM python:3.13-slim

# Устанавливаем зависимости для postgresql-client
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости приложения
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    pip install requests

# Копируем исходный код
COPY . .

# Порт, который будет слушать приложение
EXPOSE ${APP_PORT}