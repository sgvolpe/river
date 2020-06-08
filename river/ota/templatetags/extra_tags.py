import json
from django import template

from django.shortcuts import render
register = template.Library()

@register.filter
def to_json(value):
    print (value[:500])
    value = value.replace("'",'"')
    return json.loads(value)


@register.filter
def type_(value):
    return type(value)\

@register.filter
def get_elem_adjusted(value, el):

    return value[int(el) - 1]

@register.simple_tag
def my_tag(a, b, schedules, *args, **kwargs):

    leg = a[b]
    for sched in leg:
        sched_id = sched['ref']
        schedules[sched_id-1]


    return render(None, 'ota/test.html', context={'test':'chau'})
    return [{'departure': flight['departure']['airport'],
             'arrival': flight['arrival']['airport'],
             'dep_time': flight['departure']['time'],
             'arr_time': flight['arrival']['time'],
             } for flight in [schedules[sched['ref']-1] for sched in a[b]]]


@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg