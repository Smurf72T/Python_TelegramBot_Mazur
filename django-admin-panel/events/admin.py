"""
Модуль администраторского интерфейса для приложения events.

Этот модуль определяет конфигурацию моделей в админ-панели Django,
включая встроенные формы (inlines) и кастомные методы отображения.

Основные классы:
- EventInline: встроенная форма для отображения событий пользователя
- UserStatisticsInline: встроенная форма для статистики пользователя
- UserProfileAdmin: админ-интерфейс для профилей пользователей
- EventAdmin: админ-интерфейс для событий
- AppointmentAdmin: админ-интерфейс для встреч
- BotStatisticsAdmin: админ-интерфейс для статистики бота
- UserStatisticsAdmin: админ-интерфейс для статистики пользователей
"""

from django.contrib import admin
from events.models import Event, BotStatistics, Appointment, UserProfile, UserStatistics


# =============================================================================
# ИНЛАЙНЫ (ВСТРОЕННЫЕ ФОРМЫ)
# =============================================================================

class EventInline(admin.TabularInline):
    """
    Встроенная форма для отображения событий пользователя.
    
    Позволяет просматривать события в контексте страницы профиля пользователя
    без возможности добавления или удаления событий.
    """
    
    model = Event
    extra = 0  # Не добавлять пустые формы для новых событий
    fields = ('name', 'event_date', 'event_time', 'details')  # Поля для отображения
    readonly_fields = ('name', 'event_date', 'event_time', 'details')  # Поля только для чтения
    can_delete = False  # Запрет удаления событий через инлайн
    show_change_link = True  # Показывать ссылку для редактирования события

    def has_add_permission(self, request, obj=None):
        """
        Отключает возможность добавления новых событий через инлайн.

        Args:
            request: HTTP-запрос
            obj: Родительский объект (UserProfile)

        Returns:
            bool: Всегда False - запрет добавления
        """
        return False

    def get_queryset(self, request):
        """
        Возвращает набор событий, отфильтрованных по пользователю.

        Использует временный атрибут request._userprofile_inline_parent,
        установленный в методе get_formset, для фильтрации событий.

        Args:
            request: HTTP-запрос с атрибутом родительского объекта

        Returns:
            QuerySet: События текущего пользователя или пустой QuerySet
        """
        qs = super().get_queryset(request)
        if hasattr(request, '_userprofile_inline_parent'):
            parent = request._userprofile_inline_parent
            return qs.filter(user_id=parent.telegram_id)
        return qs.none()

    def get_formset(self, request, obj=None, **kwargs):
        """
        Устанавливает родительский объект в запрос для использования в get_queryset.

        Args:
            request: HTTP-запрос
            obj: Родительский объект (UserProfile)
            **kwargs: Дополнительные аргументы

        Returns:
            ModelFormSet: Набор форм для отображения
        """
        request._userprofile_inline_parent = obj
        return super().get_formset(request, obj, **kwargs)


class UserStatisticsInline(admin.StackedInline):
    """
    Встроенная форма для отображения статистики пользователя.

    Позволяет просматривать статистику действий пользователя в контексте
    страницы профиля пользователя без возможности редактирования.
    """

    model = UserStatistics
    extra = 0  # Не добавлять пустые формы для новой статистики
    can_delete = False  # Запрет удаления статистики через инлайн
    max_num = 1  # Максимум одна запись статистики на пользователя

    # Поля для отображения (все только для чтения)
    fields = (
        'created_events',
        'edited_events',
        'cancelled_events',
        'updated_at'
    )
    readonly_fields = (
        'created_events',
        'edited_events',
        'cancelled_events',
        'updated_at'
    )

    def has_add_permission(self, request, obj=None):
        """
        Отключает возможность добавления новой статистики через инлайн.

        Статистика формируется автоматически бэкендом, ручное создание
        может привести к дублям и некорректным данным.

        Args:
            request: HTTP-запрос
            obj: Родительский объект (UserProfile)

        Returns:
            bool: Всегда False - запрет добавления
        """
        return False


# =============================================================================
# АДМИН-ИНТЕРФЕЙСЫ МОДЕЛЕЙ
# =============================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для профилей пользователей.

    Предоставляет интерфейс для просмотра и управления профилями пользователей
    с возможностью просмотра связанных событий и статистики.
    """

    # Поля, отображаемые в списке объектов
    list_display = (
        'telegram_id',
        'username',
        'first_name',
        'registered_at'
    )

    # Поля для поиска
    search_fields = ('username', 'telegram_id')

    # Поле для сортировки по умолчанию (новые первыми)
    ordering = ('-registered_at',)

    # Встроенные формы для отображения связанных объектов
    inlines = [EventInline, UserStatisticsInline]

    def get_queryset(self, request):
        """
        Оптимизирует запрос с предварительной загрузкой связанных объектов.

        Использует prefetch_related для предотвращения проблемы N+1 запросов
        при отображении событий и статистики пользователя.

        Args:
            request: HTTP-запрос

        Returns:
            QuerySet: Профили пользователей с предзагруженными связанными объектами
        """
        return super().get_queryset(request).prefetch_related('events', 'statistics')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для событий.

    Предоставляет интерфейс для просмотра и управления событиями
    с фильтрацией и поиском по различным полям.
    """

    # Поля, отображаемые в списке объектов
    list_display = (
        'id',
        'get_user_display',
        'name',
        'event_date',
        'event_time',
        'is_public'
    )

    # Поля для фильтрации в боковой панели
    list_filter = ('event_date', 'is_public')

    # Поля для поиска
    search_fields = ('name', 'details', 'user__username', 'user__telegram_id')

    # Оптимизация запросов - предварительная загрузка связанных пользователей
    list_select_related = ('user',)

    def get_user_display(self, obj):
        """
        Возвращает отображаемое имя пользователя для события.

        Если у пользователя есть username, возвращает его, иначе возвращает
        Telegram ID в формате "tg:{id}".

        Args:
            obj: Объект Event

        Returns:
            str: Username пользователя или форматированный Telegram ID
        """
        if hasattr(obj, 'user') and obj.user:
            if obj.user.username:
                return obj.user.username
            return f"tg:{obj.user.telegram_id}"
        return f"ID: {obj.user_id}"

    # Человеко-понятное название для колонки
    get_user_display.short_description = "Пользователь"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для встреч.

    Предоставляет интерфейс для просмотра и управления встречами
    с фильтрацией по статусу и дате.
    """

    # Поля, отображаемые в списке объектов
    list_display = (
        'id',
        'event',
        'organizer_telegram_id',
        'participant_telegram_id',
        'status'
    )

    # Поля для фильтрации в боковой панели
    list_filter = ('status', 'date')

    # Поля для поиска
    search_fields = ('event__name', 'organizer_telegram_id', 'participant_telegram_id')


@admin.register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для общей статистики бота.

    Предоставляет интерфейс для просмотра статистики использования бота
    за определённую дату. Все поля только для чтения.
    """

    # Поля, отображаемые в списке объектов
    list_display = (
        'date',
        'user_count',
        'event_count',
        'edited_events',
        'cancelled_events'
    )

    # Поля только для чтения (статистика формируется автоматически)
    readonly_fields = (
        'date',
        'user_count',
        'event_count',
        'edited_events',
        'cancelled_events'
    )

    # Поля для поиска
    search_fields = ('date',)

    # Поле для сортировки по умолчанию (новые даты первыми)
    ordering = ('-date',)


@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для персональной статистики пользователей.

    Предоставляет интерфейс для просмотра статистики действий каждого пользователя.
    Все поля только для чтения, так как статистика обновляется автоматически.
    """

    # Поля, отображаемые в списке объектов
    list_display = (
        'get_username',
        'created_events',
        'edited_events',
        'cancelled_events',
        'updated_at'
    )

    # Поля только для чтения (статистика формируется автоматически)
    readonly_fields = (
        'created_events',
        'edited_events',
        'cancelled_events',
        'updated_at'
    )

    # Поля для поиска (по связанному пользователю)
    search_fields = ('user_telegram_id__telegram_id', 'user_telegram_id__username')

    # Поле для сортировки по умолчанию (недавно обновлённые первыми)
    ordering = ('-updated_at',)

    # Оптимизация запросов - предварительная загрузка связанных пользователей
    list_select_related = ('user_telegram_id',)

    def get_username(self, obj):
        """
        Возвращает имя пользователя (username или Telegram ID).

        Если username существует, возвращает его, иначе возвращает
        Telegram ID в формате "tg:{id}".

        Args:
            obj: Объект UserStatistics

        Returns:
            str: Username пользователя или форматированный Telegram ID
        """
        if obj.user_telegram_id and obj.user_telegram_id.username:
            return obj.user_telegram_id.username
        return f"tg:{obj.user_telegram_id.telegram_id}" if obj.user_telegram_id else "—"

    # Человеко-понятное название для колонки
    get_username.short_description = "Пользователь"

    def has_add_permission(self, request):
        """
        Отключает возможность добавления новой статистики вручную.

        Статистика формируется автоматически бэкендом, ручное создание
        может привести к некорректным данным.

        Args:
            request: HTTP-запрос

        Returns:
            bool: Всегда False - запрет добавления
        """
        return False