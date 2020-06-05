import json
from django.http import HttpResponse
from django.shortcuts import render

import requests

def error(request):
    return HttpResponse('Error')


def index(request):

    return render(request, 'ota/index.html', context={'test': 'test'})


def search(request):
    ori = request.GET.get('ori')
    des = request.GET.get('des')
    sta = request.GET.get('sta')
    ret = request.GET.get('ret')


    token = 'T1RLAQL4Bvkkv1JQ2rU8HInf2saIgaM1vBC7We2JvnCLhccKlragajr1AADAsX2e1mFwyY3SLG6mWfboD4Bbmfmdb7sm0aAFziwYxdfGvqk3lyoqQlDOlnJADSkDznenMKqwR1g8lmKJi8Xi54T38dK3L07X9IgpxcmqpgOPD5Rrs/+Y5UYKx0Akk/BTEEkutNoHaMgDlLMl7QUNp10+w04vV22BH2v0l95XDuTejBO+CG9dl130vkUj8zPrZFoZp7arm2l+c9KMDg70/T1ipx7IsnILZhJCxaL36RX00vTnr44WeIcrklXn2mmR';
    payload = """{"OTA_AirLowFareSearchRQ": {
 "OriginDestinationInformation": [{"DepartureDateTime": "2021-01-21T00:00:00", "DestinationLocation": {"LocationCode":"BUE"}, "OriginLocation": { "LocationCode":"MVD"},        "RPH": "0"      },      {        "DepartureDateTime": "2021-01-22T00:00:00",        "DestinationLocation": { "LocationCode":"MVD"},        "OriginLocation": {"LocationCode":"BUE"},        "RPH": "1"      }    ]
 ,    "POS": {      "Source": [        {          "PseudoCityCode": "F9CE",          "RequestorID": {            "CompanyName": {              "Code": "TN"            },            "ID": "1",            "Type": "1"          }        }      ]    },    "TPA_Extensions": {      "IntelliSellTransaction": {        "RequestType": {          "Name": "200ITINS"        }      }    },    "TravelPreferences": {      "TPA_Extensions": {        "DataSources": {          "ATPCO": "Enable",          "LCC": "Disable",          "NDC": "Disable"        },        "NumTrips": {}      }    },    "TravelerInfoSummary": {      "AirTravelerAvail": [        {          "PassengerTypeQuantity": [            {              "Code": "ADT",              "Quantity": 1            }          ]        }      ],      "SeatsRequested": [        1      ]    },    "Version": "1"  }}"""

    url = "https://api-crt.cert.havail.sabre.com/v2/offers/shop"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + token}

    results = json.loads( requests.post(url, headers=headers, data=payload).text)['groupedItineraryResponse']


    return render( request, 'ota/results.html', context={'ori': ori, 'des': des, 'sta': sta, 'ret':ret, 'results': results})

def return_something(request):
    return 'Something'


def results(request):
    return HttpResponse(f'Searching: {request}')
