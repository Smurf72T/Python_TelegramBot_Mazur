from django.db import models


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_time = models.TimeField()
    details = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'events'
        managed = False               # !!! очень важно — Django НЕ будет пытаться создавать/менять таблицу

    def __str__(self):
        return f"{self.name} ({self.event_date} {self.event_time})"


class BotStatistics(models.Model):
    date             = models.DateField(unique=True)
    user_count       = models.PositiveIntegerField(default=0)
    event_count      = models.PositiveIntegerField(default=0)
    edited_events    = models.PositiveIntegerField(default=0)
    cancelled_events = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Статистика бота"
        verbose_name_plural = "Статистика бота"
        ordering = ['-date']

    def __str__(self):
        return f"Статистика за {self.date}"


class Appointment(models.Model):
    # Кто создал встречу (организатор)
    organizer = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='organized_appointments'
    )

    # На какое событие приглашаем
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    # Кого пригласили
    participant_telegram_id = models.BigIntegerField()  # telegram_id участника

    date = models.DateField()
    time = models.TimeField()
    details = models.TextField(blank=True, default='')

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает подтверждения'),
            ('confirmed', 'Подтверждено'),
            ('declined', 'Отклонено'),
            ('cancelled', 'Отменено'),
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointments'  # явно указываем имя таблицы
        verbose_name = "Встреча"
        verbose_name_plural = "Встречи"
        unique_together = ('event', 'participant_telegram_id')  # один человек — одно приглашение на событие

    def __str__(self):
        return f"Встреча #{self.id} | {self.event.name} → tg:{self.participant_telegram_id} ({self.status})"