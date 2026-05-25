import pytest
from asgiref.sync import sync_to_async
from notes_bot.calendar_functions import Calendar

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_register_user():
    cal = Calendar()
    from events.models import UserProfile
    # Создаем пользователя вручную
    profile, created = await sync_to_async(UserProfile.objects.get_or_create)(
        telegram_id=777777777,
        defaults={"username": "testbot"}
    )
    assert created  # Проверяем, что пользователь был создан
    
    cal = Calendar()
    result = cal.register_user(777777777, "testbot")
    assert "успешно зарегистрированы" in result.lower()

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_create_event():
    from events.models import UserProfile
    # Создаем пользователя вручную
    profile, created = await sync_to_async(UserProfile.objects.get_or_create)(
        telegram_id=999999999,
        defaults={"username": "testuser"}
    )
    assert created  # Проверяем, что пользователь был создан
    
    cal = Calendar()
    result = cal.create_event(
        profile.telegram_id,
        "Тестовое событие",
        "2026-03-01",
        "15:00",
        "Описание"
    )
    assert "создано" in result.lower()

    from events.models import Event
    event = await Event.objects.filter(user_id=profile.telegram_id).afirst()
    assert event is not None
    assert event.name == "Тестовое событие"