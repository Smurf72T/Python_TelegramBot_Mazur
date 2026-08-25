#!/bin/bash

# =============================================================================
# Entrypoint скрипт для Django Admin Panel
# =============================================================================

RUN_ENV=${RUN_ENV:-"local"}

# =============================================================================
# Определение хоста базы данных
# =============================================================================
# Хост базы данных зависит от окружения выполнения:
# - В Docker: используем имя сервиса "db" (из docker-compose.yml)
# - Локально: используем "localhost"
# ОБЯЗАТЕЛЬНО: установите DB_HOST_DOCKER или DB_HOST_LOCAL в .env
if [ "$RUN_ENV" = "docker" ]; then
    if [ -z "$DB_HOST_DOCKER" ]; then echo "Ошибка: DB_HOST_DOCKER не установлена"; exit 1; fi
    DB_HOST=$DB_HOST_DOCKER
else
    if [ -z "$DB_HOST_LOCAL" ]; then echo "Ошибка: DB_HOST_LOCAL не установлена"; exit 1; fi
    DB_HOST=$DB_HOST_LOCAL
fi

# =============================================================================
# Конфигурация подключения к базе данных
# =============================================================================
# Параметры подключения к PostgreSQL (обязательные переменные окружения)
if [ -z "$DB_PORT" ]; then echo "Ошибка: DB_PORT не установлена"; exit 1; fi
if [ -z "$DB_USER" ]; then echo "Ошибка: DB_USER не установлена"; exit 1; fi
if [ -z "$DB_PASSWORD" ]; then echo "Ошибка: DB_PASSWORD не установлена"; exit 1; fi

DB_PORT=$DB_PORT
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

echo "Ожидание готовности базы данных на хосте $DB_HOST..."
max_retries=60
retry_delay=2
attempt=1

while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  if [ $attempt -ge $max_retries ]; then
    echo "Ошибка: База данных не готова после $max_retries попыток"
    exit 1
  fi
  echo "Попытка $attempt/$max_retries: База данных не готова, ждем $retry_delay сек..."
  sleep $retry_delay
  attempt=$((attempt + 1))
done

echo "База данных готова к подключению"

echo "Применение миграций..."
python /app/manage.py migrate --noinput

# =============================================================================
# Создание суперпользователя Django
# =============================================================================
# Проверяем существование суперпользователя и создаем его при необходимости.
# ОБЯЗАТЕЛЬНО: установите ADMIN_PASSWORD в .env
if [ -z "$ADMIN_PASSWORD" ]; then echo "Ошибка: ADMIN_PASSWORD не установлена"; exit 1; fi

echo "Создание суперпользователя..."
cat << EOF | python /app/manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin_sup').exists():
    User.objects.create_superuser(
        'admin_sup',      # Имя пользователя
        'admin@admin.admin',  # Email
        '$ADMIN_PASSWORD'        # Пароль из переменной окружения
    )
    print('Суперпользователь admin_sup успешно создан.')
else:
    print('Суперпользователь admin_sup уже существует.')
EOF

echo "Запуск Django-сервера..."
exec python /app/manage.py runserver 0.0.0.0:8000