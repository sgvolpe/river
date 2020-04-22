from django.urls import path, re_path
from . import views
from django.conf.urls import url, include

urlpatterns = [
    re_path('^$', views.index, name='index'),
    #re_path('^simple_example', views.simple_example, name='simple_example'),
    #re_path('^app2', views.app2, name='app2'),
    #re_path('^stock_app', views.stock_app, name='stock_app'),
    #re_path('^live_app', views.live_app, name='live_app'),
    #re_path('^analys_df_app', views.analys_df_app, name='analys_df_app'),
    #path('render_app/<str:app_name>/', views.render_app),
    path('render_app/<str:app_name>/', views.render_app, name='render_app'),
    re_path('render_app/$', views.index, name='index'),

    path('django_plotly_dash/', include('django_plotly_dash.urls'), name='the_django_plotly_dash'),
#    re_path('^basic_dash', views.BasicDashDetail.as_view(), name='basic_dash'),

]
app_name = 'basic_dash'
