__author__ = 'SGV'

from django.db import models
from django.forms.models import model_to_dict


class Search(models.Model):
    origins = models.CharField(max_length=50, blank=True)
    destinations = models.CharField(max_length=50, blank=True)
    dates = models.CharField(max_length=50, blank=True)
    options_in_cache = models.IntegerField(blank=True, default=0)
    observations = models.CharField(max_length=250, blank=True)

    def save_results(self, results) -> None:
        self.save()
        for itinerar_key, itinerary_details in results.items():
            itin = Itinerary(search_id=self)
            itin.create_(itinerary_details)
            itin.save()
        self.save()

    def get_json(self):
        itineraries = Itinerary.objects.filter(search_id=self.pk)
        return {id: itinerary.get_json() for id, itinerary in enumerate(itineraries)}



class Itinerary(models.Model):
    search_id = models.ForeignKey(Search, on_delete=models.CASCADE)
    main_carrier = models.CharField(max_length=2, blank=True)
    flight_numbers = models.CharField(max_length=200, blank=True)

    departure_airports = models.CharField(max_length=3, blank=True, default='SGV')
    arrival_airports = models.CharField(max_length=3, blank=True, default='SGV')
    departure_times = models.CharField(max_length=5, blank=True, default='12:00')
    arrival_times = models.CharField(max_length=5, blank=True, default='12:00')
    carriers = models.CharField(max_length=2, blank=True, default='YY')


    itinerary_origin = models.CharField(max_length=3, blank=True)
    itinerary_destination = models.CharField(max_length=3, blank=True)
    itinerary_departure_time = models.CharField(max_length=5, blank=True)
    itinerary_arrival_time = models.CharField(max_length=5, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    total_price = models.FloatField(default=0.0)

    def create_(self, itinerary):

        def parse_flight_number(f_num: int) -> str:
            """ returns a string 4 in length for flight number passed """
            return (4 - len(str(f_num))) * '0' + str(f_num)

        self.main_carrier = itinerary['main_carrier']
        self.itinerary_origin = itinerary['itinerary_origin']
        self.itinerary_destination = itinerary['itinerary_destination']
        self.itinerary_departure_time = itinerary['itinerary_departure_time']
        self.currency = itinerary['currency']
        self.total_price = itinerary['total_price']

        sep = '|'

        self.flight_numbers = (sep).join(f['carrier'] + parse_flight_number(f['flight_number'])
                                  for f in itinerary['flights'])
        self.departure_airports = sep.join([f['departure_airport'] for f in itinerary['flights']])
        self.arrival_airports = sep.join([f['arrival_airport'] for f in itinerary['flights']])
        self.departure_times = sep.join([f['departure_time'] for f in itinerary['flights']])
        self.arrival_times = sep.join([f['arrival_time'] for f in itinerary['flights']])
        self.carriers = sep.join([f['carrier'] for f in itinerary['flights']])

        self.save()

    def get_json(self):
        sep = '|'
        d = model_to_dict(self, fields=[field.name for field in self._meta.fields])



        flight_count = len(self.flight_numbers.split(sep))
        d['flights'] = [{'departure_airport': self.departure_airports.split(sep)[i], 'departure_time': self.departure_times.split(sep)[i],
                                 'arrival_airport': self.arrival_airports.split(sep)[i], 'arrival_time': self.arrival_times.split(sep)[i],
                                 'carrier': self.carriers.split(sep)[i], 'flight_number': self.flight_numbers.split(sep)[i]
                        }
            for i in range(flight_count)
        ]

        return d
