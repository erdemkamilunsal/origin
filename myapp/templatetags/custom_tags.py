from django import template
from django.templatetags.static import static

register = template.Library()

@register.filter
def channel_icon(channel):
    return static(f'images/{channel}.png')
