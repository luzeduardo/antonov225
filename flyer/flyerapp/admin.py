from django.contrib import admin
from django.contrib.admin import helpers

from flyerapp.models import Place, Schedule

def search_flights(modeladmin, request, queryset):
    ids = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
    for id in ids:
        schedule = Schedule.objects.filter(id=id).get()
        departure = Place.objects.filter(id=schedule.departure_id).get()
        landing = Place.objects.filter(id=schedule.landing_id).get()

    search_flights.short_description = "Search Flights"

class ScheduleAdmin(admin.ModelAdmin):
    actions = [search_flights]

admin.site.register(Place)
admin.site.register(Schedule, ScheduleAdmin)