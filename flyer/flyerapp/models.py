from django.db import models
from datetime import datetime
from rq import get_current_job
# Create your models here.
class Place(models.Model):
    name = models.CharField(max_length=70, null=False)
    iata_code = models.CharField(max_length=3, null=False, unique=True)
    
    def __unicode__(self):
        return self.name

class Schedule(models.Model):
    active = models.BooleanField(default=True, null=False)
    # notify = models.BooleanField(default=True, null=False)
    logic_delete = models.BooleanField(default=False, null=False)
    departure = models.ForeignKey(Place, related_name="departure_schedule", null=False)
    landing = models.ManyToManyField(Place, related_name="landing_schedule", null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    price_lower = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    price_highter = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    departure_date = models.DateField(default=None, null=False) 
    landing_date = models.DateField(default=None, null=False)
    days_in_place = models.IntegerField()
    departure_in_weekend_only = models.BooleanField(default=False, null=False)
    landing_in_weekend_only = models.BooleanField(default=False, null=False)
    exactly_days_check = models.BooleanField(default=False, null=False)
    email = models.CharField(max_length=80,default=None, null=True, blank=True)
    pub_date = models.DateTimeField('date published', null=True, default=datetime.now() )

    def __unicode__(self):
        return u'%s | %s: %s - %s >> %s' % (self.departure, ", ".join(l.name for l in self.landing.all()[:5]), self.departure_date, self.landing_date, self.price)

class Flight(models.Model):
    schedule = models.ForeignKey(Schedule, related_name="schedule_flight", null=False, default=None)
    departure = models.ForeignKey(Place, related_name="departure_flight", null=False)
    landing = models.ForeignKey(Place, related_name="landing_flight", null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    departure_date = models.DateField(default=None, null=False)
    landing_date = models.DateField(default=None, null=False)
    pub_date = models.DateTimeField('date published', null=True,default=datetime.now())
    link = models.TextField()

    def __unicode__(self):
      return u'%s | %s: %s - %s >> %s - %s' % (self.departure, self.landing, self.departure_date, self.landing_date, self.price, self.link)

class PossibleFlights(models.Model):
    schedule = models.ForeignKey(Schedule, related_name="schedule_schedule")
    pub_date = models.DateTimeField('date published')