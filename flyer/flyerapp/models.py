from django.db import models

# Create your models here.
class Place(models.Model):
	name = models.CharField(max_length=70)
	iata_code = models.CharField(max_length=5)

class Flight(models.Model):
	departure = models.ForeignKey(Place, related_name="departure_flight")
	landing = models.ForeignKey(Place, related_name="landing_flight")
	price = models.DecimalField(max_digits=10, decimal_places=2)
	departure_date = models.DateField(default=None, null=True) 
	landing_date = models.DateField(default=None, null=True)
	pub_date = models.DateTimeField('date published')
	link = models.TextField()

class Schedule(models.Model):
	departure = models.ForeignKey(Place, related_name="departure_schedule")
	landing = models.ForeignKey(Place, related_name="landing_schedule")
	price = models.DecimalField(max_digits=10, decimal_places=2)
	departure_date = models.DateField(default=None, null=True) 
	landing_date = models.DateField(default=None, null=True)
	days_in_place = models.IntegerField()
	departure_in_weekeng_only = models.BooleanField(default=False)
	landing_in_weekeng_only = models.BooleanField(default=False)
	pub_date = models.DateTimeField('date published')