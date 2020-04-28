from django.shortcuts import render, HttpResponse


def index(request):
    print('am i here?')
    return render(request, 'index.html', context={'test': 'test'})
    return HttpResponse("Hello, world. You're at the polls index.")