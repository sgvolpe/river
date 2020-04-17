from . import models
from . import app
from django.views.generic import (DetailView)

from django.http import HttpResponse
from django.shortcuts import render

DEBUG = True

def index(request):
    return HttpResponse('Basic Dash')

def simple_example(request):
    if DEBUG: print ('basic dash')

    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_simple_example()})
    return HttpResponse('simple')



