import csv
import json
from datetime import date
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Event, UserProfile, BotStatistics, UserStatistics, Appointment
from .serializers import (
    UserProfileSerializer,
    EventSerializer,
    BotStatisticsSerializer,
    UserStatisticsSerializer,
    AppointmentSerializer
)


def export_events(request):
    """Выгружает события пользователя в CSV. Только свои события."""
    user_id = request.GET.get('user_id')
    token = request.GET.get('token')

    if not user_id or not token:
        return HttpResponse("Ошибка: user_id или token не указаны", status=400)

    try:
        user_id = int(user_id)
        profile = UserProfile.objects.get(telegram_id=user_id, export_token=token)
    except (ValueError, UserProfile.DoesNotExist):
        return HttpResponse("Ошибка: неверный user_id или token", status=403)

    events = Event.objects.filter(user=profile).order_by('-event_date', '-event_time')

    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="calendar_{user_id}_{date.today().strftime("%Y-%m-%d")}.csv"'
        },
    )

    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['ID', 'Название события', 'Дата', 'Время', 'Описание', 'Публичное'])

    for event in events:
        writer.writerow([
            event.id,
            event.name,
            event.event_date,
            event.event_time,
            event.details or '',
            'Да' if event.is_public else 'Нет'
        ])

    return response


def export_events_json(request):
    """Выгружает события пользователя в JSON. Только свои события."""
    user_id = request.GET.get('user_id')
    token = request.GET.get('token')

    if not user_id or not token:
        return HttpResponse("Ошибка: user_id или token не указаны", status=400, content_type='text/plain')

    try:
        user_id = int(user_id)
        profile = UserProfile.objects.get(telegram_id=user_id, export_token=token)
    except (ValueError, UserProfile.DoesNotExist):
        return HttpResponse("Ошибка: неверный user_id или token", status=403, content_type='text/plain')

    events = Event.objects.filter(user=profile).order_by('-event_date', '-event_time')

    data = []
    for event in events:
        data.append({
            "id": event.id,
            "name": event.name,
            "date": str(event.event_date),
            "time": str(event.event_time),
            "details": event.details or "",
            "is_public": event.is_public,
        })

    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json',
        headers={
            'Content-Disposition': f'attachment; filename="calendar_{user_id}_{date.today().strftime("%Y-%m-%d")}.json"'
        }
    )

    return response


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class BotStatisticsViewSet(viewsets.ReadOnlyModelViewSet):   # только чтение
    queryset = BotStatistics.objects.all()
    serializer_class = BotStatisticsSerializer


class UserStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserStatistics.objects.all()
    serializer_class = UserStatisticsSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer