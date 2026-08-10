"""
Миграция 0008: переименование таблицы users -> events_userprofile.

Таблица `users` создаётся скриптом init_db.py (устаревший путь инициализации БД),
тогда как модель UserProfile использует стандартное имя таблицы events_userprofile.
Миграция безопасно переименовывает таблицу, если она существует, и ничего не
делает, если целевая таблица уже создана (например, через makemigrations).
"""

from django.db import migrations


def rename_users_table(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT to_regclass('public.users')"
        )
        users_exists = cursor.fetchone()[0] is not None
        cursor.execute(
            "SELECT to_regclass('public.events_userprofile')"
        )
        target_exists = cursor.fetchone()[0] is not None
        if users_exists and not target_exists:
            cursor.execute(
                "ALTER TABLE users RENAME TO events_userprofile"
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_alter_userprofile_table'),
    ]

    operations = [
        migrations.RunPython(rename_users_table, noop),
    ]
