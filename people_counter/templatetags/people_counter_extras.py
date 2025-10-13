import locale
from datetime import datetime
from django import template


register = template.Library()


@register.filter
def get_percentage(value1, value2):
    if value2 > 0:
        return round(value1 / value2 * 100, 2)
    else:
        return 0


@register.filter
def get_rate(value1, value2):
    if value2 > 0:
        return round((value1 - value2) / value2 * 100, 2)
    else:
        return 0


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_day_name(date):
    locale.setlocale(locale.LC_ALL, "es_ES")
    return datetime.strptime(date, "%Y-%m-%d").strftime("%A").title()
