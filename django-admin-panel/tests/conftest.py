import pytest
import asyncio
import sys
import os
from asgiref.sync import sync_to_async
from django.test import AsyncClient
from events.models import UserProfile, Event

# Добавляем путь к django-admin-panel для импорта admin_panel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'django-admin-panel'))

# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Здесь можно создать тестовые данные
        pass

@pytest.fixture
async def async_client():
    return AsyncClient()

@pytest.fixture
def calendar():
    from notes_bot.calendar_functions import Calendar
    return Calendar()

@pytest.fixture
def user_profile():
    """Создаёт тестового пользователя"""
    profile, _ = UserProfile.objects.get_or_create(
        telegram_id=999999999,
        defaults={"username": "testuser"}
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