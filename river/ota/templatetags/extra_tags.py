import json
from django import template


register = template.Library()

@register.filter
def to_json(value):
    print (value[:500])
    value = value.replace("'",'"')
    return json.loads(value)


@register.filter
def type(value):
    return type(value)