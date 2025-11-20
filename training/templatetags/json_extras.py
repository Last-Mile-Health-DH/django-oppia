import json
from django import template

register = template.Library()

@register.filter
def json_key(value, key):
    try:
        data = json.loads(value)
        return data.get(key, '')
    except Exception:
        return ''