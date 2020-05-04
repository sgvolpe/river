from . import app
from . models import AnalysisApp
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView


from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'dashboard/analysisapp_list.html', context={})



class AnalysisAppDetailView(DetailView):
    model = AnalysisApp


    def get_context_data(self, **kwargs):
        self.object.run()
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['app'] = self.object.app #app.AnalysisApp().get_app()
        context['app_name'] = 'analysis_app'

        return context

class AnalysisAppListView(ListView):
    model = AnalysisApp
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context