from . import models
from . import app
from django.views.generic import (DetailView)

from django.http import HttpResponse
from django.shortcuts import render

DEBUG = True

def index(request):
    #return HttpResponse ('TEST')
    apps = [
            'analys_df_app',
            'stock_app']
    return render(request, 'basic_dash/--index.html', context={'apps':apps})

    return HttpResponse('Basic Dash')

def simple_example(request):
    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_simple_example(), 'app_name': 'simple_example'})

def app2(request):
    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_app2(), 'app_name': 'app2'})

def stock_app(request):
    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_stock_app(), 'app_name': 'stock_app'})


def live_app(request):
    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_live_app(), 'app_name': 'live_app'})

def analys_df_app(request):
    return render(request, 'basic_dash/simple_example.html', context={'app': app.get_analys_df_app(), 'app_name': 'analys_df_app'})


def render_app(request, app_name):
    if DEBUG: print (app_name)
    return render(request, 'basic_dash/dash_app.html', context={'app': app.get_app(app_name), 'app_name': app_name})





