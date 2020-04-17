
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'river.settings')

import django
django.setup()

import random
from faker import Faker

from hello_app.models import AccessRecord, Webpage


fakegen = Faker()



def populate(N=5):

    for entry in range(N):
        # Crate Fake Data
        fake_url = fakegen.url()
        fake_date = fakegen.date()
        fake_name = fakegen.company()

        # Create new webpage
        webpage = Webpage.objects.get_or_create(url=fake_url)[0]

        # Create fake access record
        acc_rec = AccessRecord.objects.get_or_create(name=webpage, date=fake_date)[0]



if __name__ == '__main__':
    print ('Populating Script!')
    populate()
    print ('Pop complete')