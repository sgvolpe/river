from django.urls import path, re_path
from . import views
from django.conf.urls import url, include

app_name = 'basic_dash'
urlpatterns = [
    re_path('^$', views.index, name='index'),
    re_path('^simple_example', views.simple_example, name='simple_example'),
    re_path('^app2', views.app2, name='app2'),
    re_path('^stock_app', views.stock_app, name='stock_app'),

    path('django_plotly_dash/', include('django_plotly_dash.urls'), name='the_django_plotly_dash'),
#    re_path('^basic_dash', views.BasicDashDetail.as_view(), name='basic_dash'),

]