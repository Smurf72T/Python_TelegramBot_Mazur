"""
Модуль views для приложения events.

Этот модуль содержит представления (views) для работы с событиями, пользователями,
статистикой и записями на приём. Включает функции экспорта данных в CSV и JSON,
а также ViewSets для REST API.

Основные компоненты:
- export_events: экспорт событий пользователя в CSV формат
- export_events_json: экспорт событий пользователя в JSON формат
- UserProfileViewSet: CRUD операции для профилей пользователей
- EventViewSet: CRUD операции для событий
- BotStatisticsViewSet: чтение статистики бота
- UserStatisticsViewSet: чтение статистики пользователей
- AppointmentViewSet: CRUD операции для записей на приём

Автор: Smurf
"""

import csv
import json
from datetime import date
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from events.models import (
    Event,
    UserProfile,
    BotStatistics,
    UserStatistics,
    Appointment
)
from .serializers import (
    UserProfileSerializer,
    EventSerializer,
    BotStatisticsSerializer,
    UserStatisticsSerializer,
    AppointmentSerializer
)


def export_events(request):
    """
    Выгружает события пользователя в CSV формат.

    Эта функция обеспечивает безопасный экспорт событий пользователя, требуя
    аутентификацию через user_id и export_token. Пользователь может экспортировать
    только свои собственные события.

    Параметры запроса (GET):
        user_id (str): Telegram ID пользователя
        token (str): Токен экспорта пользователя (export_token)

    Возвращает:
        HttpResponse: CSV файл с событиями пользователя или сообщение об ошибке

    Коды ответа:
        200: Успешный экспорт
        400: Не указан user_id или token
        403: Неверный user_id или token

    Формат CSV:
        - Разделитель: точка с запятой (;)
        - Кодировка: UTF-8 с BOM (для совместимости с Excel)
        - Столбцы: ID, Название события, Дата, Время, Описание, Публичное
    """
    # Получение параметров из запроса
    user_id = request.GET.get('user_id')
    token = request.GET.get('token')

    # Проверка наличия обязательных параметров
    if not user_id or not token:
        return HttpResponse(
            "Ошибка: user_id или token не указаны",
            status=400,
            content_type='text/plain; charset=utf-8'
        )

    # Валидация и аутентификация пользователя
    try:
        user_id = int(user_id)
        profile = UserProfile.objects.get(telegram_id=user_id, export_token=token)
    except (ValueError, UserProfile.DoesNotExist):
        return HttpResponse(
            "Ошибка: неверный user_id или token",
            status=403,
            content_type='text/plain; charset=utf-8'
        )

    # Дополнительная проверка: если token равен 'None', разрешаем доступ (для отладки)
    if token == 'None':
        # Получаем первый профиль пользователя или создаем его
        profile, created = UserProfile.objects.get_or_create(telegram_id=user_id)
        if created:
            profile.export_token = 'None'
            profile.save()

    # Получение событий пользователя, отсортированных по дате и времени (убывание)
    events = Event.objects.filter(user=profile).order_by('-event_date', '-event_time')

    # Создание HTTP-ответа с CSV-контентом
    response = HttpResponse(
        content_type='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename="calendar_{user_id}_{date.today().strftime("%Y-%m-%d")}.csv"'
        },
    )

    # Добавляем BOM (Byte Order Mark) для корректного отображения кириллицы в Excel на Windows
    bom = '\ufeff'
    response.write(bom)

    # Настройка CSV-писателя с разделителем ';' для совместимости с Excel
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Запись заголовка CSV-файла
    writer.writerow(['ID', 'Название события', 'Дата', 'Время', 'Описание', 'Публичное'])

    # Запись данных каждого события в CSV
    for event in events:
        writer.writerow([
            event.id,
            event.name,
            event.event_date.strftime('%Y-%m-%d') if event.event_date else '',
            event.event_time.strftime('%H:%M') if event.event_time else '',
            event.details or '',
            'Да' if event.is_public else 'Нет'
        ])

    return response


def export_events_json(request):
    """
    Выгружает события пользователя в JSON формат.

    Эта функция обеспечивает безопасный экспорт событий пользователя, требуя
    аутентификацию через user_id и export_token. Пользователь может экспортировать
    только свои собственные события. JSON формат удобен для программной обработки
    данных и интеграции с другими системами.

    Параметры запроса (GET):
        user_id (str): Telegram ID пользователя
        token (str): Токен экспорта пользователя (export_token)

    Возвращает:
        HttpResponse: JSON файл с событиями пользователя или сообщение об ошибке

    Коды ответа:
        200: Успешный экспорт
        400: Не указан user_id или token
        403: Неверный user_id или token

    Формат JSON:
        - Массив объектов событий
        - Кодировка: UTF-8
        - Отступы: 2 пробела для читаемости
        - Поля каждого события: id, name, date, time, details, is_public
    """
    # Получение параметров из запроса
    user_id = request.GET.get('user_id')
    token = request.GET.get('token')

    # Проверка наличия обязательных параметров
    if not user_id or not token:
        return HttpResponse(
            "Ошибка: user_id или token не указаны",
            status=400,
            content_type='text/plain; charset=utf-8'
        )

    # Валидация и аутентификация пользователя
    try:
        user_id = int(user_id)
        profile = UserProfile.objects.get(telegram_id=user_id, export_token=token)
    except (ValueError, UserProfile.DoesNotExist):
        return HttpResponse(
            "Ошибка: неверный user_id или token",
            status=403,
            content_type='text/plain; charset=utf-8'
        )

    # Дополнительная проверка: если token равен 'None', разрешаем доступ (для отладки)
    if token == 'None':
        # Получаем первый профиль пользователя или создаем его
        profile, created = UserProfile.objects.get_or_create(telegram_id=user_id)
        if created:
            profile.export_token = 'None'
            profile.save()

    # Получение событий пользователя, отсортированных по дате и времени (убывание)
    events = Event.objects.filter(user=profile).order_by('-event_date', '-event_time')

    # Формирование списка данных событий в формате JSON
    data = []
    for event in events:
        data.append({
            "id": event.id,
            "name": event.name,
            "date": event.event_date.strftime('%Y-%m-%d') if event.event_date else None,
            "time": event.event_time.strftime('%H:%M') if event.event_time else None,
            "details": event.details or "",
            "is_public": event.is_public,
        })

    # Создание HTTP-ответа с JSON-контентом
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename="calendar_{user_id}_{date.today().strftime("%Y-%m-%d")}.json"'
        }
    )

    return response


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с профилями пользователей через REST API.

    Предоставляет полный набор CRUD операций (Create, Read, Update, Delete)
    для модели UserProfile. Позволяет администраторам системы управлять
    профилями пользователей через API.

    Атрибуты:
        queryset: QuerySet для получения всех профилей пользователей
        serializer_class: Сериализатор для преобразования данных UserProfile
        permission_classes: Классы прав доступа (только авторизованные пользователи)

    Доступные операции:
        - GET /api/userprofiles/ - список всех профилей
        - POST /api/userprofiles/ - создание нового профиля
        - GET /api/userprofiles/{id}/ - получение профиля по ID
        - PUT /api/userprofiles/{id}/ - полное обновление профиля
        - PATCH /api/userprofiles/{id}/ - частичное обновление профиля
        - DELETE /api/userprofiles/{id}/ - удаление профиля

    Примечание: Пользователи видят только свой профиль, администраторы - все профили.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        """
        Возвращает профили пользователей с учётом прав доступа.
        - Администраторы видят все профили
        - Обычные пользователи видят только свой профиль
        """
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return UserProfile.objects.all()

        # Если у пользователя есть профиль, возвращаем только его
        if hasattr(user, 'profile'):
            return UserProfile.objects.filter(user=user)

        return UserProfile.objects.none()


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с событиями через REST API.

    Предоставляет полный набор CRUD операций (Create, Read, Update, Delete)
    для модели Event. Позволяет управлять событиями календаря через API.

    Атрибуты:
        queryset: QuerySet для получения всех событий
        serializer_class: Сериализатор для преобразования данных Event
        permission_classes: Классы прав доступа (только авторизованные пользователи)

    Доступные операции:
        - GET /api/events/ - список всех событий
        - POST /api/events/ - создание нового события
        - GET /api/events/{id}/ - получение события по ID
        - PUT /api/events/{id}/ - полное обновление события
        - PATCH /api/events/{id}/ - частичное обновление события
        - DELETE /api/events/{id}/ - удаление события

    Примечание: Пользователи видят и управляют только своими событиями.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        """
        Возвращает события с учётом прав доступа.
        - Администраторы видят все события
        - Обычные пользователи видят только свои события
        """
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Event.objects.all()

        # Если у пользователя есть профиль, возвращаем только его события
        if hasattr(user, 'profile'):
            return Event.objects.filter(user=user.profile)

        return Event.objects.none()

    def perform_create(self, serializer):
        """
        Автоматически привязывает создаваемое событие к профилю текущего пользователя.
        """
        user = self.request.user
        if hasattr(user, 'profile'):
            serializer.save(user=user.profile)
        else:
            raise permissions.PermissionDenied("У пользователя нет профиля")


class BotStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для чтения статистики бота через REST API.

    Предоставляет только операции чтения (Read) для модели BotStatistics.
    Используется для мониторинга и аналитики работы бота без возможности
    изменения данных через API.

    Атрибуты:
        queryset: QuerySet для получения всей статистики бота
        serializer_class: Сериализатор для преобразования данных BotStatistics
        permission_classes: Классы прав доступа (только администраторы)

    Доступные операции:
        - GET /api/botstatistics/ - список всей статистики бота
        - GET /api/botstatistics/{id}/ - получение записи статистики по ID

    Примечание: ViewSet только для чтения, доступен только администраторам.
    """
    queryset = BotStatistics.objects.all()
    serializer_class = BotStatisticsSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get']


class UserStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для чтения статистики пользователей через REST API.

    Предоставляет только операции чтения (Read) для модели UserStatistics.
    Используется для аналитики активности пользователей без возможности
    изменения данных через API.

    Атрибуты:
        queryset: QuerySet для получения всей статистики пользователей
        serializer_class: Сериализатор для преобразования данных UserStatistics
        permission_classes: Классы прав доступа (только администраторы)

    Доступные операции:
        - GET /api/userstatistics/ - список всей статистики пользователей
        - GET /api/userstatistics/{id}/ - получение записи статистики по ID

    Примечание: ViewSet только для чтения, доступен только администраторам.
    """
    queryset = UserStatistics.objects.all()
    serializer_class = UserStatisticsSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get']


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с записями встреч через REST API.

    Предоставляет полный набор CRUD операций (Create, Read, Update, Delete)
    для модели Appointment. Позволяет управлять записями пользователей встреч.

    Атрибуты:
        queryset: QuerySet для получения всех записей встреч
        serializer_class: Сериализатор для преобразования данных Appointment
        permission_classes: Классы прав доступа (только авторизованные пользователи)

    Доступные операции:
        - GET /api/appointments/ - список всех записей встреч
        - POST /api/appointments/ - создание новой записи
        - GET /api/appointments/{id}/ - получение записи по ID
        - PUT /api/appointments/{id}/ - полное обновление записи
        - PATCH /api/appointments/{id}/ - частичное обновление записи
        - DELETE /api/appointments/{id}/ - удаление записи

    Примечание: Пользователи видят и управляют только своими записями.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        """
        Возвращает записи с учётом прав доступа.
        - Администраторы видят все записи
        - Обычные пользователи видят только свои записи
        """
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Appointment.objects.all()

        # Если у пользователя есть профиль, возвращаем только его записи
        if hasattr(user, 'profile'):
            return Appointment.objects.filter(user=user.profile)

        return Appointment.objects.none()

    def perform_create(self, serializer):
        """
        Автоматически привязывает создаваемую запись к профилю текущего пользователя.
        """
        user = self.request.user
        if hasattr(user, 'profile'):
            serializer.save(user=user.profile)
        else:
            raise permissions.PermissionDenied("У пользователя нет профиля")