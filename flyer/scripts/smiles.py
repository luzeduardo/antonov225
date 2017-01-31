#!/usr/local/bin/python
# coding: utf-8
# To install the Python client library:
# pip install -U selenium

# Import the Selenium 2 namespace (aka "webdriver")
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, date, timedelta
from collections import OrderedDict, deque
from itertools import combinations
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
import os, sys

reload(sys)
sys.#setdefaultencoding('utf8')

conf#ig_destinos = {
    #'AJU':'Aracajú (SE)',
    #'BEL':'Belém (PA)',
    'CNF':'Belo Horizonte – Confins (MG)',
    #'PLU':'Belo Horizonte – Pampulha (MG)',
    #'CXJ':'Caxias do Sul (RS)',
    #'CGB':'Cuiabá (MT)',
    'CWB':'Curitiba (PR)',
    'FLN':'Florianópolis (SC)',
    #'FOR':'Fortaleza (CE)',
    #'IGU':'Foz do Iguaçu (PR)',
    #'GYN':'Goiânia (GO)',
    #'IOS':'Ilhéus (BA)',
    #'JPA':'João Pessoa (PB)',
    #'MCZ':'Maceió (AL)',
    #'MAO':'Manaus (AM)',
    #'NAT':'Natal (RN)',
    #'NVT':'Navegantes (SC)',
    ## 'PMW':'Palmas (TO)',
    #'POA':'Porto Alegre (RS)',
    #'BPS':'Porto Seguro (BA)',
    #'PVH':'Porto Velho (RO)',
    #'REC':'Recife (PE)',
    #'RBR':'Rio Branco (AC)',
    #'SSA':'Salvador (BA)',
    #'SLZ':'São Luiz (MA)',
    'CGH':'São Paulo – Congonhas (SP)',
    ## 'GRU':'São Paulo – Guarulhos (SP)',
    ## 'THE':'Terezina (PI)',
    #'UDI':'Uberlândia (MG)',
    'VIX':'Vitória (ES)'
}#

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
#
# config_destinos = {
#     'NVT':'Navegantes',
#     'EZE':'Buenos Aires',
#     'MVD':'Montevideo',
#     # 'JFK':'New York',
#     # 'MIA':'Miami',
#     # 'MCO':'Orlando',
#     'CUZ':'Chile',
# }
origem = {
    'GIG',
    'SDU'
}
def calc_proc_load():
    processor_load =  os.getloadavg()
    proc_len = len(processor_load)
    max_load = 1.5 * float(proc_len)
    pprc_max_loaded = 0
    for prc in processor_load:
        pprc_max_loaded += float(prc)
    print pprc_max_loaded
    if pprc_max_loaded > max_load:
        return pprc_max_loaded - max_load
    else:
        return 0

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

def is_friday(date):
    date_format = "%Y-%m-%d"
    day_number = datetime.strptime(date, date_format).weekday()
    if day_number == 4:
        return True
    else:
        return False

def is_weekend_day(date):
    date_format = "%Y-%m-%d"
    day_number = datetime.strptime(date, date_format).weekday()
    if day_number == 5 or day_number == 6:
        return True
    else:
        return False

def date_interval(s_year,s_month, s_day, e_year,e_month, e_day):
    '''
    pega a diferenca entre as datas e gera o range baseado no numero de dias
    '''
    days = days_between(s_year,s_month, s_day, e_year,e_month, e_day)
    counter_days = days
    datas_list = list()

    #menor maior
    while counter_days > 0:
        for result in perdelta_start_to_end(date(s_year,s_month, s_day), date(e_year,e_month, e_day), timedelta(days=1)):
            if counter_days > 0:
                datas_list.append(str(result))
            counter_days = counter_days - 1

    #maior menor
    counter_days = days
    itr = 0
    while counter_days > 0:
        try:
            datetime(s_year,s_month, s_day + itr)
            for result in perdelta_end_to_start(date(s_year, s_month, s_day + itr), date(e_year, e_month, e_day), timedelta(days=1)):
                if itr == 0:
                    continue
                if counter_days > 0:
                    datas_list.append(str(result))
        except Exception, e:
            counter_days = counter_days - 1
            itr += 1
            continue
        counter_days = counter_days - 1
        itr += 1
        datas_list = setlist(datas_list)
    return combinations(datas_list, 2)

def setlist(lst=[]):
   return list(set(lst))


def stringtotimestamp(dt, epoch=datetime(1970,1,1), dt_format="%Y-%m-%d"):
    dt = datetime.strptime(dt.replace('Z', 'GMT'), dt_format)
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

s_year = 2017
s_month = 3
s_day = 1

e_year = 2017
e_month = 12
e_day = 31

min_days_in_place = 3
exactly_days_check = True

datas = date_interval(s_year, s_month, s_day, e_year, e_month, e_day)
#ou setando na mao
# datas = [['2017-04-14','2017-04-16'], ['2017-04-21','2017-04-23'], ['2017-04-29','2017-05-01']]
display_nao_encontrado = False

config_datas = datas
problemas = deque()
nao_existe = deque()
ida_sexta_feira = True
ida_durante_semana = False
volta_durante_semana = False
milha_buscada = 2600
percentual_acima = 2
percentual_abaixo = 2
preco_milha = 35
valor_maximo_smiles_money = 120
url = ''
timer = 1
# iii = 0
for datas in config_datas:
    for config_origem in origem:
        for destino in config_destinos.items():
            try:
                if is_friday(datas[0]) and not ida_sexta_feira:
                    continue
                if not is_friday(datas[0]) and not is_weekend_day(datas[0]) and not ida_durante_semana:
                    continue
                if not is_weekend_day(datas[1]) and not volta_durante_semana:
                    continue
                if exactly_days_check and not is_valid_min_days_in_place(datas[0], datas[1], min_days_in_place):
                    continue
                if datetime.strptime(datas[0], "%Y-%m-%d") >= datetime.strptime(datas[1], "%Y-%m-%d"):
                    continue



                # print config_origem + ' - ' + str(destino[0])  + ' - ' + datas[0] + ' - ' + datas[1] + ' - ' + str(iii)
                # iii += 1
                # continue

                config_dia_inicio = str(stringtotimestamp(datas[0]))
                config_dia_fim = str(stringtotimestamp(datas[1]))

                #driver = webdriver.Firefox()
                try:
                    driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any', '--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
                    driver.set_window_size(2048, 2048)  # set browser size.
                except Exception, e:
                    print "Erro com driver"

                url = 'https://www.smiles.com.br/emissao-com-milhas?tripType=1&originAirport='+ config_origem +'&destinationAirport=' + str(destino[0]) + '&departureDate=' + config_dia_inicio + '000&returnDate=' + config_dia_fim + '000&adults=1&children=0&infants=0&searchType=g3&segments=1&isElegible=false'
                # print datas[0] + ' - '+ datas[1] + ' - ' + config_origem + ' - ' + str(destino[0])
                # print url
                driver.get( url )
                time.sleep(timer)
                driver.implicitly_wait(timer)

                try:
                    milhas = 'ul.fGothamRoundedMedium18Gray'
                    time.sleep(timer)
                    driver.implicitly_wait(timer)
                    milhas = driver.find_elements_by_css_selector(milhas)
                    menor_milha = 0
                    encontrado_milha_range = False
                    valor_processado = 0
                    for resultado in milhas:
                        valor_processado = resultado.text
                        valor_processado = re.sub('[^0-9]+', '', valor_processado)
                        if menor_milha == 0 or menor_milha > valor_processado:
                            menor_milha = valor_processado

                        if int( valor_processado ) > 100000:
                            continue

                        if int(valor_processado) <= milha_buscada * percentual_abaixo <= int(valor_processado) * percentual_acima:
                            encontrado_milha_range = True
                            data =  "S" + "\t" + valor_processado + "\t" + datas[0] + "\t" + datas[1] + "\t" + url  + "\t" + str(config_origem) + "\t" + str(destino[1])  + "-" + str(destino[0]) + "\t" + datetime.now().strftime("%d/%m/%Y %H:%M") + "\n"
                            datafile =  "S" + "\t" + valor_processado + "\t" + datas[0] + "\t" + datas[1] + "\t" + str(config_origem) + "\t" + str(destino[1])  + "-" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y %H:%M") + "\n"
                            print data
                            file = open('smiles_passagem_' + datetime.now().strftime("%d%m%Y") + '.csv', 'a')
                            file.write(datafile)
                            # print "Milha" + "\t" + valor_processado + "\t" + valor_processado + "\t" + datas[0] + "\t" + datas[1] + "\t" + str(config_origem) + "\t" + str(destino[1]) + "\t" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y") + "\t" + datetime.now().strftime("%H:%M")

                    if not encontrado_milha_range and not int( valor_processado ) > 100000 and display_nao_encontrado:
                        print "Nao encontrado" + "\t" + menor_milha + "\t" + menor_milha + "\t" + datas[0] + "\t" + datas[1] + "\t" + str(config_origem) + "\t" + str(destino[1]) + "\t" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y") + "\t" + datetime.now().strftime("%H:%M")
                    # driver.quit()

                except Exception, e:
                    problemas.append('Problema ao retornar valor de: ' + str(destino[1]) +"\t" + url)
                    # driver.quit()

                try:
                    milhas = 'ul.fGothamRoundedMedium16Gray'
                    time.sleep(timer)
                    driver.implicitly_wait(timer)
                    milhas = driver.find_elements_by_css_selector(milhas)
                    menor_milha = 0
                    encontrado_milha_range = False
                    valor_processado = 0
                    for resultado in milhas:
                        valores = resultado.text.split("\n")
                        for valor in valores:
                            valor = valor.split("+")
                            valor_processado = int(re.sub('[^0-9]+', '', valor[0]))/preco_milha + int(re.sub('[^0-9]+', '', valor[1]))
                            if menor_milha == 0 or menor_milha > valor_processado:
                                menor_milha = valor_processado

                            if int( valor_processado ) > 100000:
                                continue

                            if valor_maximo_smiles_money >= int(re.sub('[^0-9]+', '', valor[1])):
                               encontrado_milha_range = True
                               data = "M" + "\t" + valor_processado + "\t" + datas[0] + "\t" + datas[1] + "\t" + url  + "\t" + str(config_origem) + "\t" + str(destino[1])  + "-" + str(destino[0]) + "\t" + datetime.now().strftime("%d/%m/%Y %H:%M") + "\n"
                               datafile =  "M" + "\t" + valor_processado + "\t" + datas[0] + "\t" + datas[1] + "\t" + str(config_origem) + "\t" + str(destino[1])  + "-" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y %H:%M") + "\n"
                               print data
                               file.write(datafile)
                                # print "Milha" + "\t" + valor_processado + "\t" + valor_processado + "\t" + datas[0] + "\t" + datas[1] + "\t" + str(config_origem) + "\t" + str(destino[1]) + "\t" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y") + "\t" + datetime.now().strftime("%H:%M")

                        if not encontrado_milha_range and not int( valor_processado ) > 100000 and display_nao_encontrado:
                            print "Nao encontrado" + "\t" + menor_milha + "\t" + menor_milha + "\t" + datas[0] + "\t" + datas[1] + "\t" + str(config_origem) + "\t" + str(destino[1]) + "\t" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y") + "\t" + datetime.now().strftime("%H:%M")
                        driver.quit()

                except Exception, e:
                    problemas.append('Problema ao retornar valor de: ' + str(destino[1]) +"\t" + url)
                    driver.quit()
                driver.quit()
            except Exception, e:
                problemas.append('Problema ao retornar elemento principal: ' + str(destino[1]) +"\t" + url)
                driver.quit()
print 'Hora Fim: ' + datetime.now().strftime("%d/%m/%Y %H:%M")
