from django.contrib import admin
from django.contrib.admin import helpers

from flyerapp.models import Place, Schedule, Flight
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, date, timedelta
from collections import OrderedDict, deque
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
import os, sys

def search_flights(modeladmin, request, queryset):
    ids = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
    for id in ids:
        schedule = Schedule.objects.filter(id=id).get()
        departure = Place.objects.filter(id=schedule.departure_id).get()
        landing = Place.objects.filter(id=schedule.landing_id).get()

        config_datas = [ [schedule.departure_date,schedule.landing_date] ]
        search(departure, landing, departure.iata_code, landing.iata_code, config_datas, schedule.departure_in_weekend_only, schedule.landing_in_weekend_only, schedule.exactly_days_check, schedule.days_in_place)

    search_flights.short_description = "Search Flights"








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

def search(departure, landing, origem, destinos, config_datas, ida_durante_semana, volta_durante_semana, exactly_days_check, min_days_in_place):
    problemas = deque()
    nao_existe = deque()
    google_cheap_price_class = '-c-pb'
    google_processing_price_class = '-j-n'
    config_origem = {
        origem:origem
    }
    config_destinos = {
        destinos:destinos
    }
    for config_origem in config_origem:
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
                    #driver = webdriver.Firefox()
                    driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'])
                    driver.set_window_size( 2048, 2048)  # set browser size.

                    url = 'https://www.google.com.br/flights/#search;f=' + config_origem + ';t='+ str(destino[0]) +';d='+config_dia_inicio + ';r=' + config_dia_fim
                    #print url
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
                        # data hora consulta, origem, valor, data pesquisada ida, data pesquisada volta, destino, url acesso
                        valor_exibicao = resultado.text
                        valor_processado = valor_exibicao.split("R$")
                        valor_processado = valor_processado[1]
                        valor_processado = re.sub('[^0-9]+', '', valor_processado)

                        fly = Flight()
                        fly.departure = departure
                        fly.landing = landing
                        fly.price = valor_processado
                        fly.departure_date = config_dia_inicio
                        fly.landing_date = config_dia_fim
                        fly.link = url
                        fly.save()

                        #print "Valor" + "\t"+ valor_exibicao + "\t" + valor_processado + "\t" + config_dia_inicio + "\t" + config_dia_fim + "\t" + str(config_origem) + "\t" + str(destino[1]) + "\t" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y") + "\t" + datetime.now().strftime("%H:%M")

                        driver.quit()
                    except NoSuchElementException, e:
                        notfound_class = '.' + class_splited[0] + '-Pb-e'
                        resultado = driver.find_element_by_css_selector(notfound_class)
                        for ne in nao_existe:
                            if str(ne) == str(destino[1]):
                                problemas.append('Ignorar destino: ' + str(destino[1]))
                        nao_existe.append(str(destino[1]))
                        driver.quit()
                    except Exception, e:
                        problemas.append('Problema ao retornar valor de: ' + str(destino[1]) +"\t" + url)
                        driver.quit()
                    #print("--- %s seconds ---" % (time.time() - start_time_loop))
                except Exception, e:
                    problemas.append('Problema ao retornar elemento principal: ' + str(destino[1]) +"\t" + url)
                    driver.quit()





class ScheduleAdmin(admin.ModelAdmin):
    actions = [search_flights]

admin.site.register(Place)
admin.site.register(Schedule, ScheduleAdmin)