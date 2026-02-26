from django.contrib import admin
from .models import Event, BotStatistics


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