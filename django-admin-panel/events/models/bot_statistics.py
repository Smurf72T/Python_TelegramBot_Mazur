"""
Модель общей статистики работы бота.

Содержит определение модели BotStatistics для сбора и хранения агрегированной
статистики использования бота за конкретную дату. Записи создаются ежедневно
и содержат сводную информацию о деятельности всех пользователей системы.
"""

from django.db import models


class BotStatistics(models.Model):
    """
    Модель общей статистики работы бота.

    Хранит агрегированную статистику использования бота за конкретную дату.
    Записи создаются ежедневно и содержат сводную информацию о деятельности
    всех пользователей системы.

    Атрибуты:
        date: Дата, за которую собрана статистика (уникальное поле)
        user_count: Количество пользователей, активных в этот день
        event_count: Количество созданных событий
        edited_events: Количество отредактированных событий
        cancelled_events: Количество отменённых событий
    """

    # Дата статистики (уникальное поле - одна запись на день)
    date = models.DateField(
        unique=True,
        verbose_name="Дата статистики"
    )

    # Счётчики активности
    user_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество пользователей"
    )
    event_count = models.PositiveIntegerField(
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

    class Meta:
        """Метаданные модели BotStatistics."""
        verbose_name = "Статистика бота"
        verbose_name_plural = "Статистика бота"
        # Сортировка по убыванию даты (сначала новые записи)
        ordering = ['-date']

    def __str__(self):
        """
        Строковое представление статистики.

        Returns:
            str: Строка с датой статистики
        """
        return f"Статистика за {self.date}"