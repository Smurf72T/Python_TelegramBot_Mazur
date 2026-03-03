import pytest
from asgiref.sync import sync_to_async
from notes_bot.calendar_functions import Calendar

@pytest.mark.django_db
async def test_register_user():
    cal = Calendar()
    result = await sync_to_async(cal.register_user)(777777777, "testbot")
    assert "успешно зарегистрированы" in result.lower()

    from events.models import UserProfile
    profile = await sync_to_async(UserProfile.objects.get)(telegram_id=777777777)
    assert profile is not None

@pytest.mark.django_db
async def test_create_event(user_profile):
    cal = Calendar()
    result = await sync_to_async(cal.create_event)(
        user_profile.telegram_id,
        "Тестовое событие",
        "2026-03-01",
        "15:00",
        "Описание"
    )
    assert "создано" in result.lower()

    from events.models import Event
    event = await sync_to_async(Event.objects.filter)(user_id=user_profile.telegram_id).afirst()
    assert event is not None
    assert event.name == "Тестовое событие"