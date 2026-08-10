"""
Тесты фасадного класса Calendar и ORM-слоя данных бота.

Проверяют регистрацию пользователей, CRUD событий, встречи (appointments),
публичные события и статистику через Django ORM.
"""

import pytest
from asgiref.sync import sync_to_async

from events.models import UserProfile, Event, Appointment, BotStatistics

from notes_bot.calendar_functions import Calendar
from notes_bot.statistics import increment_stat, get_user_stats


@pytest.fixture
def calendar():
    return Calendar()


@pytest.mark.django_db
def test_register_user(calendar):
    result = calendar.register_user(777000001, "newuser")
    assert "зарегистрированы" in result.lower()

    profile = UserProfile.objects.get(telegram_id=777000001)
    assert profile.username == "newuser"


@pytest.mark.django_db
def test_register_user_duplicate(calendar):
    calendar.register_user(777000002, "existing")
    result = calendar.register_user(777000002, "renamed")
    assert "зарегистрированы" in result.lower()

    # Существующий профиль не перезаписывается насильно
    assert UserProfile.objects.filter(telegram_id=777000002).count() == 1


@pytest.mark.django_db
def test_create_and_list_events(calendar):
    user_id = 777000003
    calendar.register_user(user_id, "user3")

    result = calendar.create_event(user_id, "Встреча с командой", "2027-01-10", "10:30", "Обсуждение")
    assert "создано" in result.lower()

    listed = calendar.list_events(user_id)
    assert "Встреча с командой" in listed

    event = Event.objects.filter(user_id=user_id).first()
    assert event is not None
    assert event.is_public is False


@pytest.mark.django_db
def test_create_event_invalid_format(calendar):
    result = calendar.create_event(777000004, "Битый формат", "10/01/2027", "10:30")
    assert "Неверный формат" in result


@pytest.mark.django_db
def test_edit_event(calendar):
    user_id = 777000005
    calendar.register_user(user_id, "user5")
    calendar.create_event(user_id, "Старое имя", "2027-02-01", "09:00")

    event = Event.objects.get(user_id=user_id)
    result = calendar.edit_event(user_id, str(event.id), name="Новое имя")
    assert "обновлено" in result.lower()

    event.refresh_from_db()
    assert event.name == "Новое имя"


@pytest.mark.django_db
def test_delete_event_ownership(calendar):
    owner = 777000006
    other = 777000007
    calendar.register_user(owner, "owner")
    calendar.register_user(other, "other")
    calendar.create_event(owner, "Личное", "2027-03-01", "12:00")

    event = Event.objects.get(user_id=owner)

    # Чужой пользователь не может удалить
    result = calendar.delete_event(other, str(event.id))
    assert "не принадлежит" in result.lower()
    assert Event.objects.filter(id=event.id).exists()

    # Владелец может удалить
    result = calendar.delete_event(owner, str(event.id))
    assert "удалено" in result.lower()
    assert not Event.objects.filter(id=event.id).exists()


@pytest.mark.django_db
def test_appointment_flow(calendar):
    organizer = 777000008
    participant = 777000009
    calendar.register_user(organizer, "organizer")
    calendar.register_user(participant, "participant")

    calendar.create_event(organizer, "Событие для встречи", "2027-04-01", "14:00")
    event = Event.objects.get(user_id=organizer)

    result = calendar.create_appointment(organizer, event.id, participant, "Перезвонить")
    assert "успешно отправлено" in result.lower()

    appointment = Appointment.objects.get(event=event, participant_telegram_id=participant)
    assert appointment.status == "pending"
    assert appointment.organizer_telegram_id == organizer

    # Подтверждение участником
    result = calendar.update_appointment_status(appointment.id, participant, "confirmed")
    assert "обновлен" in result.lower()
    appointment.refresh_from_db()
    assert appointment.status == "confirmed"

    # Недопустимый статус
    result = calendar.update_appointment_status(appointment.id, participant, "invalid")
    assert "Недопустимый статус" in result


@pytest.mark.django_db
def test_appointment_requires_registered_participant(calendar):
    organizer = 777000010
    calendar.register_user(organizer, "organizer")
    calendar.create_event(organizer, "Ещё событие", "2027-05-01", "16:00")
    event = Event.objects.get(user_id=organizer)

    result = calendar.create_appointment(organizer, event.id, 777099999, "")
    assert "не зарегистрирован" in result.lower()


@pytest.mark.django_db
def test_public_events(calendar):
    user_a = 777000011
    user_b = 777000012
    calendar.register_user(user_a, "userA")
    calendar.register_user(user_b, "userB")
    calendar.create_event(user_a, "Публичное событие", "2027-06-01", "11:00")
    event = Event.objects.get(user_id=user_a)

    # Сделать публичным
    result = calendar.toggle_public(user_a, str(event.id))
    assert "публичным" in result.lower()
    event.refresh_from_db()
    assert event.is_public is True

    # Другой пользователь видит его в списке
    public_text = calendar.get_public_events(user_b)
    assert "Публичное событие" in public_text

    # Свой список не содержит собственного события
    own_text = calendar.get_public_events(user_a)
    assert "Публичное событие" not in own_text


@pytest.mark.django_db
def test_statistics_increment():
    user_id = 777000013
    increment_stat("event_count", user_id)
    increment_stat("event_count", user_id)
    increment_stat("edited_events", user_id)

    stats_text = get_user_stats(user_id)
    assert "Создано событий" in stats_text

    stat = BotStatistics.objects.filter(date=__import__("datetime").date.today()).first()
    assert stat is not None
    assert stat.event_count == 2
