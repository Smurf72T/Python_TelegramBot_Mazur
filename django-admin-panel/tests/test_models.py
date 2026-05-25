import pytest
from events.models import UserProfile, Event, UserStatistics

@pytest.mark.django_db
def test_user_profile_creation():
    profile = UserProfile.objects.create(telegram_id=123456789, username="smurf")
    assert profile.telegram_id == 123456789
    assert str(profile) == "@smurf (tg:123456789)" or "tg:123456789"

@pytest.mark.django_db
def test_event_creation(user_profile):
    event = Event.objects.create(
        user=user_profile,
        name="Встреча",
        event_date="2026-03-01",
        event_time="14:00:00"
    )
    assert event.name == "Встреча"
    assert event.user.telegram_id == user_profile.telegram_id

@pytest.mark.django_db
def test_user_statistics_creation(user_profile):
    stats = UserStatistics.objects.create(user_telegram_id=user_profile)
    assert stats.created_events == 0
    assert stats.user_telegram_id.telegram_id == user_profile.telegram_id