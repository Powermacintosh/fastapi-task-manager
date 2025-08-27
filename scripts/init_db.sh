#!/bin/bash
set -e

echo "Ожидание, пока база данных будет готова..."
# Увеличиваем количество попыток и таймаут
for i in {1..30}; do
  if PGPASSWORD="${DB_PASS}" psql -h "${DB_HOST}" -U "${DB_USER}" -c '\q'; then
    echo "База данных готова!"
    break
  fi
  echo "PostgreSQL недоступен - ожидание... (попытка $i/30)"
  sleep 2
done

# Проверяем, существует ли база данных
if PGPASSWORD="${DB_PASS}" psql -h "${DB_HOST}" -U "${DB_USER}" -lqt | cut -d \| -f 1 | grep -qw "${DB_NAME}"; then
  echo "Проверяем, инициализирована ли база данных..."
  # Проверяем наличие таблицы alembic_version
  if ! PGPASSWORD="${DB_PASS}" psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" -tAc "SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'alembic_version'" | grep -q 1; then
    echo "База существует, но не инициализирована. Применяем миграции..."
    cd /app
    export PYTHONPATH=/app
    poetry run alembic upgrade head
    echo "Миграции успешно применены!"
  else
    echo "База данных уже инициализирована."
  fi
else
  # Если базы нет - создаем и инициализируем
  echo "Создание новой базы..."
  PGPASSWORD="${DB_PASS}" psql -h "${DB_HOST}" -U "${DB_USER}" -c "CREATE DATABASE \"${DB_NAME}\" WITH ENCODING 'UTF8';"
  
  echo "Выполнение миграций..."
  cd /app
  export PYTHONPATH=/app
  poetry run alembic upgrade head
  echo "Инициализация базы данных завершена!"
fi

exec "$@"