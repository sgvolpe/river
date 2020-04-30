
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


def report(request):
    return HttpResponse('test')
