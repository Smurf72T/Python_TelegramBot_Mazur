#!/bin/bash

# =============================================================================
# Entrypoint скрипт для Django Admin Panel
# =============================================================================

RUN_ENV=${RUN_ENV:-"local"}

if [ "$RUN_ENV" = "docker" ]; then
    DB_HOST=${DB_HOST_DOCKER:-"db"}
else
    DB_HOST=${DB_HOST_LOCAL:-"localhost"}
fi

DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}

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

echo "Создание суперпользователя..."
cat << EOF | python /app/manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin_sup').exists():
    User.objects.create_superuser(
        'admin_sup',
        'admin@admin.admin',
        'admin123'
    )
    print('Суперпользователь admin_sup успешно создан.')
else:
    print('Суперпользователь admin_sup уже существует.')
EOF

echo "Запуск Django-сервера..."
exec python /app/manage.py runserver 0.0.0.0:8000