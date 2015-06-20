__author__ = 'eduardo'
from django.forms import widgets
from rest_framework import serializers
from models import Schedule

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            'active',
            'departure',
            'landing',
            'price',
            'price_percent_lower',
            'price_percent_highter',
            'departure_date',
            'landing_date',
            'days_in_place',
            'departure_in_weekend_only',
            'landing_in_weekend_only',
            'exactly_days_check',
            'url_access',
            'email'
        )