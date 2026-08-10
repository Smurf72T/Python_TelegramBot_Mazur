# notes_bot/statistics.py
# Модуль для сбора и управления статистикой бота и пользователей
#
# Содержит синхронные функции для:
# - сбора глобальной статистики бота (по дням)
# - сбора персональной статистики пользователей
# - форматированного вывода статистики
#
# Использует Django ORM для работы с моделями BotStatistics и UserStatistics.

from datetime import date
from typing import Optional

from events.models import BotStatistics, UserProfile, UserStatistics


# ==================== ГЛОБАЛЬНАЯ СТАТИСТИКА БОТА ====================

def increment_global_stat(field: str):
    """
    Увеличивает глобальную статистику бота за текущий день.

    Аргументы:
        field (str): Поле для увеличения счётчика.
                    Допустимые значения: 'user_count', 'event_count',
                    'edited_events', 'cancelled_events'
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

    setattr(stat, field, getattr(stat, field) + 1)
    stat.save()


# ==================== ПЕРСОНАЛЬНАЯ СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ ====================

def increment_user_stat(user_id: int, field: str):
    """
    Увеличивает персональную статистику конкретного пользователя.

    Аргументы:
        user_id (int): Telegram ID пользователя
        field (str): Поле для увеличения счётчика.
                    Допустимые значения: 'created_events', 'edited_events',
                    'cancelled_events'
    """
    profile, _ = UserProfile.objects.get_or_create(telegram_id=user_id)
    stat, _ = UserStatistics.objects.get_or_create(user_telegram_id=profile)

    setattr(stat, field, getattr(stat, field) + 1)
    stat.save()


# ==================== УНИВЕРСАЛЬНЫЕ ФУНКЦИИ ====================

def increment_stat(field: str, user_id: Optional[int] = None):
    """
    Увеличивает глобальную и (при указании user_id) персональную статистику.

    Аргументы:
        field (str): Поле для увеличения счётчика.
                    Допустимые значения: 'user_count', 'event_count',
                    'edited_events', 'cancelled_events'
        user_id (Optional[int]): Telegram ID пользователя. Если указан и поле
                                 относится к событиям, увеличивается также
                                 персональная статистика пользователя.
    """
    increment_global_stat(field)

    if user_id and field in ('event_count', 'edited_events', 'cancelled_events'):
        user_field_mapping = {
            'event_count': 'created_events',
            'edited_events': 'edited_events',
            'cancelled_events': 'cancelled_events',
        }
        increment_user_stat(user_id, user_field_mapping[field])


def get_user_stats(user_id: int) -> str:
    """
    Возвращает отформатированную персональную статистику пользователя.

    Аргументы:
        user_id (int): Telegram ID пользователя

    Возвращает:
        str: Отформатированная строка со статистикой пользователя.
    """
    try:
        stat = UserStatistics.objects.select_related('user_telegram_id').get(
            user_telegram_id__telegram_id=user_id
        )

        return (
            f"📊 Ваша личная статистика:\n\n"
            f"📅 Создано событий: **{stat.created_events}**\n"
            f"✏️ Отредактировано событий: **{stat.edited_events}**\n"
            f"❌ Отменено событий: **{stat.cancelled_events}**"
        )
    except UserStatistics.DoesNotExist:
        return "📊 У вас пока нет личной статистики (ещё не создано событий)"
