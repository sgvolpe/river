"""river URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from . import views
#from hello_app import views

app_name = 'river'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('cameras_list', views.cameras_list, name='cameras_list'),
    path('cameras', views.cameras, name='cameras'),
    path('view_camera', views.view_camera, name='view_camera'),

    path('random_pic/', views.random_pic, name='random_pic'),
    path('random_cam/', views.random_cam, name='random_cam'),
    path('weather/', views.weather, name='weather'),



    path('ota/', include('ota.urls')),
    path('hello_app/', include('hello_app.urls')),
    path('short_url/', include('short_url.urls')),
    path('basic_dash/', include('basic_dash.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls'),name='the_django_plotly_dash'),

]


