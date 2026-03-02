#!/usr/bin/env python
"""
Инициализация тестовой базы данных
"""
import os
import sys
import django
from django.conf import settings

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()

# Импортируем модели для создания таблиц
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Создаем таблицы в тестовой БД
    execute_from_command_line(['manage.py', 'migrate', '--database=default'])