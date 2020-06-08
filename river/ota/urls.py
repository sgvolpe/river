
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from . import views
#from hello_app import views

app_name = 'ota'

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('results', views.results, name='results'),
    path('return_something', views.return_something, name='return_something'),
    path('search_details/<int:pk>/', views.search_details.as_view(), name='search_details'),



]


