import csv
from django.http import HttpResponse
from .models import Event


def export_events(request):
    """Выгружает события пользователя в CSV. Только свои события."""
    user_id = request.GET.get('user_id')

    if not user_id:
        return HttpResponse("Ошибка: не указан user_id", status=400)

    try:
        user_id = int(user_id)
    except ValueError:
        return HttpResponse("Ошибка: неверный user_id", status=400)

    # Важно: выгружаем ТОЛЬКО события этого пользователя
    events = Event.objects.filter(user_id=user_id).order_by('-event_date', '-event_time')

    # Создаём HTTP-ответ с заголовком для скачивания файла
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="my_calendar_events_{user_id}.csv"'
        },
    )

    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Заголовки CSV
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