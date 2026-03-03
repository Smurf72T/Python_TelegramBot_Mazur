# Generated manually for adding export_token field to UserProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_remove_userstatistics_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='export_token',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Секретный токен для безопасной выгрузки',
                max_length=64,
                null=True,
                unique=True
            ),
        ),
    ]