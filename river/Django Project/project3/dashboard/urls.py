
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dashboard'


urlpatterns = [
    path('', views.index, name='index'),

    #
    #path('dash2', views.dash2, name='dash2'),
    path('django_plotly_dash/', include('django_plotly_dash.urls'),name='the_django_plotly_dash'),


    #IndividualDashboard
    path('individual_new', views.CreateIndividualDashboard.as_view(), name='individual_new'),
    path('individual_list', views.IndividualDashboardListView.as_view(), name='individual_list'),
    path("individual_view/<int:pk>/",views.IndividualDashboardDetail.as_view(),name="individual_view"),

    #Summary Dashboard
    path('summary_new', views.CreateSummaryDashboard.as_view(), name='summary_new'),
    path('summary_list', views.SummaryDashboardListView.as_view(), name='summary_list'),
    path("summary_view/<int:pk>/",views.SummaryDashboardDetail.as_view(),name="summary_view"),

    #Shopping Comparison
    path('shoppingcomparison_new', views.CreateShoppingComparison.as_view(), name='shoppingcomparison_new'),
    path('shoppingcomparison_list', views.ShoppingComparisonListView.as_view(), name='shoppingcomparison_list'),
    path("shoppingcomparison_view/<int:pk>/",views.ShoppingComparisonDetail.as_view(),name="shoppingcomparison_view"),
    path("run_analysis/<int:pk>/", views.run_analysis, name="run_analysis"),


    #Ancillaries
    path('ancillariescomparison_new', views.CreateAncillariesComparison.as_view(), name='ancillariescomparison_new'),
    path('ancillariescomparison_list', views.AncillariesComparisonListView.as_view(), name='ancillariescomparison_list'),
    path('ancillariescomparison_view/<int:pk>/', views.AncillariesComparisonDetail.as_view(), name='ancillariescomparison_view'),
    path('ancillaries_download_csv_files/<int:pk>/', views.ancillaries_download_csv_files, name='ancillaries_download_csv_files'),

    #path('ancillaries_form', views.ancillaries_form, name='ancillaries_form'),
    #path('ancillaries_calculate', views.ancillaries_calculate, name='ancillaries_calculate'),

    #Benchmark
    path('benchmark_list', views.BenchmarkListView.as_view(), name='benchmark_list'),
    path('benchmark_new', views.CreateBenchmark.as_view(), name='benchmark_new'),
    path("benchmark_view/<int:pk>/",views.BenchmarkDetail.as_view(),name="benchmark_view"),
    path("run_benchmark_analysis/<int:pk>/", views.run_benchmark_analysis, name="run_benchmark_analysis"),
]
