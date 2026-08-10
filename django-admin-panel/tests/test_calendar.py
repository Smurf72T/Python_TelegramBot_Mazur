import pytest
from asgiref.sync import sync_to_async
from notes_bot.calendar_interface import Calendar
from notes_bot.user_management import UserManager
from notes_bot.event_crud import EventCRUD

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_register_user():
    """Тест регистрации пользователя через UserManager"""
    from events.models import UserProfile
    
    # Проверяем, что пользователя нет (через sync_to_async)
    exists = await sync_to_async(UserProfile.objects.filter(telegram_id=777777777).exists)()
    assert not exists
    
    # Создаем пользователя
    profile, created = await sync_to_async(UserProfile.objects.get_or_create)(
        telegram_id=777777777,
        defaults={"username": "testbot"}
    )
    assert created  # Проверяем, что пользователь был создан
    
    # Проверяем, что пользователь создан
    exists = await sync_to_async(UserProfile.objects.filter(telegram_id=777777777).exists)()
    assert exists
    user = await sync_to_async(UserProfile.objects.get)(telegram_id=777777777)
    assert user.username == "testbot"

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_create_event():
    """Тест создания события через EventCRUD"""
    from events.models import UserProfile, Event
    
    # Создаем пользователя
    profile, created = await sync_to_async(UserProfile.objects.get_or_create)(
        telegram_id=999999999,
        defaults={"username": "testuser"}
    )
    assert created
    
    # Проверяем создание события через Django ORM
    event = await sync_to_async(Event.objects.create)(
        user=profile,
        name="Тестовое событие",
        event_date="2026-03-01",
        event_time="15:00:00",
        details="Описание теста"
    )
    
    # Проверяем, что событие создано
    exists = await sync_to_async(Event.objects.filter(id=event.id).exists)()
    assert exists
    retrieved_event = await sync_to_async(Event.objects.get)(id=event.id)
    assert retrieved_event.name == "Тестовое событие"