from django.db import models
from datetime import datetime
# Create your models here.
class Place(models.Model):
    name = models.CharField(max_length=70, null=False)
    iata_code = models.CharField(max_length=3, null=False)
    
    def __unicode__(self):
        return self.name

class Flight(models.Model):
    departure = models.ForeignKey(Place, related_name="departure_flight", null=False)
    landing = models.ForeignKey(Place, related_name="landing_flight", null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    departure_date = models.DateField(default=None, null=False) 
    landing_date = models.DateField(default=None, null=False)
    pub_date = models.DateTimeField('date published', null=True)
    link = models.TextField()

class Schedule(models.Model):
    departure = models.ForeignKey(Place, related_name="departure_schedule", null=False)
    landing = models.ForeignKey(Place, related_name="landing_schedule", null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    price_percent_lower = models.DecimalField(max_digits=2, decimal_places=1, null=False, default=1.3)
    price_percent_highter = models.DecimalField(max_digits=2, decimal_places=1, null=False, default=1.3)
    departure_date = models.DateField(default=None, null=False) 
    landing_date = models.DateField(default=None, null=False)
    days_in_place = models.IntegerField()
    departure_in_weekend_only = models.BooleanField(default=False, null=False)
    landing_in_weekend_only = models.BooleanField(default=False, null=False)
    exactly_days_check = models.BooleanField(default=False, null=False)
    url_access = models.TextField(default=None, null=True, blank=True)
    email = models.CharField(max_length=80,default=None, null=True, blank=True)
    pub_date = models.DateTimeField('date published', null=True, default=datetime.now() )

class PossibleFlights(models.Model):
    schedule = models.ForeignKey(Schedule, related_name="schedule_schedule")
    pub_date = models.DateTimeField('date published')