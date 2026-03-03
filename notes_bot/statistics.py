# notes_bot/statistics.py
# Модуль для сбора и управления статистикой бота и пользователей
#
# Данный модуль предоставляет функции для:
# - Сбора глобальной статистики по боту (по дням)
# - Сбора персональной статистики пользователей
# - Форматированного вывода статистики
#
# Использует Django ORM для работы с моделями BotStatistics и UserStatistics

import os
import django

# Настройка Django перед импортом моделей
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()

from datetime import date
from typing import Optional
from asgiref.sync import sync_to_async
from events.models import BotStatistics, UserStatistics, UserProfile


# ==================== ГЛОБАЛЬНАЯ СТАТИСТИКА БОТА ====================

@sync_to_async
def increment_statistics(field: str):
    """
    УСТАРЕВШАЯ ФУНКЦИЯ
    
    Синхронная функция для увеличения глобального счётчика статистики.
    
    Аргументы:
        field (str): Название поля для увеличения.
                    Допустимые значения: 'user_count', 'event_count',
                    'edited_events', 'cancelled_events'
    
    Логика работы:
        1. Получает текущую дату
        2. Ищет запись статистики за сегодняшний день
        3. Если запись не найдена - создаёт новую с нулевыми значениями
        4. Увеличивает указанный счётчик на 1
        5. Сохраняет изменения в базе данных
    
    Возвращает:
        None
    """
    today = date.today()

    # Получаем или создаём запись статистики за сегодняшний день
    stat, _ = BotStatistics.objects.get_or_create(
        date=today,
        defaults={
            'user_count': 0,
            'event_count': 0,
            'edited_events': 0,
            'cancelled_events': 0,
        }
    )

    # Получаем текущее значение счётчика и увеличиваем его на 1
    current_value = getattr(stat, field)
    setattr(stat, field, current_value + 1)
    stat.save()


@sync_to_async
def increment_global_stat(field: str):
    """
    Увеличивает глобальную статистику бота по дням.
    
    Эта функция работает с моделью BotStatistics и собирает статистику
    по всем действиям в боте, независимо от пользователя.
    
    Аргументы:
        field (str): Поле для увеличения счётчика.
                    Допустимые значения: 'user_count', 'event_count',
                    'edited_events', 'cancelled_events'
    
    Логика работы:
        1. Определяет текущую дату
        2. Получает или создаёт запись BotStatistics за сегодня
        3. Увеличивает указанный счётчик на 1
        4. Сохраняет изменения
    
    Пример использования:
        await increment_global_stat('event_count')  # Увеличить счётчик созданных событий
    """
    today = date.today()
    
    # Получаем или создаём запись статистики за сегодняшний день
    stat, _ = BotStatistics.objects.get_or_create(
        date=today,
        defaults={
            'user_count': 0,
            'event_count': 0,
            'edited_events': 0,
            'cancelled_events': 0,
        }
    )
    
    # Увеличиваем указанный счётчик на 1
    setattr(stat, field, getattr(stat, field) + 1)
    stat.save()


# ==================== ПЕРСОНАЛЬНАЯ СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ ====================

@sync_to_async
def increment_user_stat(user_id: int, field: str):
    """
    Увеличивает персональную статистику конкретного пользователя.
    
    Эта функция работает с моделью UserStatistics и собирает статистику
    по действиям конкретного пользователя.
    
    Аргументы:
        user_id (int): Telegram ID пользователя
        field (str): Поле для увеличения счётчика.
                    Допустимые значения: 'created_events', 'edited_events',
                    'cancelled_events'
    
    Логика работы:
        1. Получает или создаёт UserProfile по telegram_id
        2. Получает или создаёт UserStatistics для этого пользователя
        3. Увеличивает указанный счётчик на 1
        4. Сохраняет изменения
    
    Пример использования:
        await increment_user_stat(123456789, 'created_events')
    """
    # Получаем или создаём профиль пользователя по Telegram ID
    profile, _ = UserProfile.objects.get_or_create(telegram_id=user_id)
    
    # Получаем или создаём запись статистики для этого пользователя
    stat, _ = UserStatistics.objects.get_or_create(user_telegram_id=profile)
    
    # Увеличиваем указанный счётчик на 1
    setattr(stat, field, getattr(stat, field) + 1)
    stat.save()


# ==================== УНИВЕРСАЛЬНЫЕ ФУНКЦИИ ====================

async def increment_stat(field: str, user_id: Optional[int] = None):
    """
    Универсальная асинхронная функция для увеличения статистики.
    
    Эта функция объединяет логику увеличения как глобальной, так и персональной статистики.
    
    Аргументы:
        field (str): Поле для увеличения счётчика.
                    Допустимые значения: 'user_count', 'event_count',
                    'edited_events', 'cancelled_events'
        user_id (Optional[int]): Telegram ID пользователя (необязательный).
                                Если указан, увеличивается также персональная статистика.
    
    Логика работы:
        1. Всегда увеличивает глобальную статистику
        2. Если указан user_id и поле относится к событиям - увеличивает персональную статистику
    
    Примеры использования:
        await increment_stat('user_count')  # Только глобальная статистика
        await increment_stat('event_count', 123456789)  # Глобальная + персональная
    """
    # Сначала всегда увеличиваем глобальную статистику
    await increment_global_stat(field)

    # Если указан user_id и поле относится к событиям - увеличиваем персональную статистику
    if user_id and field in ('event_count', 'edited_events', 'cancelled_events'):
        # Сопоставление полей глобальной статистики с полями персональной статистики
        user_field_mapping = {
            'event_count': 'created_events',      # Создание события -> created_events
            'edited_events': 'edited_events',     # Редактирование события -> edited_events
            'cancelled_events': 'cancelled_events' # Отмена события -> cancelled_events
        }
        
        # Получаем соответствующее поле для персональной статистики
        user_field = user_field_mapping[field]
        
        # Увеличиваем персональную статистику
        await increment_user_stat(user_id, user_field)


async def get_user_stats(user_id: int) -> str:
    """
    Получает и форматирует персональную статистику пользователя для отображения.
    
    Аргументы:
        user_id (int): Telegram ID пользователя
    
    Возвращает:
        str: Отформатированная строка с статистикой пользователя в виде красивого сообщения.
             Если пользователь не найден - возвращает сообщение об отсутствии статистики.
    
    Формат возвращаемого сообщения:
        📊 Ваша личная статистика:
        
        📅 Создано событий: **X**
        ✏️ Отредактировано событий: **Y**
        ❌ Отменено событий: **Z**
    
    Пример использования:
        stats_message = await get_user_stats(123456789)
        await bot.send_message(chat_id, stats_message)
    """
    try:
        # Получаем статистику пользователя с предзагрузкой связанных данных
        # для оптимизации запросов к базе данных
        stat = await sync_to_async(UserStatistics.objects.select_related('user_telegram_id').get)(
            user_telegram_id__telegram_id=user_id
        )
        
        # Формируем красивое сообщение со статистикой
        return (
            f"📊 Ваша личная статистика:\n\n"
            f"📅 Создано событий: **{stat.created_events}**\n"
            f"✏️ Отредактировано событий: **{stat.edited_events}**\n"
            f"❌ Отменено событий: **{stat.cancelled_events}**"
        )
    except UserStatistics.DoesNotExist:
        # Если статистика не найдена - возвращаем сообщение об отсутствии данных
        return "📊 У вас пока нет личной статистики (ещё не создано событий)"