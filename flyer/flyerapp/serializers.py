__author__ = 'eduardo'
from django.forms import widgets
from rest_framework import serializers
from models import Schedule, Place, Flight

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
    departure = PlaceSerializer()

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
            'email'
        )

class FlightSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer()
    departure = PlaceSerializer()
    landing = PlaceSerializer()

    class Meta:
        model = Flight
        fields = (
            'id',
            'schedule',
            'departure',
            'landing',
            'price',
            'departure_date',
            'link'
        )

class FlightListSerializer(serializers.ListSerializer):
    child = FlightSerializer()
    allow_null = True
    many = True