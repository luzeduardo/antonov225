from django.db import models

# Create your models here.
class Place(models.Model):
	name = models.CharField(max_length=70)
	iata_code = models.CharField(max_length=5)

class Flight(models.Place):
	departure = models.ForeignKey(Place)
	landing = models.ForeignKey(Place)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	departure_date = models.DateTimeField(default=None, null=True) 
	landing_date = models.DateTimeField(default=None, null=True)
	pub_date = models.DateTimeField('date published')
	link = models.CharField()

class Schedule(models.Place):
	departure = models.ForeignKey(Place)
	landing = models.ForeignKey(Place)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	departure_date = models.DateTimeField(default=None, null=True) 
	landing_date = models.DateTimeField(default=None, null=True)
	days_in_place = models.IntegerField()
	departure_in_weekeng_only = BooleanField(initial=False)
	landing_in_weekeng_only = BooleanField(initial=False)
	pub_date = models.DateTimeField('date published')