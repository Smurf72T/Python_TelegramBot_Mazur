from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'name', 'event_date', 'event_time', 'details')
    list_filter = ('event_date', 'user_id')
    search_fields = ('name', 'details')
    ordering = ('-event_date', '-event_time')