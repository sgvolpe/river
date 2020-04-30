
from __future__ import unicode_literals

import base64 ,datetime, io, json,plotly, dash, os, re, io, urllib
from datetime import datetime
from collections import OrderedDict

from django.shortcuts import render, get_object_or_404, redirect
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic import (TemplateView, ListView)

from braces.views import SelectRelatedMixin
from . import models
from . models import StatelessApp, IndividualDashboard, SummaryDashboard, ShoppingComparison, AncillariesComparison, Benchmark
from . import dashboard_app


import matplotlib as mpl
import matplotlib.pyplot as plt

import seaborn as sns

from . import assistant as AS


#import seaborn as sns
#from sklearn import preprocessing
#import matplotlib.pyplot as plt
#import dash
#import dash_core_components as dcc
#import dash_html_components as html


########################
#Benchmark

class CreateBenchmark(LoginRequiredMixin,SelectRelatedMixin,generic.CreateView):
    model = models.Benchmark
    #template_name = "bfm_app/bfm.html"
    fields = ("title", 'description','repeats','onds','ap', 'los','bfm_template_1','bfm_template_2')


class BenchmarkDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Benchmark
    select_related = ()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['app'] = dashboard_app.get_summary_app(str(context['benchmark']), providers = ['rq_1','rq_2'])
        except: pass
        #context['app'] = dashboard_app.get_summary_app(str(context['benchmark']))
        return context


class BenchmarkListView(ListView):
    model = Benchmark
    template_name = "dashboard/benchmark_list.html"
    select_related = ()

    def get_queryset(self):
        return Benchmark.objects.all()


#@login_required
def run_benchmark_analysis(request, pk):
    print ('Running Analysis')
    b  = get_object_or_404(Benchmark, pk=pk)
    print (b)
    b.run_analysis()
    return redirect('dashboard:benchmark_view', pk=b.pk)

########################


class CreateSummaryDashboard(LoginRequiredMixin,SelectRelatedMixin,generic.CreateView):
    model = models.SummaryDashboard
    #template_name = "bfm_app/bfm.html"
    fields = ("title", 'description','csv_file','onds','ap_los')


class SummaryDashboardDetail(SelectRelatedMixin, generic.DetailView):
    model = models.SummaryDashboard
    select_related = ()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app'] = dashboard_app.get_summary_app(str(context['summarydashboard']))
        return context


class SummaryDashboardListView(ListView):
    model = SummaryDashboard
    template_name = "dashboard/summarydashboard_list.html"
    select_related = ()

    def get_queryset(self):
        return SummaryDashboard.objects.all()

###

class CreateIndividualDashboard(LoginRequiredMixin, SelectRelatedMixin,generic.CreateView):
    model = IndividualDashboard
    #template_name = "bfm_app/bfm.html"
    fields = ("title", 'description','csv_file', 'summary_dashboard','onds','ap_los', 'search_date')


class IndividualDashboardDetail(SelectRelatedMixin, generic.DetailView):
    model = IndividualDashboard
    select_related = ()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app'] = dashboard_app.getapp(str(context['individualdashboard']))
        return context


class IndividualDashboardListView(ListView):
    model = IndividualDashboard
    template_name = "dashboard/individualdashboard_list.html"
    select_related = ()

    def get_queryset(self):
        return IndividualDashboard.objects.all()


def index(request):
    return render(request, 'index.html',{})

################################################################################
# Shopping ShoppingComparison
################################################################################

class CreateShoppingComparison(LoginRequiredMixin, SelectRelatedMixin,generic.CreateView):
    model = ShoppingComparison
    #template_name = "bfm_app/bfm.html"
    fields = ("title", 'description','csv_file','onds','ap_los', 'summary_dashboard')


class ShoppingComparisonDetail(SelectRelatedMixin, generic.DetailView):
    model = ShoppingComparison
    select_related = ()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['app'] = dashboard_app.getapp(str(context['shoppingcomparison']))
        return context


class ShoppingComparisonListView(ListView):
    model = ShoppingComparison
    template_name = "dashboard/shoppingcomparison_list.html"
    select_related = ()

    def get_queryset(self):
        return IndividualDashboard.objects.all()

#@login_required
def run_analysis(request, pk):
    sc  = get_object_or_404(ShoppingComparison, pk=pk)
    print (sc)
    sc.run_analysis()
    return redirect('dashboard:shoppingcomparison_view', pk=sc.pk)




################################################################################
# Ancillaries
################################################################################

class CreateAncillariesComparison(LoginRequiredMixin, SelectRelatedMixin,generic.CreateView):
    model = AncillariesComparison
    fields = ("title", 'description','bookings_file','ancillaries', 'charts')#,'charts','ancillaries')




class AncillariesComparisonDetail(SelectRelatedMixin, generic.DetailView):
    model = AncillariesComparison
    select_related = ()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ac = context['ancillariescomparison']
        ancillary_list = list(ac.ancillaries)
        gds_list = ['sabre','travelport']        #TODO: ADD TRAVELPORT
        ancillaries = AS.Ancillaries(pk=ac.pk, ancillary_list=ancillary_list, gds_list=gds_list, what_to_graph=['sabre+amadeus'], bookings_file=ac.bookings_file)
        context['app'] = dashboard_app.get_ancillaries(str(context['ancillariescomparison']), ancillaries)

        return context

def ancillaries_download_csv_files(request, pk):
    obj  = get_object_or_404(AncillariesComparison, pk=pk)




    ancillaries.get_csv_files()
    print ('+'*99)

    obj.get_csv_files()
    return redirect('dashboard:shoppingcomparison_view', pk=sc.pk)




class AncillariesComparisonListView(ListView):
    model = AncillariesComparison
    template_name = "dashboard/ancillariescomparison_list.html"
    select_related = ()

    def get_queryset(self):
        return AncillariesComparison.objects.all()
