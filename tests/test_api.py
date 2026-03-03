import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_api_events_list():
    client = APIClient()
    response = client.get('/api/events/')
    assert response.status_code in (200, 401)  # 401 если нет аутентификации