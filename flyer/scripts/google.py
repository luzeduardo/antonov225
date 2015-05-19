#!/usr/local/bin/python
# coding: utf-8
# To install the Python client library:
# pip install -U selenium
 
# Import the Selenium 2 namespace (aka "webdriver")
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, date, timedelta
from collections import OrderedDict, deque
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
import os, sys

reload(sys)  
sys.setdefaultencoding('utf8')

config_destinos = { 
    # 'ATM':'Altamira (PA)',
    # 'AJU':'Aracajú (SE)',
    # 'AQA':'Araraquara (SP)',
    # 'BGX':'Bagé (RS)',
    # 'JTC':'Bauru (SP)',
    'BEL':'Belém (PA)',
    'CNF':'Belo Horizonte – Confins (MG)',
    'PLU':'Belo Horizonte – Pampulha (MG)',
    'BVB':'Boa Vista (RR)',
    # 'BSB':'Brasília (DF)',
    'CPV':'Campina Grande (PB)',
    # 'VCP':'Campinas – Viracopos (SP)',
    'CGR':'Campo Grande (MS)',
    'CAW':'Campos dos Goytacazes (RJ)',
    # 'CKS':'Carajás (PR)',
    'CAU':'Caruaru (PE)',
    'CXJ':'Caxias do Sul (RS)',
    # 'XAP':'Chapecó (SC)',
    # 'CMG':'Corumbá (MS)',
    'CCM':'Criciúma (SC)',
    'CGB':'Cuiabá (MT)',
    'CWB':'Curitiba (PR)',
    # 'CZS':'Cruzeiro do Sul (AC)',
    # 'FEN':'Fernando de Noronha (PE)',
    'FLN':'Florianópolis (SC)',
    'FOR':'Fortaleza (CE)',
    'IGU':'Foz do Iguaçu (PR)',
    'GYN':'Goiânia (GO)',
    # 'IOS':'Ilhéus (BA)',
    # 'IMP':'Imperatriz (MA)',
    'JPA':'João Pessoa (PB)',
    'JOI':'Joinville (SC)',
    # 'JDO':'Juazeiro do Norte (CE)',
    # 'LDB':'Londrina (PR)',
    # 'MEA':'Macaé (RJ)',
    # 'MCP':'Macapá (AP)',
    'MCZ':'Maceió (AL)',
    'MAO':'Manaus (AM)',
    # 'MAB':'Marabá (PA)',
    'MGF':'Maringá (PR)',
    'MOC':'Montes Claros (MG)',
    # 'MVF':'Mossoró (RN)',
    # 'NAT':'Natal (RN)',
    'NVT':'Navegantes (SC)',
    # 'PMW':'Palmas (TO)',
    'PHB':'Parnaíba (PI)',
    # 'PAV':'Paulo Afonso (BA)',
    # 'PNZ':'Petrolina (PE)',
    'POO':'Poços de Caldas (MG)',
    'PMG':'Ponta Porã (MS)',
    'POA':'Porto Alegre (RS)',
    # 'BPS':'Porto Seguro (BA)',
    'PVH':'Porto Velho (RO)',
    # 'PPB':'Presidente Prudente (SP)',
    # 'REC':'Recife (PE)',
    # 'RAO':'Ribeirão Preto (SP)',
    'RBR':'Rio Branco (AC)',
    # 'SSA':'Salvador (BA)',
    'STM':'Santarém (PA)',
    # 'SJP':'São José do Rio Preto (SP)',
    # 'SJK':'São José dos Campos (SP)',
    'SLZ':'São Luiz (MA)',
    'CGH':'São Paulo – Congonhas (SP)',
    # 'GRU':'São Paulo – Guarulhos (SP)',
    'TBT':'Tabatinga (AM)',
    # 'THE':'Terezina (PI)',
    'UDI':'Uberlândia (MG)',
    # 'URA':'Uberaba (MG)',
    # 'UBT':'Ubatuba (SP)',
    # 'VIX':'Vitória (ES)'
}

# config_destinos = {
#   'JFK':'New York',
#   'MIA':'Miami',
#   'MCO':'Orlando',
#   'EZE':'Buenos Aires',
#   'CUZ':'Chile',
#   'CDG':'Paris',
#   'BCN':'Barcelona',  
#   'SXF':'Berlim',
#   'BRU':'Bélgica',
#   'AMS':'Amsterdã',
#   'LCY':'Londres',
#   'YYZ':'Canadá',
#   'MEX':'México',
#   'PRG':'Praga',
#   'DUB':'Irlanda Dublin',
#   'OPO':'Porto',
#   'LIS':'Lisboa',
#   'FRA':'Frankfurt',
#   'ATH':'Athenas',
# }
#config_origem = 'CGH'

config_destinos = {
    'JFK':'New York',
    'MIA':'Miami',
    'MCO':'Orlando',
    'CUZ':'Chile',
}
config_origem = 'GIG,SDU'

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


s_year = 2015
s_month = 11
s_day = 10

e_year = 2015
e_month = 11
e_day = 16

c_year = 2015
c_month = 5
c_day = 15
min_days_in_place = 2

datas = date_interval(s_year,s_month, s_day, e_year,e_month, e_day)
# datas = {
# '2015-06-14':'2015-06-22',
# '2015-06-13':'2015-06-22'
# }

config_datas = datas
problemas = deque()
nao_existe = deque()
ida_durante_semana = True
volta_durante_semana = True

print 'Hora Início: ' + datetime.now().strftime("%d/%m/%Y %H:%M")
for destino in config_destinos.items():
    for datas in config_datas:
        try:
            if is_weekend_day(datas[0]) and not ida_durante_semana: #ida apenas fds
                continue
            if is_weekend_day(datas[1]) and not volta_durante_semana: #volta apenas fds
                continue    
            if not is_valid_min_days_in_place(datas[0], datas[1], min_days_in_place):
                continue            
            config_dia_inicio = datas[0]
            config_dia_fim = datas[1]
            #driver = webdriver.Firefox()
            driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'])
            driver.set_window_size( 2048, 2048)  # set browser size.
            
            url = 'https://www.google.com.br/flights/#search;f=' + config_origem + ';t='+ str(destino[0]) +';d='+config_dia_inicio + ';r=' + config_dia_fim
            
            driver.get( url )
            time.sleep(2)
            driver.implicitly_wait(2)

            core = driver.find_element_by_css_selector('#root')
            class_name = core.get_attribute("class")            
            class_splited = class_name.split('-',1)
            final_class = '.' + class_splited[0] + '-c-nb'
            wait_class = '.' + class_splited[0] + '-j-n'

            #Testa se elemento de processamento sumiu e processegue com o script
            element_existe = True
            teste_processando = 0
            while element_existe:
                try:
                    teste_processando += 1
                    resultado = driver.find_element_by_css_selector(wait_class)
                    time.sleep(1)
                    driver.implicitly_wait(1)
                    if teste_processando == 3:
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
                print valor_exibicao + "\t" + valor_processado + "\t" + config_dia_inicio + "\t" + config_dia_fim + "\t" + str(config_origem) + "\t" + str(destino[1]) + "\t" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y") + "\t" + datetime.now().strftime("%H:%M")
                driver.quit()
            except NoSuchElementException, e:
                notfound_class = '.' + class_splited[0] + '-Pb-e'
                resultado = driver.find_element_by_css_selector(notfound_class)
                for ne in nao_existe:
                    if str(ne) == str(destino[1]):
                        problemas.append('Ignorar destino: ' + str(destino[1])+ ' motivo: ' +"\t" + valor)
                nao_existe.append(str(destino[1]))
                driver.quit()
            except Exception, e:
                problemas.append('Problema ao retornar valor de: ' + str(destino[1]) +"\t" + url)
                driver.quit()
        except Exception, e:
            problemas.append('Problema ao retornar elemento principal: ' + str(destino[1]) +"\t" + url)
            driver.quit()
print 'Hora Fim: ' + datetime.now().strftime("%d/%m/%Y %H:%M")
# @TODO verificar o que fazer com os erros
for erros in problemas:
    print erros
#link smiles
#'https://www.smiles.com.br/passagens-com-milhas?tripType=1&originAirport='+ config_origem +'&destinationAirport=' + destino[0] + '&departureDay=1433386800&returnDay=1433732400&adults=01&children=0&infants=0'