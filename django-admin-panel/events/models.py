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