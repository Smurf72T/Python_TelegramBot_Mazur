import pytest
from django.test import RequestFactory
from events.views import export_events, export_events_json
from events.models import UserProfile, Event

@pytest.mark.django_db
def test_export_csv(user_profile):
    # Создаём тестовое событие
    Event.objects.create(
        user=user_profile,
        name="Экспорт тест",
        event_date="2026-03-01",
        event_time="12:00:00"
    )

    factory = RequestFactory()
    request = factory.get(f'/export/events/?user_id={user_profile.telegram_id}&token={user_profile.export_token}')
    response = export_events(request)

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'
    assert 'calendar_' in response['Content-Disposition']
    assert 'Экспорт тест'.encode('utf-8') in response.content  # проверяем, что событие попало в CSV