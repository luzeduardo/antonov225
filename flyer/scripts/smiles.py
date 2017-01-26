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
    'ATM':'Altamira (PA)',
    'AJU':'Aracajú (SE)',
    'AQA':'Araraquara (SP)',
    'BGX':'Bagé (RS)',
    'JTC':'Bauru (SP)',
    'BEL':'Belém (PA)',
    'CNF':'Belo Horizonte – Confins (MG)',
    'PLU':'Belo Horizonte – Pampulha (MG)',
    'BVB':'Boa Vista (RR)',
    'BSB':'Brasília (DF)',
    'CPV':'Campina Grande (PB)',
    'VCP':'Campinas – Viracopos (SP)',
    'CGR':'Campo Grande (MS)',
    'CAW':'Campos dos Goytacazes (RJ)',
    'CKS':'Carajás (PR)',
    'CAU':'Caruaru (PE)',
    'CXJ':'Caxias do Sul (RS)',
    'XAP':'Chapecó (SC)',
    'CMG':'Corumbá (MS)',
    'CCM':'Criciúma (SC)',
    'CGB':'Cuiabá (MT)',
    'CWB':'Curitiba (PR)',
    'CZS':'Cruzeiro do Sul (AC)',
    'FEN':'Fernando de Noronha (PE)',
    'FLN':'Florianópolis (SC)',
    'FOR':'Fortaleza (CE)',
    'IGU':'Foz do Iguaçu (PR)',
    'GYN':'Goiânia (GO)',
    'IOS':'Ilhéus (BA)',
    'IMP':'Imperatriz (MA)',
    'JPA':'João Pessoa (PB)',
    'JOI':'Joinville (SC)',
    'JDO':'Juazeiro do Norte (CE)',
    'LDB':'Londrina (PR)',
    # 'MEA':'Macaé (RJ)',
    'MCP':'Macapá (AP)',
    'MCZ':'Maceió (AL)',
    'MAO':'Manaus (AM)',
    'MAB':'Marabá (PA)',
    'MGF':'Maringá (PR)',
    'MOC':'Montes Claros (MG)',
    'MVF':'Mossoró (RN)',
    'NAT':'Natal (RN)',
    'NVT':'Navegantes (SC)',
    # 'PMW':'Palmas (TO)',
    'PHB':'Parnaíba (PI)',
    'PAV':'Paulo Afonso (BA)',
    'PNZ':'Petrolina (PE)',
    'POO':'Poços de Caldas (MG)',
    'PMG':'Ponta Porã (MS)',
    'POA':'Porto Alegre (RS)',
    'BPS':'Porto Seguro (BA)',
    'PVH':'Porto Velho (RO)',
    'PPB':'Presidente Prudente (SP)',
    'REC':'Recife (PE)',
    'RAO':'Ribeirão Preto (SP)',
    'RBR':'Rio Branco (AC)',
    'SSA':'Salvador (BA)',
    'STM':'Santarém (PA)',
    'SJP':'São José do Rio Preto (SP)',
    'SJK':'São José dos Campos (SP)',
    'SLZ':'São Luiz (MA)',
    'CGH':'São Paulo – Congonhas (SP)',
    # 'GRU':'São Paulo – Guarulhos (SP)',
    'TBT':'Tabatinga (AM)',
    # 'THE':'Terezina (PI)',
    'UDI':'Uberlândia (MG)',
    'URA':'Uberaba (MG)',
    'UBT':'Ubatuba (SP)',
    'VIX':'Vitória (ES)'
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
config_origem = {
    'GIG',
    #'CGH'
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
    days = days_between(s_year,s_month, s_day, e_year,e_month, int(e_day))
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

def stringtotimestamp(dt, epoch=datetime(1970,1,1), dt_format="%Y-%m-%d"):
    dt = datetime.strptime(dt.replace('Z', 'GMT'), dt_format)
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

s_year = 2017
s_month = 04
s_day = 21

e_year = 2017
e_month = 04
e_day = 23

c_year = 2017
c_month = 4
c_day = 23
min_days_in_place = 3
exactly_days_check = False

#datas = date_interval(s_year,s_month, s_day, e_year,e_month, e_day)
#ou setando na mao
datas = [['2017-04-21','2017-04-23'],['2017-04-14','2017-04-16'],['2017-04-29','2017-05-01']]
display_nao_encontrado = False


config_datas = datas
problemas = deque()
nao_existe = deque()
ida_durante_semana = True
volta_durante_semana = True
milha_buscada = 12000
percentual_acima = 2
percentual_abaixo = 2
url = ''
timer = 3
# print 'Hora Início: ' + datetime.now().strftime("%d/%m/%Y %H:%M")
for config_origem in config_origem:
    for destino in config_destinos.items():
        for datas in config_datas:
            try:
                #corrigir timezone para trabalhar co o timestamp
                if is_weekend_day(datas[0]) and not ida_durante_semana: #ida apenas fds
                    continue
                if is_weekend_day(datas[1]) and not volta_durante_semana: #volta apenas fds
                    continue
                if exactly_days_check and not is_valid_min_days_in_place(datas[0], datas[1], min_days_in_place):
                    continue
                config_dia_inicio = str(stringtotimestamp(datas[0]))
                config_dia_fim = str(stringtotimestamp(datas[1]))
                #print config_dia_fim
                #continue

                #driver = webdriver.Firefox()
                driver = webdriver.PhantomJS(service_args=['--ssl-protocol=any'])
                driver.set_window_size( 2048, 2048)  # set browser size.

                url = 'https://www.smiles.com.br/emissao-com-milhas?tripType=1&originAirport='+ config_origem +'&destinationAirport=' + str(destino[0]) + '&departureDate=' + config_dia_inicio + '000&returnDate=' + config_dia_fim + '000&adults=1&children=0&infants=0&searchType=g3&segments=1&isElegible=false'
                print datas[0] + ' - '+ datas[1] + ' - ' + config_origem + ' - ' + str(destino[0])
                # print url
                driver.get( url )
                time.sleep(timer)
                driver.implicitly_wait(timer)

                milhas = 'ul.fGothamRoundedMedium18Gray'

                #Testa se elemento de processamento sumiu e processegue com o script
                # element_existe = True
                # teste_processando = 0
                # while element_existe:
                #     try:
                #         teste_processando += 1
                #         resultado = driver.find_elements_by_css_selector('div.legData[data-legid="0"] td.resulttable.rtB .hide')
                #         for sml in resultado:
                #             print json.dumps(sml.text, sort_keys=True, ensure_ascii=False)
                #         #print resultado.text
                #         if teste_processando == 3:
                #             element_existe = False
                #     except NoSuchElementException, e:
                #         element_existe = False

                try:
                    time.sleep(timer)
                    driver.implicitly_wait(timer)
                    milhas = driver.find_elements_by_css_selector(milhas)
                    menor_milha = 0
                    encontrado_milha_range = False
                    for resultado in milhas:
                        valor_processado = resultado.text
                        valor_processado = re.sub('[^0-9]+', '', valor_processado)
                        if menor_milha == 0 or menor_milha > valor_processado:
                            menor_milha = valor_processado

                        if int( valor_processado ) > 100000: #ignorando valores de smiles e money
                            continue

                        if int(valor_processado) <= milha_buscada * percentual_abaixo <= int(valor_processado) * percentual_acima:
                            encontrado_milha_range = True
                            print "Milha" + "\t" + valor_processado + "\t" + valor_processado + "\t" + datas[0] + "\t" + datas[1] + "\t" + str(config_origem) + "\t" + str(destino[1]) + "\t" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y") + "\t" + datetime.now().strftime("%H:%M")

                    if not encontrado_milha_range and not int( valor_processado ) > 100000 and display_nao_encontrado:
                        print "Nao encontrado" + "\t" + menor_milha + "\t" + menor_milha + "\t" + datas[0] + "\t" + datas[1] + "\t" + str(config_origem) + "\t" + str(destino[1]) + "\t" + str(destino[0]) + "\t" + url  + "\t" + datetime.now().strftime("%d/%m/%Y") + "\t" + datetime.now().strftime("%H:%M")
                    driver.quit()
                # except NoSuchElementException, e:
                #     notfound_class = '.' + class_splited[0] + '-Pb-e'
                #     resultado = driver.find_element_by_css_selector(notfound_class)
                #     for ne in nao_existe:
                #         if str(ne) == str(destino[1]):
                #             problemas.append('Ignorar destino: ' + str(destino[1])+ ' motivo: ' +"\t" + valor)
                #     nao_existe.append(str(destino[1]))
                #     driver.quit()
                except Exception, e:
                    problemas.append('Problema ao retornar valor de: ' + str(destino[1]) +"\t" + url)
                    driver.quit()
            except Exception, e:
                problemas.append('Problema ao retornar elemento principal: ' + str(destino[1]) +"\t" + url)
                driver.quit()
# print 'Hora Fim: ' + datetime.now().strftime("%d/%m/%Y %H:%M")
# @TODO verificar o que fazer com os erros
# for erros in problemas:
#     print erros
#link smiles


#def process_or_sleep_task():
#processamento de task simples com time sleep
# i = 0
# while i < 9999999999999999999:
#     i += 1
#     sleep_time = calc_proc_load()
#     if sleep_time > 0:
#         print '------------------'
#         time.sleep(sleep_time)
