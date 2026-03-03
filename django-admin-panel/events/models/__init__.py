"""
Модуль моделей приложения событий.

Этот пакет содержит все модели Django для приложения events,
разделённые по тематическим файлам для лучшей организации кода.
"""

from .event import Event
from .bot_statistics import BotStatistics
from .appointment import Appointment
from .user_profile import UserProfile
from .user_statistics import UserStatistics

__all__ = [
    'Event',
    'BotStatistics',
    'Appointment',
    'UserProfile',
    'UserStatistics'
]