from rest_framework import serializers
from .models import UserProfile, Event, BotStatistics, UserStatistics, Appointment


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['telegram_id', 'username', 'first_name', 'last_name', 'registered_at', 'export_token']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'user_id', 'name', 'event_date', 'event_time', 'details', 'is_public']


class BotStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotStatistics
        fields = ['date', 'user_count', 'event_count', 'edited_events', 'cancelled_events']


class UserStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatistics
        fields = ['user_telegram_id', 'created_events', 'edited_events', 'cancelled_events', 'updated_at']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'organizer_id', 'event', 'participant_telegram_id', 'date', 'time', 'details', 'status', 'created_at']