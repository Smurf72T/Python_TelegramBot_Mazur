# notes_bot/statistics.py

from datetime import date
from asgiref.sync import sync_to_async
from events.models import BotStatistics


@sync_to_async
def increment_statistics(field: str):
    """
    Одна синхронная функция, которая:
    - получает или создаёт запись за сегодня
    - увеличивает нужный счётчик
    - сохраняет изменения
    """
    today = date.today()

    stat, _ = BotStatistics.objects.get_or_create(
        date=today,
        defaults={
            'user_count': 0,
            'event_count': 0,
            'edited_events': 0,
            'cancelled_events': 0,
        }
    )

    # Увеличиваем нужный счётчик
    current_value = getattr(stat, field)
    setattr(stat, field, current_value + 1)
    stat.save()


async def increment_stat(field: str):
    """Асинхронная обёртка для использования в хендлерах бота"""
    await increment_statistics(field)