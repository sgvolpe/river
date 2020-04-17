from . import models
from . import app
from django.views.generic import (DetailView)

from django.http import HttpResponse
from django.shortcuts import render

DEBUG = True

def index(request):
    return HttpResponse('Basic Dash')

def simple_example(request):
    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_simple_example(), 'app_name': 'simple_example'})

def app2(request):
    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_app2(), 'app_name': 'app2'})

def stock_app(request):
    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_stock_app(), 'app_name': 'stock_app'})




