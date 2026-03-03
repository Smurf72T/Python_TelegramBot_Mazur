"""
Модель события (заметки/встречи).

Содержит определение модели Event для управления событиями, создаваемыми
пользователями через Telegram-бот. Каждое событие связано с конкретным
пользователем и может быть публичным или приватным.
"""

from django.db import models


class Event(models.Model):
    """
    Модель события (заметки/встречи).

    Хранит информацию о событиях, создаваемых пользователями через Telegram-бот.
    Каждое событие связано с конкретным пользователем и может быть публичным
    или приватным.

    Атрибуты:
        user: Пользователь, создавший событие (ForeignKey на UserProfile)
        name: Название события (максимум 255 символов)
        event_date: Дата события
        event_time: Время события
        details: Дополнительные детали события (опционально)
        is_public: Флаг публичности события (по умолчанию False)
    """

    # Связь с пользователем, создавшим событие
    # CASCADE означает, что при удалении пользователя удалятся все его события
    user = models.ForeignKey(
        'events.UserProfile',
        on_delete=models.CASCADE,
        related_name='events'
    )

    # Основная информация о событии
    name = models.CharField(
        max_length=255,
        verbose_name="Название события"
    )
    event_date = models.DateField(
        verbose_name="Дата события"
    )
    event_time = models.TimeField(
        verbose_name="Время события"
    )
    details = models.TextField(
        blank=True,
        default='',
        verbose_name="Детали события"
    )

    # Флаг публичности события
    # Публичные события могут быть видны другим пользователям
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичное событие"
    )

    class Meta:
        """Метаданные модели Event."""
        db_table = 'events'  # Имя таблицы в базе данных
        # Сортировка по убыванию даты и времени (сначала новые события)
        ordering = ['-event_date', '-event_time']
        verbose_name = "Событие"
        verbose_name_plural = "События"

    def __str__(self):
        """
        Строковое представление события.

        Returns:
            str: Название события с датой и временем
        """
        return f"{self.name} ({self.event_date} {self.event_time})"