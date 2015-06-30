from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from datetime import datetime, date
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponseRedirect
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from models import Schedule, Place, Flight
from serializers import ScheduleSerializer, PlaceSerializer, PlaceListSerializer
import json

class JSONResponse(HttpResponse):
    """
    Um HttpReponse  que renderiza seu conteudo em, json.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def schedule_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        schedules = Schedule.objects.select_related("departure").all()
        scheduleserializer = ScheduleSerializer(schedules, many=True)

        places = Place.objects.all()
        placeserializer = PlaceListSerializer(places)

        response = {}
        response['schedules'] = scheduleserializer.data
        response['places'] = placeserializer.data
        return JSONResponse(response)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ScheduleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)


def schedule_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        schedule = Schedule.objects.get(pk=pk)
    except Schedule.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ScheduleSerializer(schedule)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ScheduleSerializer(schedule, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        schedule.delete()
        return HttpResponse(status=204)

def index(request, *args, **kwargs):
    schedules = Schedule.objects.filter(logic_delete=False).select_related("departure").all()
    scheduleserializer = ScheduleSerializer(schedules, many=True)

    places = Place.objects.all().order_by('name')
    placeserializer = PlaceListSerializer(places)

    response = {}
    response['schedules'] = scheduleserializer.data
    response['places'] = placeserializer.data

    return render_to_response("schedule/index.html", {
        'data' : response
    })

@csrf_exempt
def edit_schedule(request, *args, **kwargs):
    if request.method == 'POST':

        schobj = Schedule()
        dt_start_temp = request.POST.get('dt-start', None)
        dt_start = datetime.strptime(dt_start_temp, '%d/%m/%Y').strftime("%Y-%m-%d")
        dt_end_temp = request.POST.get('dt-end', None)
        dt_end = datetime.strptime(dt_end_temp, '%d/%m/%Y').strftime("%Y-%m-%d")

        schobj.price = float(request.POST.get('sch-price', 0))
        schobj.price_lower = float(request.POST.get('sch-price-lower', 0))
        schobj.price_highter = float(request.POST.get('sch-price-highter', 0))
        schobj.departure_date = dt_start
        schobj.landing_date = dt_end
        schobj.days_in_place = diffdays(dt_start_temp, dt_end_temp)

        # schobj.departure_in_weekend_only = request.POST.get('sch-', None)
        # schobj.landing_in_weekend_only = request.POST.get('sch-', None)
        # schobj.exactly_days_check = request.POST.get('sch-', None)

        departure_id = request.POST.get('sch-place-departure', None)
        placeobj = Place.objects.get(pk=departure_id)
        schobj.departure = placeobj

        id = request.POST.get('sch-id', None)

        if id:
            Schedule.objects.filter(pk=id).update(logic_delete=True)

        schobj.save()
        landings = request.POST.getlist('sch-place-landing', None)
        places = Place.objects.filter(pk__in=landings)
        schobj.landing = places
        schobj.save()
        return HttpResponseRedirect( reverse( 'flyerapp:home' ) )

@csrf_exempt
def delete_schedule(request, *args, **kwargs):
    if request.method == 'POST':
        id = request.POST.get('sch-id', None)
        if id:
            schobj = Schedule.objects.get(pk=id)
            if schobj:
                schobj.delete()
        else:
            msg = 'show errors'
    return HttpResponseRedirect( reverse( 'flyerapp:home' ) )

def diffdays(date_a, date_b, date_format="%d/%m/%Y"):
    a = datetime.strptime(date_a, date_format)
    b = datetime.strptime(date_b, date_format)
    delta = b - a
    return int(delta.days)