from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'web_apps'

urlpatterns = [
    path('', views.apps_directory, name='apps_directory'),
    path('generate_dates_form/', views.generate_dates_form, name='generate_dates_form'),
    path('simple_upload/', views.simple_upload, name='simple_upload'),

]
