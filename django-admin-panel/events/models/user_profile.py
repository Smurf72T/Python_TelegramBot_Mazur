"""
Модель профиля пользователя Telegram-бота.

Содержит определение модели UserProfile для хранения информации о пользователях,
взаимодействующих с ботом. Использует существующую таблицу 'users' в базе данных.
"""

from django.db import models


class UserProfile(models.Model):
    """
    Модель профиля пользователя Telegram-бота.

    Хранит информацию о пользователях, взаимодействующих с ботом.
    Использует существующую таблицу 'users' в базе данных.

    Атрибуты:
        telegram_id: Уникальный идентификатор пользователя в Telegram (первичный ключ)
        username: Имя пользователя в Telegram (опционально)
        first_name: Имя пользователя (опционально)
        last_name: Фамилия пользователя (опционально)
        email: Email пользователя (опционально)
        registered_at: Дата и время регистрации пользователя
        export_token: Секретный токен для безопасной выгрузки данных (опционально)
    """

    # Основной идентификатор пользователя (Telegram ID)
    # Используется как первичный ключ для связи с существующей таблицой
    telegram_id = models.BigIntegerField(
        unique=True,
        primary_key=True,
        verbose_name="Telegram ID"
    )

    # Информация о пользователе из Telegram
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Имя пользователя"
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Фамилия"
    )
    email = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Email"
    )

    # Временные метки
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )

    # Токен для безопасной выгрузки данных пользователя
    export_token = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        unique=True,
        help_text="Секретный токен для безопасной выгрузки",
        verbose_name="Токен выгрузки"
    )

    class Meta:
        """Метаданные модели UserProfile."""
        db_table = 'events_userprofile'  # Используем существующую таблицу Django
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"
        # Сортировка по дате регистрации (сначала новые)
        ordering = ['-registered_at']

    def __str__(self):
        """
        Строковое представление профиля пользователя.

        Returns:
            str: Имя пользователя с Telegram ID или только Telegram ID
        """
        return f"@{self.username} (tg:{self.telegram_id})" if self.username else f"tg:{self.telegram_id}"