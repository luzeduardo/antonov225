#coding: utf-8
from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from datetime import datetime
import logging
import json
import locale
locale.setlocale(locale.LC_ALL, '')

register = template.Library()

@register.filter
def hash(h, key):
    return h[key]

@register.filter
def to_date(value, arg):
    try:
        dt = datetime.strptime(value, arg)
        return dt
    except Exception, e:
        return ""

@register.filter
def convertdateformat(value, fmt):
    return datetime.strptime(value, '%Y-%m-%d').strftime(fmt)

@register.filter
def jsonify(value):
    return mark_safe(json.dumps(value))

@register.filter
def msisdn_format(value):
    try:
        ddd = value[0:2]
        msisdn = value[2:7]
        msisdn_f = value[7:12]
        return '(' + ddd + ')' + msisdn + '-' + msisdn_f
    except ValueError:
        return ''

@register.filter
def get_range( value ):
    """
    Returns a standard Python zero-based range.
    from: https://djangosnippets.org/snippets/1357/
    Filter - returns a list containing range made from given value
    Usage (in template):
    <ul>
    {% for i in 3|get_range %}
    <li>{{ i }}. Do something</li>
    {% endfor %}
    </ul>
    Results with the HTML:
    <ul>
    <li>0. Do something</li>
    <li>1. Do something</li>
    <li>2. Do something</li>
    </ul>
    Instead of 3 one may use the variable set in the views
    """
    return range( value )

@register.filter
def get_range1( value ):
    """
    Same as get_range but with a 1-based range, end inclusive.
    <ul>
    {% for i in 3|get_range1 %}
    <li>{{ i }}. Do something</li>
    {% endfor %}
    </ul>
    Results with the HTML:
    <ul>
    <li>1. Do something</li>
    <li>2. Do something</li>
    <li>3. Do something</li>
    </ul>
    """
    return range(1, int(value)+1)

@register.filter
def get_range_start( value, arg ):
    """
    Same as get_range but with a 1-based range, end inclusive.
    <ul>
    {% for i in 3|get_range1 %}
    <li>{{ i }}. Do something</li>
    {% endfor %}
    </ul>
    Results with the HTML:
    <ul>
    <li>1. Do something</li>
    <li>2. Do something</li>
    <li>3. Do something</li>
    </ul>
    """
    return range( arg, int(value)+1 )

@register.filter
def cpf_format(value):
    try:
        ddd = value[0:2]
        msisdn = value[2:7]
        msisdn_f = value[7:12]
        return value[0:3] + '.' + value[3:6] + '.' + value[6:9] + '-' + value[9:11]
    except ValueError:
        return ''

@register.filter
def sum(value, arg):
    return value + arg

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter()
def to_float(value):
    return float(value.replace(',', '.'))

@register.filter()
def yearmonthformat(value):
     ano = value[0]
     mes = value[1]     
     return str(ano) + str(mes) 

@register.filter
def get_at_index(list, index):
    return list[index]     

@register.filter
def concatestr(value, arg):
    return str(value) + str(arg)

@register.filter(name='access')
def access(value, arg):
    return value[arg]

# @register.filter
# def get_year_range_dict(years):
#     current_year = datetime.now( ).year
#     for x in range( 1, int(years)):


def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)

@register.filter
def currency(value, arg = '', symbol = True):
    '''
    Currency formatting template filter.

    Takes a number -- integer, float, decimal -- and formats it according to
    the locale specified as the template tag argument (arg). Examples:

      * {{ value|currency }}
      * {{ value|currency:"en_US" }}
      * {{ value|currency:"pt_BR" }}
      * {{ value|currency:"pt_BR.UTF8" }}

    If the argument is omitted, the default system locale will be used.

    The third parameter, symbol, controls whether the currency symbol will be
    printed or not. Defaults to true.

    As advised by the Django documentation, this template won't raise
    exceptions caused by wrong types or invalid locale arguments. It will
    return an empty string instead.

    Be aware that currency formatting is not possible using the 'C' locale.
    This function will fall back to 'en_US.UTF8' in this case.
    '''

    saved = '.'.join([x for x in locale.getlocale() if x]) or (None, None)
    given = arg and ('.' in arg and str(arg) or str(arg) + '.UTF-8')
    # Workaround for Python bug 1699853 and other possibly related bugs.
    if '.' in saved and saved.split('.')[1].lower() in ('utf', 'utf8'):
        saved = saved.split('.')[0] + '.UTF-8'

    if saved == (None, None) and given == '':
        given = 'en_US.UTF-8'
    try:
        locale.setlocale(locale.LC_ALL, given)
        res = locale.currency(float(value) or 0, symbol, True)
        return res
    except (TypeError, locale.Error):
        return ''

    finally:
        locale.setlocale(locale.LC_ALL, saved)