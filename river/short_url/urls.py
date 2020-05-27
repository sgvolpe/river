from django.urls import path
from . import views




app_name = 'short_url'
urlpatterns = [
    path('', views.index, name='index'),
    path('encode/<str:url>/', views.encode, name='encode'),
    path('decode/<str:encoded_url>/', views.decode, name='decode'),
    path('new', views.ShortUrlCreate.as_view(), name='new'),
]
