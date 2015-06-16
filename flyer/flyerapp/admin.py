from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import helpers

from models import Place, Schedule, Flight

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, date, timedelta
from collections import OrderedDict, deque
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
import os, sys

import tasks
import django_rq
from rq import get_current_job
from django_rq import job

"""
Code for cronjob execution.
This code will create automatically jobs in queue to do a flight search
"""
def autoexec_search_flights():
    scheduler = django_rq.get_scheduler('default')
    scheduler.schedule(
        scheduled_time=datetime.now(), # Time for first execution, in UTC timezone
        func=tasks.auto_schedule_search,                     # Function to be queued
        args=[None],                   # Arguments passed into function when executed
        kwargs={},                     # Keyword arguments passed into function when executed
        interval=3600,                   # Time before the function is called again, in seconds
        repeat=None                      # Repeat this number of times (None means repeat forever)
    )

    ids = Schedule.objects.filter(active=1).values()
    for scd in ids:
        schedule = Schedule.objects.filter(id=id, active=1)
        if schedule:
            schedule = schedule.get()
            departure = Place.objects.filter(id=schedule.departure_id).get()
            schedule_data_search(schedule, departure)

"""
This code will create manual jobs in queue to do a flight search
"""
def search_flights(modeladmin, request, queryset):
    ids = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
    for id in ids:
        schedule = Schedule.objects.filter(id=id, active=1)
        if schedule:
            schedule = schedule.get()
            departure = Place.objects.filter(id=schedule.departure_id).get()
            schedule_data_search(schedule, departure)

    search_flights.short_description = "Search Flights Manually"

"""
"""
def schedule_data_search(schedule, departure):
    landing_list = {}
    for lnd in schedule.landing.all():
        landing = {}
        landing[lnd.iata_code] = lnd.name
        landing_list[lnd.id] = landing

    config_datas = [ [schedule.departure_date,schedule.landing_date] ]
    try:
        enqueue_search(departure, departure.iata_code, landing_list, config_datas, schedule.departure_in_weekend_only, schedule.landing_in_weekend_only, schedule.exactly_days_check, schedule.days_in_place)
    except Exception, e:
        messages.error('Problema ao retornar valor de: ' + str(departure.iata_code))


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
def enqueue_search(departure, config_origem, config_destinos, config_datas, ida_durante_semana, volta_durante_semana, exactly_days_check, min_days_in_place):
    problemas = deque()
    nao_existe = deque()

    for destino in config_destinos.items():
        for datas in config_datas:
            try:
                #start_time_loop = time.time()
                if is_weekend_day(str(datas[0])) and not ida_durante_semana: #ida apenas fds
                    continue
                if is_weekend_day(str(datas[1])) and not volta_durante_semana: #volta apenas fds
                    continue
                if exactly_days_check and not is_valid_min_days_in_place(datas[0], datas[1], min_days_in_place):
                    continue
                config_dia_inicio = str(datas[0])
                config_dia_fim = str(datas[1])

                queue = django_rq.get_queue('default')
                queue.enqueue(tasks.fligth_value_search, departure, config_origem, destino, config_dia_inicio, config_dia_fim)
                #print("--- %s seconds ---" % (time.time() - start_time_loop))
            except Exception, e:
                problemas.append('Problema ao retornar elemento principal: ' + str(destino[1]) +"\t")
                return problemas

class FlightAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    pass

class ScheduleAdmin(admin.ModelAdmin):
    actions = [search_flights,autoexec_search_flights]

admin.site.register(Place)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Schedule, ScheduleAdmin)