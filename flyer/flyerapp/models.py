from django.db import models

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
    pub_date = models.DateTimeField('date published')
    link = models.TextField()

class Schedule(models.Model):
    departure = models.ForeignKey(Place, related_name="departure_schedule", null=False)
    landing = models.ForeignKey(Place, related_name="landing_schedule", null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    departure_date = models.DateField(default=None, null=False) 
    landing_date = models.DateField(default=None, null=False)
    days_in_place = models.IntegerField()
    departure_in_weekeng_only = models.BooleanField(default=False, null=False)
    landing_in_weekeng_only = models.BooleanField(default=False, null=False)
    pub_date = models.DateTimeField('date published')