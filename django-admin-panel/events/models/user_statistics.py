"""
Модель личной статистики пользователя.

Содержит определение модели UserStatistics для хранения индивидуальной
статистики активности каждого пользователя. Связана с UserProfile
отношением One-to-One (один пользователь — одна запись статистики).
"""

from django.db import models


class UserStatistics(models.Model):
    """
    Модель личной статистики пользователя.

    Хранит индивидуальную статистику активности каждого пользователя.
    Связана с UserProfile отношением One-to-One (один пользователь — одна запись статистики).

    Атрибуты:
        user_telegram_id: Ссылка на профиль пользователя (первичный ключ)
        created_events: Количество созданных пользователем событий
        edited_events: Количество отредактированных пользователем событий
        cancelled_events: Количество отменённых пользователем событий
        updated_at: Время последнего обновления статистики
    """

    # Связь с профилем пользователя (One-to-One)
    # Явно указываем имя столбца в БД для совместимости с существующей схемой
    user_telegram_id = models.OneToOneField(
        'events.UserProfile',
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='user_telegram_id',
        related_name='statistics',
        verbose_name="Пользователь"
    )

    # Счётчики активности пользователя
    created_events = models.PositiveIntegerField(
        default=0,
        verbose_name="Создано событий"
    )
    edited_events = models.PositiveIntegerField(
        default=0,
        verbose_name="Отредактировано событий"
    )
    cancelled_events = models.PositiveIntegerField(
        default=0,
        verbose_name="Отменено событий"
    )

    # Время последнего обновления статистики
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено"
    )

    class Meta:
        """Метаданные модели UserStatistics."""
        db_table = 'user_statistics'
        verbose_name = "Личная статистика пользователя"
        verbose_name_plural = "Личная статистика пользователей"
        # Сортировка по времени обновления (сначала свежие)
        ordering = ['-updated_at']

    def __str__(self):
        """
        Строковое представление статистики пользователя.

        Returns:
            str: Строка с Telegram ID пользователя
        """
        return f"Статистика {self.user_telegram_id}"