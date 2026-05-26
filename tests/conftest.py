import pytest
import sys
import os
from django.test import AsyncClient
from events.models import UserProfile, Event

# Добавляем пути для импорта модулей
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DJANGO_PATH = os.path.join(BASE_DIR, 'django-admin-panel')
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if DJANGO_PATH not in sys.path:
    sys.path.insert(0, DJANGO_PATH)

# Настраиваем Django перед импортом моделей
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')

import django
django.setup()

@pytest.fixture
async def async_client():
    return AsyncClient()

@pytest.fixture
def calendar():
    from notes_bot.calendar_functions import Calendar
    return Calendar()

@pytest.fixture
def user_profile():
    """Создаёт тестового пользователя в БД"""
    profile = UserProfile.objects.create(
        telegram_id=999999999,
        username="testuser"
    )
    return profile

@pytest.fixture
def event(user_profile):
    """Создаёт тестовое событие"""
    event = Event.objects.create(
        user=user_profile,
        name="Тестовое событие",
        event_date="2026-03-01",
        event_time="15:00:00",
        details="Описание теста"
    )
    return event