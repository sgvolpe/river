__author__ = 'SGV'

from django.contrib import admin
from .models import (AccessRecord, Webpage, UserProfileInfo
                              )
admin.site.register(AccessRecord)
admin.site.register(Webpage)
admin.site.register(UserProfileInfo)
