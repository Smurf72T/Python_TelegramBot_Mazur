from django.contrib import admin
from .models import Event, BotStatistics, Appointment, UserProfile, UserStatistics


# ─── Inline для событий пользователя ────────────────────────────────
class EventInline(admin.TabularInline):
    model = Event
    extra = 0
    fields = ('name', 'event_date', 'event_time', 'details')
    readonly_fields = ('event_date', 'event_time')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request, '_userprofile_inline_parent'):
            parent = request._userprofile_inline_parent
            return qs.filter(user_id=parent.telegram_id)
        return qs.none()

    def get_formset(self, request, obj=None, **kwargs):
        request._userprofile_inline_parent = obj
        return super().get_formset(request, obj, **kwargs)


class UserStatisticsInline(admin.StackedInline):
    model = UserStatistics
    extra = 0
    can_delete = False
    fields = ('created_events', 'edited_events', 'cancelled_events', 'updated_at')
    readonly_fields = ('created_events', 'edited_events', 'cancelled_events', 'updated_at')
    max_num = 1


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'registered_at')
    search_fields = ('username', 'telegram_id')
    ordering = ('-registered_at',)
    inlines = [EventInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('events')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'name', 'event_date', 'event_time', 'is_public')
    list_filter = ('event_date', 'user_id', 'is_public')
    search_fields = ('name', 'details')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'organizer_id', 'participant_telegram_id', 'status')
    list_filter = ('status', 'date')


@admin.register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'user_count', 'event_count', 'edited_events', 'cancelled_events')
    readonly_fields = ('date', 'user_count', 'event_count', 'edited_events', 'cancelled_events')


@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        'get_username',
        'created_events',
        'edited_events',
        'cancelled_events',
        'updated_at'
    )
    readonly_fields = ('created_events', 'edited_events', 'cancelled_events', 'updated_at')
    search_fields = ('user_telegram_id__telegram_id', 'user_telegram_id__username')
    ordering = ('-updated_at',)

    def get_user_telegram_id(self, obj):
        return obj.user_telegram_id.telegram_id if obj.user_telegram_id else "—"

    get_user_telegram_id.short_description = "Telegram ID"

    def get_username(self, obj):
        return obj.user_telegram_id.username if obj.user_telegram_id and obj.user_telegram_id.username else f"tg:{obj.user_telegram_id.telegram_id}"

    get_username.short_description = "Пользователь"