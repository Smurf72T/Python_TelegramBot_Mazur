from django.contrib import admin
from django.urls import path

from events.views import export_events

urlpatterns = [
    path('admin/', admin.site.urls),
    path('export/events/', export_events, name='export_events'),   # ← новая строка
]