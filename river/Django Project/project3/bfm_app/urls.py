from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static


app_name = 'bfm_app'

urlpatterns = [
    #path('', views.index, name='BFMListView'),
    path('list', views.BFMListView.as_view(), name='list'),
    path('new', views.CreateBFM.as_view(), name='new'),
    path("view/<int:pk>/",views.bfm_rsDetail.as_view(),name="view"),

    #Market Fare View
    path('mfv_list', views.MFVListView.as_view(), name='mfv_list'),
    path('mfv_new', views.CreateMFV.as_view(), name='mfv_new'),
    path("mfv_view/<int:pk>/",views.MFVDetail.as_view(),name="mfv_view"),


    path('benchmark_list', views.BenchmarkListView.as_view(), name='benchmark_list'),
    path('benchmark_new', views.CreateBenchmark.as_view(), name='benchmark_new'),
    path("benchmark_view/<int:pk>/",views.BenchmarkDetail.as_view(),name="benchmark_view"),
    path("run_analysis/<int:pk>/", views.run_analysis, name="run_analysis"),
]
