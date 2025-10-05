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
