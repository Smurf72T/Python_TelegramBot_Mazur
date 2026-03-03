#!/usr/bin/env python
"""Проверка структуры базы данных и наличия поля export_token"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.local_settings')
django.setup()

from events.models import UserProfile
from django.db import connection

def check_database_structure():
    print("=== Проверка структуры базы данных ===\n")
    
    # Проверяем поля модели
    print("Поля модели UserProfile:")
    for field in UserProfile._meta.get_fields():
        print(f"  - {field.name}: {field.__class__.__name__}")
        if hasattr(field, 'max_length') and field.max_length:
            print(f"    Максимальная длина: {field.max_length}")
        if hasattr(field, 'unique') and field.unique:
            print(f"    Уникальное поле: Да")
        if hasattr(field, 'null') and field.null:
            print(f"    Может быть NULL: Да")
        if hasattr(field, 'blank') and field.blank:
            print(f"    Может быть пустым: Да")
        if hasattr(field, 'help_text') and field.help_text:
            print(f"    Описание: {field.help_text}")
        print()

    # Проверяем структуру таблицы в базе данных
    print("Структура таблицы users в базе данных:")
    with connection.cursor() as cursor:
        cursor.execute('PRAGMA table_info(users)')
        columns = cursor.fetchall()
        for column in columns:
            print(f"  - {column[1]}: {column[2]} (NOT NULL: {column[3]}, DEFAULT: {column[4]})")

    # Проверяем, есть ли поле export_token
    has_export_token = any(col[1] == 'export_token' for col in columns)
    print(f"\nПоле export_token существует: {has_export_token}")
    
    if has_export_token:
        print("✅ Миграция успешно применена! Поле export_token добавлено в базу данных.")
    else:
        print("❌ Поле export_token не найдено в базе данных.")
    
    return has_export_token

if __name__ == '__main__':
    check_database_structure()