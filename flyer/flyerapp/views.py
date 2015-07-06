from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from datetime import datetime, date, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponseRedirect
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from models import Schedule, Place, Flight
from serializers import ScheduleSerializer, PlaceSerializer, PlaceListSerializer, FlightSerializer, FlightListSerializer
from collections import OrderedDict, deque

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from django.contrib.auth import logout

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

def index(request, *args, **kwargs):

    if request.user and request.user.is_active:
        user_id = request.user.id
    else:
        # @TODO trhow exception
        user_id = 0

    schedules = Schedule.objects.filter(user=user_id, logic_delete=False, departure_date__gte=datetime.now() ).select_related("departure").all()
    scheduleserializer = ScheduleSerializer(schedules, many=True)

    places = Place.objects.all().order_by('name')
    placeserializer = PlaceListSerializer(places)

    response = {}
    response['schedules'] = scheduleserializer.data
    response['places'] = placeserializer.data

    return render_to_response("schedule/index.html", {
        'data' : response,
        'user': request.user
    })

@csrf_exempt
def edit_schedule(request, *args, **kwargs):
    if request.method == 'POST':

        if request.user and request.user.is_active:
            user_id = request.user.id
        else:
            # @TODO trhow exception
            user_id = 0

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

        schobj.user_id = user_id

        departure_in_weekend_only = request.POST.get('departure_in_weekend_only', False)
        if departure_in_weekend_only == 'on':
            departure_in_weekend_only = True
        landing_in_weekend_only = request.POST.get('landing_in_weekend_only', False)
        if landing_in_weekend_only == 'on':
            landing_in_weekend_only = True

        schobj.departure_in_weekend_only = departure_in_weekend_only
        schobj.landing_in_weekend_only = landing_in_weekend_only
        # schobj.exactly_days_check = request.POST.get('sch-', None)

        departure_id = request.POST.get('sch-place-departure', None)
        placeobj = Place.objects.get(pk=departure_id)
        schobj.departure = placeobj

        id = request.POST.get('sch-id', None)

        if id:
            Schedule.objects.filter(pk=id).update(logic_delete=True)
            remove_automatic_scheduled_jobs(id)

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
                remove_automatic_scheduled_jobs(id)
        else:
            msg = 'show errors'
    return HttpResponseRedirect( reverse( 'flyerapp:home' ) )

@csrf_exempt
def flights(request, *args, **kwargs):
    response = {}
    sch_id = request.POST.get('id',None)
    flight = Flight.objects.filter(schedule_id=sch_id).select_related("departure").order_by('pub_date').reverse().all()
    if flight:
        flightserializer = FlightListSerializer(flight)
        response['flights'] = flightserializer.data

    return render_to_response("flight/flights.html", {
        'data' : response
    })

"""
This code will create manual jobs in queue to do a flight search
"""
@csrf_exempt
def stop_automatic_exec(request, *args, **kwargs):
    sch_id = request.POST.get('id',None)
    if remove_automatic_scheduled_jobs(sch_id):
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

"""
This code will create manual jobs in queue to do a flight search
"""
@csrf_exempt
def manual_exec(request, *args, **kwargs):
    sch_id = request.POST.get('id',None)

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


def remove_automatic_scheduled_jobs(sch_id):
    # cancelando o job automatico
    scheduler = django_rq.get_scheduler('default')
    list_of_job_instances = scheduler.get_jobs()
    result = False
    for job in list_of_job_instances:
        if str(job.func_name) =='flyerapp.views.auto_schedule_search' and job.kwargs['id'] == sch_id:
            scheduler.cancel(job)
            result = True

    return result

def logout_view(request):
    logout(request)
    request.session.flush()
    return HttpResponseRedirect( reverse( 'flyerapp:home' ) )

"""
"""
def schedule_data_search(schedule, departure):
    landing_list = {}
    for lnd in schedule.landing.all():
        landing = {}
        landing[lnd.iata_code] = lnd.name
        landing_list[lnd.id] = landing

    config_datas = date_interval(schedule.departure_date.year, schedule.departure_date.month, schedule.departure_date.day,
                  schedule.landing_date.year, schedule.landing_date.month, schedule.landing_date.day)
    # try:
    enqueue_search(departure, departure.iata_code, landing_list, config_datas, schedule.departure_in_weekend_only, schedule.landing_in_weekend_only, schedule.exactly_days_check, schedule.days_in_place, schedule)
    # except Exception, e:


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
    if days <= 15:
        return 3
    return 4

def days_between(s_year,s_month, s_day, e_year,e_month, e_day):
    d1 = datetime(s_year,s_month, s_day)
    d2 = datetime(e_year,e_month, e_day)
    return abs((d1 - d2).days)

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
    days_for_interval = get_interval_from_diffdays(days)
    counter_days = days
    datas = list()
    tmp_days_start = list()
    tmp_days_end = list()

    base_start = datetime(s_year, s_month, s_day)
    date_list_prior = [base_start - timedelta(days=x) for x in range(0, days_for_interval)]
    for date_prior in date_list_prior:
        tmp_days_start.append(date_prior.strftime("%Y-%m-%d"))

    date_list_after = [base_start + timedelta(days=x) for x in range(1, days_for_interval)]
    for date_after in date_list_after:
        tmp_days_start.append(date_after.strftime("%Y-%m-%d"))


    base_end = datetime(e_year, e_month, e_day)
    date_list_prior = [base_end - timedelta(days=x) for x in range(0, days_for_interval)]
    for date_prior in date_list_prior:
        tmp_days_end.append(date_prior.strftime("%Y-%m-%d"))

    date_list_after = [base_end + timedelta(days=x) for x in range(1, days_for_interval)]
    for date_after in date_list_after:
        tmp_days_end.append(date_after.strftime("%Y-%m-%d"))


    for day_start in tmp_days_start:
        for day_end in tmp_days_end:
            datas.append( [( str(day_start) ), (str(day_end))] )

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

                config_dia_inicio = str(datas[0])
                config_dia_fim = str(datas[1])

                if settings.DEBUG_EXECUCAO:
                    fligth_value_search(departure, config_origem, destino, config_dia_inicio, config_dia_fim, schedule.id)
                else:
                    queue = django_rq.get_queue('default')
                    queue.enqueue(fligth_value_search, departure, config_origem, destino, config_dia_inicio, config_dia_fim, schedule.id)

            except Exception, e:
                problemas.append('Problema ao retornar elemento principal: ' + str(destino[1]) +"\t")
                return problemas

def notify_price_range_to_user(price, schedule):
    tprice = float(price)
    hprice = float(schedule.price_highter)
    lprice = float(schedule.price_lower)

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
        schedule = Schedule.objects.filter(id=int(scheduleid)).get()

        if schedule:
            notify_price_range_to_user(valor_processado, schedule)

        fly = Flight()
        fly.schedule = schedule
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
