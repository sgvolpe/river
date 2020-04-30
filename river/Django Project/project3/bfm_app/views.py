
from django.shortcuts import render, get_object_or_404, redirect
import os, zlib,base64, re
import numpy as np
import lxml.etree as ET
import pandas as pd
from django.http import HttpResponse

from django.views.generic import (TemplateView, ListView)
from .models import bfm_rs, bfm_rs_option
from braces.views import SelectRelatedMixin
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from . import dashboard_app
from . import models
from . models import bfm_rs, bfm_rs_option, mfv, Benchmark

from . import assistant as AS

# Create your views here.

def index(request):
    return render(request, 'index.html',{})
    return HttpResponse('BFM App Index')





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
        #context['app'] = dashboard_app.get_summary_app(str(context['benchmark']))
        return context


class BenchmarkListView(ListView):
    model = Benchmark
    template_name = "dashboard/benchmark_list.html"
    select_related = ()

    def get_queryset(self):
        return SummaryDashboard.objects.all()


#@login_required
def run_analysis(request, pk):
    sc  = get_object_or_404(Benchmark, pk=pk)
    print (sc)
    sc.run_analysis()
    return redirect('bfm_app:benchmark_view', pk=sc.pk)

########################


class BFMListView(ListView):
    model = bfm_rs
    template_name = "bfm_app/bfm_rs_list.html"

    def get_queryset(self):
        return bfm_rs.objects.all()


class CreateBFM(LoginRequiredMixin,SelectRelatedMixin,generic.CreateView):
    model = models.bfm_rs
    #template_name = "bfm_app/bfm.html"
    fields = ("title", 'description','bfm_file')




class bfm_rsDetail(SelectRelatedMixin, generic.DetailView):
    model = bfm_rs
    select_related = ()
    #fields = ('title','bfml_file')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bfm = AS.bfm_rs(context['bfm_rs'].bfm_file.url)
        df = bfm.bfm_rs_to_df()
        context['app'] = dashboard_app.get_bfm_rs_app(df)
        return context


###################

class MFVListView(ListView):
    model = mfv
    template_name = "bfm_app/mfv_list.html"

    def get_queryset(self):
        return mfv.objects.all()


class CreateMFV(LoginRequiredMixin,SelectRelatedMixin,generic.CreateView):
    model = models.mfv
    fields = ("title", 'xml_file')


class MFVDetail(SelectRelatedMixin, generic.DetailView):
    model = mfv
    select_related = ()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        df = context['mfv'].parse_to_df()
        #MFV = AS.bfm_rs(context['bfm_rs'].bfm_file.url)
        #df = bfm.bfm_rs_to_df()
        context['app'] = dashboard_app.get_mfv_app(df)
        return context






##########################
