__author__ = 'SGV'

import json
from collections import Counter

from .models import Itinerary, Search

from . import Handyman
from .Api import parse_response, get_token, send_bfm

from django.db.models import Avg, Sum
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

    promotions = get_promotions()

    return render(request, 'ota/index.html', context={'promotions': promotions,
                                                      'test': 'test', 'photos': range(10)})


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
    try:
        response = send_bfm(ori=ori, des=des, sta=sta, ret=ret, options_limit=int(options_limit))
        new_search.save_results(results=response)
        new_search.save()
    except Exception as e:
        raise Exception(f'{str(e)}')
    return new_search


DEBUG = True


def search_backend(ori, des, sta, ret, options_limit=50, request_search_id=False, cache=False):
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
            try:
                search = store_new_search(ori, des, sta, ret, options_limit)
                search_id = search.pk
            except Exception as e:
                raise Exception(f'{e}')
        else:
            if DEBUG: print(f'Found in Cache')
            search_id = search[0].pk
            search = search[0]
    else:
        if DEBUG: print(f'No Search Id Provided Nor using Cache')
        try:
            search = store_new_search(ori, des, sta, ret, options_limit)
            search_id = search.pk
        except Exception as e:
            raise Exception(f'{e}')

    return search, search_id


# @gzip_page()
def search(request):
    try:
        request_search_id = request.GET.get('search_id', False)

        ori = request.GET.get('ori', '').upper()
        des = request.GET.get('des', '').upper()
        sta = request.GET.get('sta')
        ret = request.GET.get('ret')

        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 5))

        cache = request.GET.get('cache', False) in ['true', 'True', True, 'TRUE']
        options_limit = int(request.GET.get('options_limit', 50))
        main_carrier = request.GET.get('main_carrier', '').upper()

        if DEBUG:
            print(ori, des, sta, ret, cache, request_search_id, offset, limit)
            print(request.headers['User-Agent'])
            print(request.GET)

        search, search_id = search_backend(ori, des, sta, ret, options_limit, request_search_id, cache)
        itineraries = search.pull()
        total_options_number = len(itineraries.keys())

        if DEBUG:
            with open('static/ota/itineararies.txt', 'w') as rq:
                rq.write(json.dumps(itineraries))

        # Filter and Truncate
        def filter_itineraries(itineraries, **kwargs):
            for filter, value in kwargs.items():
                if value != '':
                    itineraries = {k: v for k, v in itineraries.items() if v[filter] == value}
            return itineraries

        itineraries = filter_itineraries(itineraries, main_carrier=main_carrier)
        airlines_counter = dict(Counter([itin['main_carrier'] for itin_id, itin in itineraries.items()]))

        # itineraries = {k: v for k, v in itineraries.items() if offset <= int(k) < offset + limit}
        itineraries = {i: v for i, v in enumerate(itineraries.values()) if offset <= int(i) < offset + limit}

        stats = get_itin_statistics(itinerary_origin=ori, itinerary_destination=des)


        return render(request, 'ota/results.html',
                      context={'ori': ori, 'des': des, 'sta': sta, 'ret': ret, 'results': itineraries,
                               'search_id': search_id, 'limit': limit, 'offset': offset,
                               'total_options_number': total_options_number,
                               'airlines_counter': airlines_counter,
                               'stats': stats,
                               })
    except Exception as e:
        return render(request, 'ota/results.html', context={'ERROR': e})


def return_something(request):
    return 'Something'


def results(request):
    return HttpResponse(f'Searching: {request}')


def analytics(): pass


class search_details(DetailView):
    model = Search
    select_related = ('pk', 'origins', 'destinations')
    template_name = "ota/search_details.html"

    def get_context_data(self, **kwargs):
        context = super(search_details, self).get_context_data(**kwargs)
        context['test'] = 'TEST'
        return context


def populate_cache():
    airports = ['MVD', 'BUE', 'SCL']
    for ori in airports:
        for des in airports:
            for sta, ret in Handyman.generate_date_pairs():
                print(ori, des, sta, ret)
                try:
                    search_backend(ori, des, sta=sta, ret=ret, cache=True)
                except Exception as e:
                    print(str(e))


# populate_cache()

def see_itinerary(request, pk):
    itinerary = Itinerary.objects.get(pk=pk)
    return render(request, 'ota/itinerary_details.html', context={'itinerary': itinerary})


def get_itin_statistics(**kwargs):
    stats = {}
    for k, v in kwargs.items():
        print(k, v)
    # searches = Search.
    itineraries = Itinerary.objects.filter(**kwargs)
    print(len(itineraries))
    if len(itineraries) > 0:
        prices = [itin.total_price for itin in itineraries]
        stats['avg_price'] = sum(prices) / len(prices)

    return stats


def get_top_onds(top_n=50):
    searches = Search.objects.values('origins', 'destinations').annotate(Sum('hits')).order_by()
    return searches[:top_n]


def get_promotions():
    for search in get_top_onds():
        ori = search['origins'].split(',')[0]
        des = search['destinations'].split(',')[0]
        ond_price_queryset = Itinerary.objects.filter(itinerary_origin=ori,
                                                      itinerary_destination=des).values('itinerary_origin',
                                                        'itinerary_destination').annotate(Avg('total_price'))
        try:
            ond_avg_price = ond_price_queryset[0]['total_price__avg']

            cheap_itinearies = Itinerary.objects.filter(itinerary_origin=ori, itinerary_destination=des,
                                                        total_price__lte=ond_avg_price * .8)
            print(ond_price_queryset)
            print(ond_avg_price)
            print(cheap_itinearies)

            return cheap_itinearies
        except:
            pass


get_promotions()
