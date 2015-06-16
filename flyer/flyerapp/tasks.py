__author__ = 'eduardoluz'
import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from models import Place, Schedule, Flight
from rq import get_current_job
from django_rq import job
from datetime import datetime, date, timedelta
from collections import OrderedDict, deque
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re


@job
def fligth_value_search(departure, config_origem, destino, config_dia_inicio, config_dia_fim ):
    problemas = deque()
    nao_existe = deque()
    google_cheap_price_class = '-c-pb'
    google_processing_price_class = '-j-n'

    driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'])
    driver.set_window_size( 2048, 2048)  # set browser size.

    url = 'https://www.google.com.br/flights/#search;f=' + config_origem + ';t='+ str(destino[1].keys()[0]) +';d='+config_dia_inicio + ';r=' + config_dia_fim
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

        landing = Place.objects.filter(id=destino[0]).get()
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
        return problemas
    except Exception, e:
        problemas.append('Problema ao retornar valor de: ' + str(destino[1]) +"\t" + url)
        driver.quit()
        return problemas
