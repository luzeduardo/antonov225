from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from datetime import datetime, date, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponseRedirect
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from models import Schedule, Place, Flight
from serializers import ScheduleSerializer, PlaceSerializer, PlaceListSerializer
from collections import OrderedDict, deque

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import json
import re
import tasks
import time
import django_rq
from rq import get_current_job
from django_rq import job

class JSONResponse(HttpResponse):
    """
    Um HttpReponse  que renderiza seu conteudo em, json.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def diffdays(date_a, date_b, date_format="%d/%m/%Y"):
    a = datetime.strptime(date_a, date_format)
    b = datetime.strptime(date_b, date_format)
    delta = b - a
    return int(delta.days)

def get_interval_from_diffdays(days):
    if days <= 2:
        return 1
    if days <= 5:
        return 2
    if days <= 10:
        return 7
    if days <= 15:
        return 13
    if days <= 30:
        return 25
    return 30




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
    schedules = Schedule.objects.filter(logic_delete=False, departure_date__gte=datetime.now() ).select_related("departure").all()
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
        schobj.days_in_place = get_interval_from_diffdays(diffdays(dt_start_temp, dt_end_temp))

        # schobj.departure_in_weekend_only = request.POST.get('sch-', None)
        # schobj.landing_in_weekend_only = request.POST.get('sch-', None)
        # schobj.exactly_days_check = request.POST.get('sch-', None)

        departure_id = request.POST.get('sch-place-departure', None)
        placeobj = Place.objects.get(pk=departure_id)
        schobj.departure = placeobj

        id = request.POST.get('sch-id', None)

        if id:
            Schedule.objects.filter(pk=id).update(logic_delete=True)
            scheduler = django_rq.get_scheduler('default')
            scheduler.cancel("auto_schedule_search(id=u'" + id + "')")

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
            Flight.objects.filter(schedule=id).delete()
            schobj = Schedule.objects.get(pk=id)
            if schobj:
                schobj.delete()
        else:
            msg = 'show errors'
    return HttpResponseRedirect( reverse( 'flyerapp:home' ) )

"""
This code will create manual jobs in queue to do a flight search
"""
@csrf_exempt
def manual_exec(request, *args, **kwargs):
    sch_id = request.POST.get('id',None)

    # cancelando o job automatico
    # scheduler = django_rq.get_scheduler('default')
    # list_of_job_instances = scheduler.get_jobs()
    # for job in list_of_job_instances:
    #     if str(job.func_name) =='flyerapp.views.auto_schedule_search' and job.kwargs['id'] == sch_id:
    #         scheduler.cancel(job)


    schedule = Schedule.objects.filter(pk=sch_id, active=1, logic_delete=False, departure_date__gte=datetime.now()).get()
    if schedule:
        departure = Place.objects.filter(pk=schedule.departure_id).get()
        schedule_data_search(schedule, departure)
        return HttpResponse(status=200)
    return HttpResponse(status=400)
"""
Code for cronjob execution.
This code will create automatically jobs in queue to do a flight search
"""
@csrf_exempt
def automatic_exec(request, *args, **kwargs):
    sch_id = request.POST.get('id',None)
    schedule = Schedule.objects.filter(pk=sch_id, active=1, logic_delete=False, departure_date__gte=datetime.now()).get()
    if schedule:
        scheduler = django_rq.get_scheduler('default')
        scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=auto_schedule_search,
            # args=[],
            kwargs={'id':sch_id},
            interval=30,
            repeat=None
        )

"""
"""
def schedule_data_search(schedule, departure):
    landing_list = {}
    for lnd in schedule.landing.all():
        landing = {}
        landing[lnd.iata_code] = lnd.name
        landing_list[lnd.id] = landing

    config_datas = [ [schedule.departure_date,schedule.landing_date] ]
    # try:
    enqueue_search(departure, departure.iata_code, landing_list, config_datas, schedule.departure_in_weekend_only, schedule.landing_in_weekend_only, schedule.exactly_days_check, schedule.days_in_place, schedule)
    # except Exception, e:


def perdelta_start_to_end(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

def perdelta_end_to_start(start, end, delta):
    curr = start
    while end > curr:
        yield end
        end -= delta

def days_between(s_year,s_month, s_day, e_year,e_month, e_day):
    d1 = datetime(s_year,s_month, s_day)
    d2 = datetime(e_year,e_month, e_day)
    return abs((d1 - d2).days)

def is_valid_min_days_in_place(start, end, min_days_in_place, exact=True):
    '''
    o parametro exact determina se podemos ficar no minimo x dias ou mais
    ou se podemos ficar exatamente x dias no local True equivale a um numero X dias apenas
    '''
    date_format = "%Y-%m-%d"
    a = datetime.strptime(start, date_format)
    b = datetime.strptime(end, date_format)
    delta = b - a
    num_days = int(delta.total_seconds()) / (3600 * 24) + 1
    if exact==True:
        if num_days == min_days_in_place:
            return True
    else:
        if num_days >= min_days_in_place:
            return True
    return False

def is_weekend_day(date):
    date_format = "%Y-%m-%d"
    day_number = datetime.strptime(date, date_format).weekday()
    if day_number == 5 or day_number == 6:
        return False
    else:
        return True

def date_interval(s_year,s_month, s_day, e_year,e_month, e_day):
    '''
    pega a diferenca entre as datas e gera o range baseado no numero de dias
    '''
    days = days_between(s_year,s_month, s_day, e_year,e_month, e_day)
    counter_days = days
    datas = list()

    #menor maior
    while counter_days > 0:
        for result in perdelta_start_to_end(date(s_year,s_month, s_day), date(e_year,e_month, e_day), timedelta(days=1)):
            if counter_days > 0:
                datas.append( [( str(result) ), (str(date(e_year,e_month, e_day) ))] )
            counter_days = counter_days - 1

    #maior menor
    counter_days = days
    itr = 0
    while counter_days > 0:
        for result in perdelta_end_to_start(date(s_year,s_month, s_day + itr), date(e_year,e_month, e_day), timedelta(days=1)):
            if itr == 0:
                continue
            if counter_days > 0:
                datas.append( [str(date(s_year, s_month, s_day + itr)) , str(result) ] )
        counter_days = counter_days - 1
        itr += 1

    return datas

"""
This method create the jobs in queue
"""
def enqueue_search(departure, config_origem, config_destinos, config_datas, ida_durante_semana, volta_durante_semana, exactly_days_check, min_days_in_place, schedule):
    problemas = deque()
    nao_existe = deque()

    for destino in config_destinos.items():
        for datas in config_datas:
            try:
                if is_weekend_day(str(datas[0])) and not ida_durante_semana: #ida apenas fds
                    continue
                if is_weekend_day(str(datas[1])) and not volta_durante_semana: #volta apenas fds
                    continue
                if exactly_days_check and not is_valid_min_days_in_place(datas[0], datas[1], min_days_in_place):
                    continue
                config_dia_inicio = str(datas[0])
                config_dia_fim = str(datas[1])

                queue = django_rq.get_queue('default')
                queue.enqueue(fligth_value_search, departure, config_origem, destino, config_dia_inicio, config_dia_fim, schedule.id)
                #fligth_value_search(departure, config_origem, destino, config_dia_inicio, config_dia_fim, schedule.id)
            except Exception, e:
                problemas.append('Problema ao retornar elemento principal: ' + str(destino[1]) +"\t")
                return problemas

def notify_price_range_to_user(price, schedule):
    tprice = float(price)
    hpct = float(schedule.price_highter)
    lpct = float(schedule.price_lower)
    sprice = float(schedule.price)
    hprice = sprice * hpct
    lprice = sprice * lpct - sprice
    if lprice <= tprice <= hprice:
        return True
    else:
        return False


"""
This method is executed by the queue
"""
@job
def fligth_value_search(departure, config_origem, destino, config_dia_inicio, config_dia_fim, scheduleid):
    problemas = deque()
    nao_existe = deque()
    google_cheap_price_class = '-c-pb'
    google_processing_price_class = '-j-n'

    driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'])
    driver.set_window_size( 2048, 2048)  # set browser size.

    url = 'https://www.google.com.br/flights/#search;f=' + config_origem + ';t='+ str(destino[1].keys()[0]) +';d='+config_dia_inicio + ';r=' + config_dia_fim
    driver.get( url )
    time.sleep(2)
    driver.implicitly_wait(2)

    core = driver.find_element_by_css_selector('#root')
    class_name = core.get_attribute("class")
    class_splited = class_name.split('-',1)
    final_class = '.' + class_splited[0] + google_cheap_price_class
    wait_class = '.' + class_splited[0] + google_processing_price_class

    #Testa se elemento de processamento sumiu e processegue com o script
    element_existe = True
    teste_processando = 0
    while element_existe:
        try:
            teste_processando += 1
            resultado = driver.find_element_by_css_selector(wait_class)
            time.sleep(1)
            driver.implicitly_wait(1)
            if teste_processando == 1:
                element_existe = False
        except NoSuchElementException, e:
            element_existe = False

    try:
        time.sleep(2)
        driver.implicitly_wait(2)
        resultado = driver.find_element_by_css_selector(final_class)

        valor_exibicao = resultado.text
        valor_processado = valor_exibicao.split("R$")
        valor_processado = valor_processado[1]
        valor_processado = re.sub('[^0-9]+', '', valor_processado)

        landing = Place.objects.filter(id=int(destino[0])).get()
        schedule = Place.objects.filter(id=int(scheduleid)).get()

        if schedule:
            notify_price_range_to_user(valor_processado, schedule)

        fly = Flight()
        fly.departure = departure
        fly.landing = landing
        fly.price = valor_processado
        fly.departure_date = config_dia_inicio
        fly.landing_date = config_dia_fim
        fly.link = url
        fly.save()

        driver.quit()
    except NoSuchElementException, e:
        notfound_class = '.' + class_splited[0] + '-Pb-e'
        resultado = driver.find_element_by_css_selector(notfound_class)
        for ne in nao_existe:
            if str(ne) == str(destino[1]):
                problemas.append('Ignorar destino: ' + str(destino[1]))
        nao_existe.append(str(destino[1]))
        driver.quit()
        return problemas
    except Exception, e:
        problemas.append('Problema ao retornar valor de: ' + str(destino[1]) +"\t" + url)
        driver.quit()
        return problemas

@job
def auto_schedule_search(id):
    # ids = Schedule.objects.filter(active=1,logic_delete=False, departure_date__gte=datetime.now()).values()
    # for scd in ids:
    #     schedule = Schedule.objects.filter(id=int(scd['id']), active=1,logic_delete=False)
    #     if schedule:
    #         schedule = schedule.get()
    #         departure = Place.objects.filter(id=schedule.departure_id).get()
    #         schedule_data_search(schedule, departure)

    schedule = Schedule.objects.filter(id=int(id), active=1,logic_delete=False,departure_date__gte=datetime.now())
    if schedule:
        schedule = schedule.get()
        departure = Place.objects.filter(id=schedule.departure_id).get()
        schedule_data_search(schedule, departure)
