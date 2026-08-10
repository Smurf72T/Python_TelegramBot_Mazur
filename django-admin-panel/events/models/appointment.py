"""
Модель встречи (приглашения).

Содержит определение модели Appointment для управления приглашениями
пользователей на участие в событиях. Каждое приглашение имеет организатора,
событие, участника и статус.
"""

from django.db import models


class Appointment(models.Model):
    """
    Модель встречи/приглашения на событие.

    Представляет приглашение пользователя на участие в событии.
    Каждое приглашение имеет организатора, событие, участника и статус.

    Атрибуты:
        organizer_telegram_id: Telegram ID организатора (создавшего приглашение)
        event: Событие, на которое приглашают
        participant_telegram_id: Telegram ID приглашённого участника
        date: Дата встречи
        time: Время встречи
        details: Дополнительные детали встречи
        status: Статус приглашения (pending/confirmed/declined/cancelled)
        created_at: Время создания приглашения
    """

    # Telegram ID организатора (пользователь Telegram, создавший приглашение)
    organizer_telegram_id = models.BigIntegerField(
        verbose_name="Telegram ID организатора"
    )

    # Событие, на которое приглашают
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="Событие"
    )

    # Telegram ID участника, которого пригласили
    participant_telegram_id = models.BigIntegerField(
        verbose_name="Telegram ID участника"
    )

    # Дата и время встречи
    date = models.DateField(
        verbose_name="Дата встречи"
    )
    time = models.TimeField(
        verbose_name="Время встречи"
    )

    # Дополнительная информация о встрече
    details = models.TextField(
        blank=True,
        default='',
        verbose_name="Детали встречи"
    )

    # Статус приглашения
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает подтверждения'),
            ('confirmed', 'Подтверждено'),
            ('declined', 'Отклонено'),
            ('cancelled', 'Отменено'),
        ],
        default='pending',
        verbose_name="Статус"
    )

    # Время создания записи
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано"
    )

    class Meta:
        """Метаданные модели Appointment."""
        db_table = 'appointments'  # Явно указываем имя таблицы в БД
        verbose_name = "Встреча"
        verbose_name_plural = "Встречи"
        # Ограничение: один человек может иметь только одно приглашение на событие
        unique_together = ('event', 'participant_telegram_id')
        # Сортировка по дате создания (сначала новые)
        ordering = ['-created_at']

    def __str__(self):
        """
        Строковое представление встречи.

        Returns:
            str: Строка с ID, названием события, Telegram ID участника и статусом
        """
        return f"Встреча #{self.id} | {self.event.name} → tg:{self.participant_telegram_id} ({self.status})"