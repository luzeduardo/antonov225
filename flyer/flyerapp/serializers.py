__author__ = 'eduardo'
from django.forms import widgets
from rest_framework import serializers
from models import Schedule, Place

class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Place
        fields = (
            'id',
            'name',
            'iata_code'
        )

class PlaceListSerializer(serializers.ListSerializer):
    child = PlaceSerializer()
    allow_null = True
    many = True


class ScheduleSerializer(serializers.ModelSerializer):
    landing = PlaceSerializer(many=True)

    class Meta:
        model = Schedule
        fields = (
            'id',
            'active',
            'departure',
            'landing',
            'price',
            'price_lower',
            'price_highter',
            'departure_date',
            'landing_date',
            'days_in_place',
            'departure_in_weekend_only',
            'landing_in_weekend_only',
            'exactly_days_check',
            'url_access',
            'email'
        )
