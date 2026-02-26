from django.db import models


class Event(models.Model):
    user = models.ForeignKey(
        'UserProfile',
        on_delete=models.CASCADE,
        related_name='events'
    )
    name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_time = models.TimeField()
    details = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'events'
        ordering = ['-event_date', '-event_time']

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


class UserProfile(models.Model):
    telegram_id = models.BigIntegerField(unique=True, primary_key=True)
    username    = models.CharField(max_length=255, blank=True, null=True)
    first_name  = models.CharField(max_length=255, blank=True, null=True)
    last_name   = models.CharField(max_length=255, blank=True, null=True)
    email       = models.CharField(max_length=255, blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'          # используем существующую таблицу
        managed = False             # Django НЕ будет создавать/менять таблицу
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"

    def __str__(self):
        return f"@{self.username} (tg:{self.telegram_id})" if self.username else f"tg:{self.telegram_id}"


class UserStatistics(models.Model):
    user = models.OneToOneField(
        'UserProfile',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='statistics'
    )
    created_events   = models.PositiveIntegerField(default=0)
    edited_events    = models.PositiveIntegerField(default=0)
    cancelled_events = models.PositiveIntegerField(default=0)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_statistics'
        verbose_name = "Личная статистика пользователя"
        verbose_name_plural = "Личная статистика пользователей"

    def __str__(self):
        return f"Статистика {self.user}"