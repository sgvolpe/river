__author__ = 'SGV'

import json
from collections import Counter

from .models import Search

from . import Handyman
from . Api import parse_response, get_token, send_bfm
from django.http import HttpResponse
from django.shortcuts import render

from django.views.generic.detail import DetailView

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.gzip import gzip_page


def error(request):
    return HttpResponse('Error')

def log_search(func):
    pass

def index(request):
    return render(request, 'ota/index.html', context={'test': 'test', 'photos': range(10)})


# TODO:
def clear_cache():
    pass

    # print('Clearing Cache')
    # Clear cached information for this query
    # TODO: [s.delete() for s in search_from_cache]
    # Override variable
    # #search_from_cache[0].observations = 'cache_cleared'
    # #search_from_cache = []


def store_new_search(ori, des, sta, ret, options_limit):
    new_search = Search(origins=ori, destinations=des, dates=','.join([sta, ret]))
    new_search.save()
    response = send_bfm(ori=ori, des=des, sta='sta', ret='ret', options_limit=int(options_limit))
    new_search.save_results(results=response)
    new_search.save()
    return new_search


DEBUG = True


# @gzip_page()
def search(request):
    ori = request.GET.get('ori')
    des = request.GET.get('des')
    sta = request.GET.get('sta')
    ret = request.GET.get('ret')

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 5))

    request_search_id = request.GET.get('search_id', False)
    cache = request.GET.get('cache', False) in ['true', 'True', True, 'TRUE']
    options_limit = int(request.GET.get('options_limit', 50))

    main_carrier = request.GET.get('main_carrier', '')

    if DEBUG:
        print(ori, des, sta, ret, cache, request_search_id, offset, limit)
        print(request.headers['User-Agent'])
        print(request.GET)

    if request_search_id:
        if DEBUG: print(f'Retrieving Existing Search: {request_search_id}')
        search = Search.objects.get(pk=request_search_id)
        search_id = search.pk

    elif cache:
        if DEBUG: print(f'Trying to retrieve from Cache')
        # Check if there is any info
        search = Search.objects.filter(origins=ori, destinations=des, dates=[sta, ret])
        if len(search) == 0:
            if DEBUG: print(f'Nothing in Cache')
            search = store_new_search(ori, des, sta, ret, options_limit)
            search_id = search.pk
        else:
            if DEBUG: print(f'Found in Cache')
            search_id = search[0].pk
            search = search[0]
    else:
        if DEBUG: print(f'No Search Id Provided Nor using Cache')
        search = store_new_search(ori, des, sta, ret, options_limit)
        search_id = search.pk

    itineraries = search.pull()
    total_options_number = len(itineraries.keys())

    if DEBUG:
        with open('static/ota/itineararies.txt', 'w') as rq:
            rq.write(json.dumps(itineraries))

    # Filter and Truncate
    def filter_itineraries(itineraries, **kwargs):
        print(kwargs)
        for filter, value in kwargs.items():
            if value != '':
                itineraries = {k: v for k, v in itineraries.items() if v[filter] == value}
        return itineraries

    itineraries = filter_itineraries(itineraries, main_carrier=main_carrier)
    airlines_counter = dict(Counter([itin['main_carrier'] for itin_id, itin in itineraries.items()]))

    itineraries = {k: v for k, v in itineraries.items() if offset <= int(k) < offset + limit}


    return render(request, 'ota/results.html',
                  context={'ori': ori, 'des': des, 'sta': sta, 'ret': ret, 'results': itineraries,
                           'search_id': search_id, 'limit': limit, 'offset': offset,
                           'total_options_number': total_options_number,
                           'airlines_counter': airlines_counter,
                           })


def return_something(request):
    return 'Something'


def results(request):
    return HttpResponse(f'Searching: {request}')


def analytics():pass


class search_details(DetailView):
    model = Search
    select_related = ('pk', 'origins', 'destinations')
    template_name = "ota/search_details.html"

    def get_context_data(self, **kwargs):
        context = super(search_details, self).get_context_data(**kwargs)
        context['test'] = 'TEST'
        return context



def populate_cache():
    pass