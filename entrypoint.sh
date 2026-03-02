#!/bin/bash

# Ожидание готовности базы данных
echo "Ожидание готовности базы данных..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 1
done

# Применение миграций Django
echo "Применение миграций..."
python /app/django-admin-panel/manage.py migrate --noinput

# Создание суперпользователя Django
echo "Создание суперпользователя..."
cat << EOF | python /app/django-admin-panel/manage.py shell
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

# Запуск Django-сервера
echo "Запуск Django-сервера..."
exec python /app/django-admin-panel/manage.py runserver 0.0.0.0:8000
