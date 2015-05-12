from django.db import models

# Create your models here.
class Departures(models.Model):
	ori = models.CharField(max_length=5)
	cash = models.DecimalField(max_digits=10, decimal_places=2)
	pub_date = models.DateTimeField('date published')
class Landing(models.Model):
	ori = models.CharField(max_length=5)
	cash = models.DecimalField(max_digits=10, decimal_places=2)
	pub_date = models.DateTimeField('date published')