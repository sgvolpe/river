from django.contrib import admin
from django.urls import path, re_path
from . import views


app_name = 'hello_app'
urlpatterns = [
    re_path('^$', views.index, name='index'),
    re_path('^new_index$', views.new_index, name='new_index'),
    path('bye', views.bye, name='bye'),
    path('register', views.register, name='register'),
    re_path('^logout/$', views.user_logout, name='logout'),
    re_path('^login/$', views.user_login, name='user_login'),


]
