from django import template
from django.templatetags.static import static

register = template.Library()

@register.filter
def channel_icon(channel):
    return static(f'images/{channel}.png')

register = template.Library()

@register.filter
def replace_dash(value):
    """ '-' karakterlerini boşluk ile değiştirip kelimelerin baş harflerini büyük yapar """
    return value.replace("-", " ").title()

