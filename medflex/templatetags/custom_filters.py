from django import template

register = template.Library()


@register.filter
def get(dictionary, key):
    """Returns the value for the given key in a dictionary, or 'NA' if missing"""
    return dictionary.get(key, "NA")
