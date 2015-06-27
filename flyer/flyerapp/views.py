from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from models import Schedule, Place
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
    schedules = Schedule.objects.select_related("departure").all()
    scheduleserializer = ScheduleSerializer(schedules, many=True)

    places = Place.objects.all()
    placeserializer = PlaceListSerializer(places)

    response = {}
    response['schedules'] = scheduleserializer.data
    response['places'] = placeserializer.data

    return render_to_response("schedule/index.html", {
        'data' : response
    })

def add_schedule(request):
	itens_pedido = request.session.get('itens_pedido', [])

	item = json.loads(request.body)['item']
	itens_pedido.append(item)

	request.session['itens_pedido'] = itens_pedido
	return HttpResponse(json.dumps(itens_pedido))

def delete_schedule(request, index):
    itens_pedido = request.session.get('itens_pedido', [])
    del itens_pedido[int(index)]
    request.session['itens_pedido'] = itens_pedido
    return HttpResponse(json.dumps(itens_pedido))