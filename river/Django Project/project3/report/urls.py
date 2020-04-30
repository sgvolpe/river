
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dashboard'


urlpatterns = [
    path('', views.index, name='index'),


    path('django_plotly_dash/', include('django_plotly_dash.urls'),name='the_django_plotly_dash'),


    
    path('new', views.new, name='new'),


]
