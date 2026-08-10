"""
Миграция 0009: замена FK организатора на Telegram ID.

Модель Appointment отвязана от auth.User: вместо внешнего ключа `organizer`
используется скалярное поле organizer_telegram_id (BigIntegerField).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_rename_users_to_events_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='organizer',
        ),
        migrations.AddField(
            model_name='appointment',
            name='organizer_telegram_id',
            field=models.BigIntegerField(
                default=0,
                verbose_name='Telegram ID организатора',
            ),
            preserve_default=False,
        ),
    ]
