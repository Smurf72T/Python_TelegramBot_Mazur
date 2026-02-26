from django.contrib import admin
from .models import Event, BotStatistics, Appointment


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'name', 'event_date', 'event_time', 'details')
    list_filter = ('event_date', 'user_id')
    search_fields = ('name', 'details')
    ordering = ('-event_date', '-event_time')


@admin.register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'user_count',
        'event_count',
        'edited_events',
        'cancelled_events',
    )
    list_filter = ('date',)
    readonly_fields = ('date', 'user_count', 'event_count', 'edited_events', 'cancelled_events')
    ordering = ('-date',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'organizer', 'participant_telegram_id', 'status', 'date', 'time')
    list_filter = ('status', 'date', 'organizer')
    search_fields = ('event__name', 'details')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)