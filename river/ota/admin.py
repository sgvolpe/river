__author__ = 'SGV'

from django.contrib import admin
from .models import (Search, Itinerary
                              )
admin.site.register(Search)
admin.site.register(Itinerary)

