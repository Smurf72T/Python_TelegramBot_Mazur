import pytest
from events.models import UserProfile, Event

@pytest.mark.django_db
def test_user_registration():
    """Тест создания пользователя через Django ORM"""
    profile = UserProfile.objects.create(
        telegram_id=777777777,
        username="test_user"
    )
    assert profile.telegram_id == 777777777
    assert profile.username == "test_user"

@pytest.mark.django_db
def test_event_creation():
    """Тест создания события через Django ORM"""
    user_profile = UserProfile.objects.create(
        telegram_id=999999999,
        username="event_tester"
    )
    
    event = Event.objects.create(
        user=user_profile,
        name="Тестовое событие",
        event_date="2026-03-01",
        event_time="15:00:00",
        details="Описание теста"
    )
    
    assert event.name == "Тестовое событие"
    assert event.user.telegram_id == user_profile.telegram_id
