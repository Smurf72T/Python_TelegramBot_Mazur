from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from events.views import (
    UserProfileViewSet,
    EventViewSet,
    BotStatisticsViewSet,
    UserStatisticsViewSet,
    AppointmentViewSet,
    export_events,
    export_events_json
)

router = DefaultRouter()
router.register(r'api/users', UserProfileViewSet)
router.register(r'api/events', EventViewSet)
router.register(r'api/botstats', BotStatisticsViewSet)
router.register(r'api/userstats', UserStatisticsViewSet)
router.register(r'api/appointments', AppointmentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('export/events/', export_events, name='export_events'),
    path('export/events/json/', export_events_json, name='export_events_json'),
    path('', include(router.urls)),
]