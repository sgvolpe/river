from django.shortcuts import render
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView
from . import forms
from django.core.files.storage import FileSystemStorage

# Create your views here.


def apps_directory(request):
    template_name = "apps/apps_directory.html"
    return render (request, 'apps_directory.html', {})



def generate_dates_form(request):
    template_name = "apps/generate_dates_form.html"
    return render (request, 'generate_dates_form.html', {})


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'simple_upload.html')
