__author__ = 'SGV'

import datetime, json
from collections import Counter

from .models import Itinerary, Passenger, Reservation, Search

from . import Handyman
from .Api import parse_response, get_token, send_bfm

from django.db.models import Avg, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from django.views.generic.detail import DetailView

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.gzip import gzip_page


def error(request):
    return HttpResponse('Error')


def log_search(func):
    pass



# TODO:
def clear_cache():
    pass

    # print('Clearing Cache')
    # Clear cached information for this query
    # TODO: [s.delete() for s in search_from_cache]
    # Override variable
    # #search_from_cache[0].observations = 'cache_cleared'
    # #search_from_cache = []


def store_new_search(origins, destinations, dates, adt=1, cnn=0, inf=0, options_limit=50, search=False):
    if not search:
        search = Search(origins=origins, destinations=destinations, dates=dates, adt=int(adt), cnn=int(cnn), inf=int(inf))
        #search.save()
    try:
        response = send_bfm(origins=origins, destinations=destinations, dates=dates, adt=int(adt), cnn=int(cnn),
                            inf=int(inf), options_limit=int(options_limit))
        search.save_results(results=response)
        search.save()
    except Exception as e:
        raise Exception(f'{str(e)}')
    return search


DEBUG = True
def search_backend(origins, destinations, dates, adt, cnn, inf, options_limit=50, request_search_id=False, cache=False):
    sep = ','
    print (f'Search backend {origins, destinations, dates, options_limit, request_search_id, cache}')
    if request_search_id:
        if DEBUG: print(f'Retrieving Existing Search: {request_search_id}')
        search = Search.objects.get(pk=request_search_id)
        search_id = search.pk

    elif cache:
        if DEBUG: print(f'Trying to retrieve from Cache')
        # Check if there is any info
        search = Search.objects.filter(origins=origins, destinations=destinations, adt=int(adt), cnn=int(cnn), inf=int(inf), dates=dates)
        print (search)

        if len(search) > 0:
            if DEBUG: print (f'Found in cache: {len(search)}')
            id = len(search) - 1

            cache_age = timezone.now() - search[id].updated
            cache_age_minutes = cache_age.total_seconds() / 60

            if cache_age_minutes > 15:
                if DEBUG: print(f'Cache too old:{cache_age_minutes} minutes')
                try:
                    search = store_new_search(origins=origins, destinations=destinations, adt=adt, cnn=cnn, inf=inf,
                                              options_limit=options_limit, search=search[id])
                    search_id = search.pk
                except Exception as e:
                    raise Exception(f'{e}')
            else:
                if DEBUG: print(f'Found in Cache')
                search_id = search[id].pk
                search = search[id]

        else:
            if DEBUG: print(f'Nothing in Cache')
            try:
                search = store_new_search(origins=origins, destinations=destinations, dates=dates, adt=adt, cnn=cnn, inf=inf,
                                              options_limit=options_limit)
                search_id = search.pk
            except Exception as e:
                raise Exception(f'{e}')
    else:
        if DEBUG: print(f'No Search Id Provided Nor using Cache')
        try:
            search = store_new_search(origins=origins, destinations=destinations, dates=dates, adt=adt, cnn=cnn, inf=inf,
                                              options_limit=options_limit)
            search_id = search.pk
        except Exception as e:
            raise Exception(f'{e}')

    return search, search_id


# @gzip_page()
def search(request):
    try:

        request_search_id = request.GET.get('search_id', False)

       # ori = request.GET.get('ori', '').upper()
        #des = request.GET.get('des', '').upper()
        # sta = request.GET.get('sta')
        # ret = request.GET.get('ret')

        origins = request.GET.get('origins', '').upper()
        destinations = request.GET.get('destinations', '').upper()
        dates = request.GET.get('dates', '')


        adt = int(request.GET.get('adt', 1))
        cnn = int(request.GET.get('cnn', 0))
        inf = int(request.GET.get('inf', 0))


        cache = request.GET.get('cache', 'off') == 'on'
        search_id = request.GET.get('search_id', False)

        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 5))

        options_limit = int(request.GET.get('options_limit', 50))
        main_carrier = request.GET.get('main_carrier', '').upper()

        if DEBUG:
            print ('***** SEARCH ******** ')
            print(origins, destinations, dates, adt, cache, request_search_id, offset, limit)
            print(request.headers['User-Agent'])
            print(request.GET)

        search, search_id = search_backend(origins, destinations, dates, adt, cnn, inf, options_limit, request_search_id, cache)#sta, ret,
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

        stats = get_itin_statistics(itinerary_origin=origins, itinerary_destination=destinations)


        return render(request, 'ota/results.html',
                      context={'ori': origins, 'des': destinations, 'dates': dates, 'results': itineraries,
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
    airports = ['MVD', 'BUE']
    for ori in airports:
        for des in airports:
            for sta, ret in Handyman.generate_date_pairs():
                print(ori, des, sta, ret)
                try:
                    search_backend(ori, des, sta=sta, ret=ret, cache=True)
                except Exception as e:
                    print(str(e))


#populate_cache()

def see_itinerary(request, pk):
    itinerary = Itinerary.objects.get(pk=pk).get_json()
    return render(request, 'ota/itinerary_details.html', context={'itinerary': itinerary, 'itin_id': pk, 'ERROR': False})


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
    print('*** PROMOTIONS ***')
    print (get_top_onds())
    cheap_itinearies = []
    for search in get_top_onds():
        origins = search['origins']
        destinations = search['destinations']
        searches = Search.objects.filter(origins=origins, destinations=destinations).values('origins',
                                        'destinations', 'cheapest_price').annotate(Avg('cheapest_price'))
        ond_avg_cheapest = searches[0]['cheapest_price__avg']

        for it in Itinerary.objects.filter(itinerary_origin=origins, itinerary_destination=destinations,
                                           total_price__lte=ond_avg_cheapest * 1.0).order_by('total_price')[:1]:
            cheap_itinearies.append(it)


    return cheap_itinearies



def get_shopping_stats(request):
    """ Returns a Search Queryset """
    most_popular = Search.objects.values('origins', 'destinations').annotate(Sum('hits')).order_by('hits__sum')
    trending_7days = Search.objects.values('origins', 'destinations').annotate(Sum('hits')).order_by('hits__sum')
    return {'most_popular': most_popular}


def index(request):

    promotions = get_promotions()
    shopping_stats = get_shopping_stats('')
    most_popular = shopping_stats['most_popular']

    return render(request, 'ota/index.html', context={'promotions': promotions, 'most_popular': most_popular,
                                                      'test': 'test', 'photos': range(10),
                                                      })


def checkout(request, pk):
    itinerary = Itinerary.objects.get(pk=pk).get_json()
    return render(request, 'ota/checkout.html', context={'test': 'test', 'ERROR': False, 'itinerary': itinerary,
                                                         'passengers': {k: '' for k in range(1, 2, 1)},
                                                         })

def reservation_details(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    itinerary = reservation.itinerary_id
    passengers = reservation.get_passengers()

    return render(request, 'ota/reservation_details.html', context={'itinerary': itinerary.get_json(),
                                                                    'checkout': 'No', 'passengers': {k+1: v for k, v in enumerate(passengers)},
                                                                    })


def create_reservation(request):
    name1 = request.POST.get('name1', None)
    surname1 = request.POST.get('surname1', None)
    phone1 = request.POST.get('phone1', None)
    name2 = request.POST.get('name2', None)
    surname2 = request.POST.get('surname2', None)
    phone2 = request.POST.get('phone2', None)
    name3 = request.POST.get('name3', None)
    surname3 = request.POST.get('surname3', None)
    phone3 = request.POST.get('phone3', None)

    itinerary_id = request.POST.get('itinerary_id', None)
    print (itinerary_id)

    passengers = []
    paxs = [
        {'name': name1, 'surname':surname1, 'phone': phone1},
        {'name': name2, 'surname':surname2, 'phone': phone2},
        {'name': name3, 'surname':surname3, 'phone': phone3},
    ]
    for pax in paxs:
        if pax['name'] is not None:
            passenger = Passenger(name=pax['name'], surname=pax['surname'], phone=pax['phone'])
            passenger.save()
            passengers.append(passenger)

    itinerary = Itinerary.objects.get(pk=int(itinerary_id))
    reservation = Reservation(itinerary_id=itinerary)
    reservation.save()

    reservation.add_passenger(passenger)
    reservation.save()

    context = {'itinerary': itinerary, 'passengers': passengers, 'reservation': reservation}
    return redirect(reservation)


    return HttpResponse('ok')