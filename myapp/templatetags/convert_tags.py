# convert_tags.py
from django import template

register = template.Library()

@register.filter
def substract(value, arg):
    """ Add double quotes to a string value """
    return (float(value) - float(arg))

@register.filter
def adding(value, arg):
    """ Add double quotes to a string value """
    return (float(value) + float(arg))