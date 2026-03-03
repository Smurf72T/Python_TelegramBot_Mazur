"""
Модуль моделей приложения событий (заглушка обратной совместимости).

Этот файл поддерживает обратную совместимость с предыдущей версией проекта,
где все модели находились в одном файле. Теперь он перенаправляет импорты
в соответствующие модули в поддиректории models.
"""

# Импорт моделей из модульной структуры
from .models.event import Event
from .models.bot_statistics import BotStatistics
from .models.appointment import Appointment
from .models.user_profile import UserProfile
from .models.user_statistics import UserStatistics

# Экспорт всех моделей для поддержки from .models import *
__all__ = [
    'Event',
    'BotStatistics',
    'Appointment',
    'UserProfile',
    'UserStatistics'
]


def __getattr__(name):
    """
    Поддержка строковых ссылок на модели (например, 'events.Event').
    
    Django использует sys.modules для разрешения строковых зависимостей
    в миграциях и ForeignKey. Эта функция обеспечивает совместимость.
    """
    import importlib
    
    models_map = {
        'Event': Event,
        'BotStatistics': BotStatistics,
        'Appointment': Appointment,
        'UserProfile': UserProfile,
        'UserStatistics': UserStatistics,
    }
    
    if name in models_map:
        return models_map[name]
    
    # Поддержка разрешения через importlib как fallback
    try:
        return importlib.import_module(f'.models.{name.lower()}', __package__).__dict__[name]
    except (ImportError, KeyError):
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
