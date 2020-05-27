import base64
from .models import Author, ShortUrl
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.http import HttpResponse

def index(request):
    return render(request, 'short_url/index.html', context={})

def encode(request, url):
    su = ShortUrl(original_url=url)
    su.encode()
    return HttpResponse (f'Here it is your url:  <a href="http://127.0.0.1:8000/short_url/decode/{su.pk}">http://127.0.0.1:8000/short_url/decode/{su.pk} </a>')



def decode(request, encoded_url):
    su = ShortUrl.objects.filter(pk=encoded_url)


    return redirect(f'http://{su[0].original_url}')

class ShortUrlCreate(CreateView):
    model = ShortUrl
    fields = ['name',]