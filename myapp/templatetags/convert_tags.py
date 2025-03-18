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


@register.filter(name="get_type")
def get_type(dictionary, key):
    """Returns the value of a dictionary for the given key."""
    myItem = dictionary.get(key, "")
    return myItem.get("type", "")

@register.filter(name="get_name")
def get_name(dictionary, key):
    """Returns the value of a dictionary for the given key."""
    myItem = dictionary.get(key, "")
    return myItem.get("name", "")

@register.filter(name="get_wert")
def get_wert(dictionary, key):
    """Returns the value of a dictionary for the given key."""
    myItem = dictionary.get(key, "")
    return myItem.get("wert", "")

@register.filter(name="get_avr")
def get_avr(dictionary, key):
    """Returns the value of a dictionary for the given key."""
    myItem = dictionary.get(key, "")
    return myItem.get("avr", "")

@register.filter(name="get_aktuell_wert")
def get_aktuell_wert(dictionary, key):
    """Returns the value of a dictionary for the given key."""
    myItem = dictionary.get(key, "")
    return myItem.get("aktuellWert", "")