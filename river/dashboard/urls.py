from django.urls import path, re_path
from . import views
from .views import AnalysisAppDetailView, AnalysisAppListView
from django.conf.urls import url, include


app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>', AnalysisAppDetailView.as_view(), name='app-detail'),
    path('list', AnalysisAppListView.as_view(), name='app-list'),
    path('django_plotly_dash/', include('django_plotly_dash.urls'), name='the_django_plotly_dash'), # the_django_plotly_dash' is not a registered namespace
    #path('app_list', views.index, name='index'),
]