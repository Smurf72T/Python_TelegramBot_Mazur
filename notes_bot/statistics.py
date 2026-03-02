# notes_bot/statistics.py

from datetime import date
from asgiref.sync import sync_to_async
from events.models import BotStatistics, UserStatistics, UserProfile


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


@sync_to_async
def increment_global_stat(field: str):
    """Увеличивает глобальную статистику бота (по дням)"""
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
    setattr(stat, field, getattr(stat, field) + 1)
    stat.save()


@sync_to_async
def increment_user_stat(user_id: int, field: str):
    """
    Увеличивает личную статистику пользователя
    Поле field может быть: 'created_events', 'edited_events', 'cancelled_events'
    """
    profile, _ = UserProfile.objects.get_or_create(telegram_id=user_id)
    stat, _ = UserStatistics.objects.get_or_create(user_telegram_id=profile)
    setattr(stat, field, getattr(stat, field) + 1)
    stat.save()


async def increment_stat(field: str, user_id: int = None):
    """
    Универсальная асинхронная функция:
    - field — 'user_count', 'event_count', 'edited_events', 'cancelled_events'
    - если передан user_id — также увеличивает личную статистику
    """
    await increment_global_stat(field)

    if user_id and field in ('event_count', 'edited_events', 'cancelled_events'):
        user_field = {
            'event_count': 'created_events',
            'edited_events': 'edited_events',
            'cancelled_events': 'cancelled_events'
        }[field]
        await increment_user_stat(user_id, user_field)


async def get_user_stats(user_id: int) -> str:
    """Возвращает красивую строку со статистикой конкретного пользователя"""
    try:
        stat = await sync_to_async(UserStatistics.objects.select_related('user').get)(
            user__telegram_id=user_id
        )
        return (
            f"📊 Ваша личная статистика:\n\n"
            f"📅 Создано событий: **{stat.created_events}**\n"
            f"✏️ Отредактировано событий: **{stat.edited_events}**\n"
            f"❌ Отменено событий: **{stat.cancelled_events}**"
        )
    except UserStatistics.DoesNotExist:
        return "📊 У вас пока нет личной статистики (ещё не создано событий)"