
import json, requests
from . Handyman import add_days_to_date

def parse_response(http_response):
    # TODO: check if http is 200

    # version messages statistics scheduleDescs taxDescs taxSummaryDescs fareComponentDescs validatingCarrierDescs baggageAllowanceDescs legDescs
    try:
        response = json.loads(http_response.text)['groupedItineraryResponse']
    except Exception as e:
        raise Exception(f'Could not parse json:{str(e)}')

    itineraries = {}
    for itin_group in response['itineraryGroups']:
        departure_dates = []
        arrival_dates = []
        for leg_desc in itin_group['groupDescription']['legDescriptions']:
            departure_dates.append(leg_desc['departureDate'])
            arrival_dates.append('PENDING***')

        print(departure_dates)
        for itin in itin_group['itineraries']:
            itinerary = {'legs': itin['legs']}
            itineraries[itin['id'] - 1] = itinerary  # to start in 0

            for price_info in itin['pricingInformation']:
                itinerary['currency'] = price_info['fare']['totalFare']['currency']
                itinerary['total_price'] = price_info['fare']['totalFare']['totalPrice']

            flights = []
            for id, leg_id in enumerate(itin['legs']):
                schedules = response['legDescs'][leg_id['ref'] - 1]['schedules']
                print(leg_id['ref'] - 1)
                for schedule in schedules:
                    flight = response['scheduleDescs'][schedule['ref'] - 1]
                    flight_details = {'departure_airport': flight['departure']['airport'],
                                      'departure_time': flight['departure']['time'][:5],
                                      'arrival_airport': flight['arrival']['airport'],
                                      'arrival_time': flight['arrival']['time'][:5],
                                      'carrier': flight['carrier']['marketing'],
                                      'flight_number': flight['carrier']['marketingFlightNumber'],

                                      'departure_date': departure_dates[id],
                                      'arrival_date': 'empty',

                                      }

                    if 'departureDateAdjustment' in flight:
                        flight_details['departure_date'] = add_days_to_date(flight_details['departure_date'],
                                                                            flight['departureDateAdjustment'])

                    if 'dateAdjustment' in flight['departure']:
                        flight_details['departure_date'] = add_days_to_date(flight_details['departure_date'],
                                                                            flight['departure']['dateAdjustment'])

                    flight_details['arrival_date'] = flight_details['departure_date']

                    if 'dateAdjustment' in flight['arrival']:
                        flight_details['arrival_date'] = add_days_to_date(flight_details['arrival_date'],
                                                                          flight['arrival']['dateAdjustment'])

                    flights.append(flight_details)
                    itinerary['flights'] = flights

                itinerary['itin_carriers'] = '-'.join([f['carrier'] for f in flights])
                from collections import Counter
                carrier_count = Counter(c for c in itinerary['itin_carriers'].split('-'))
                count_carrier = {v: k for k, v in carrier_count.items()}
                itinerary['main_carrier'] = count_carrier[max(count_carrier.keys())]

                itinerary['itinerary_origin'] = flights[0]['departure_airport']
                itinerary['itinerary_destination'] = flights[-1]['departure_airport']
                itinerary['itinerary_departure_time'] = flights[0]['departure_time'][:5]
                itinerary['itinerary_arrival_time'] = flights[-1]['arrival_time'][:5]

    return itineraries


def get_token(url="https://api-crt.cert.havail.sabre.com/v2/auth/token", parameters={}, version='v2'):
    return 'T1RLAQLS8yzTJaFHKCoZ2Qkcz/jHW+WMTRB10L3gp0il+ogZicb2F+m+AADAuqzuwwKEPV6sedn5nsR4F5GqZBu800PhKGd7CBqILfVKRyDsEGTrcMTqKoJU99t+tTPcCeMpudKwPm1GZNgXx18NkDRRUDt8zlkH8G1L9cj0cw7LLlTvaWbWN7SsjL2rvIDPxQsMTWhiNyK2B9ABqtt/AnddM01zTiz4V+WGbnr3n1sv5gANPKwMlU9xoW8sNQBInnNREKcGCrTccwhopKiEPScygsNkkSEPL/MDelkdcr4cEyvt7qNMSOxCCnYE'
    print('Getting Token')
    user = r'8h2xrynur03b7rq5'  # parameters["user"]
    group = r'DEVCENTER'  # parameters["group"]
    domain = r'EXT'  # parameters["domain"]
    password = r'5KjfNt7W'  # parameters["password"]
    encodedUserInfo = base64.b64encode(f'V1:{user}:{group}:{domain}'.encode('ascii'))
    encodedPassword = base64.b64encode(password.encode('ascii'))
    encodedSecurityInfo = str(base64.b64encode(encodedUserInfo + ":".encode('ascii') + encodedPassword))
    print(encodedSecurityInfo)
    print(f'V1:{user}:{group}:{domain}'.encode('ascii'))

    data = {'grant_type': 'client_credentials'}
    headers = {'content-type': 'application/x-www-form-urlencoded ', 'Authorization': 'Basic ' + encodedSecurityInfo,
               'Accept-Encoding': 'gzip,deflate'}
    response = requests.post(url, headers=headers, data=data)
    if (response.status_code != 200):
        print("ERROR: I couldnt authenticate")
        print(response.text)

    token = json.loads(response.text)["access_token"]
    print(token)
    return token


# @log_search
def send_bfm(ori, des, sta, ret, options_limit=10):
    print(f'Doing Shopping{ori, des, sta, ret}')
    token = get_token()  # 'T1RLAQL4Bvkkv1JQ2rU8HInf2saIgaM1vBC7We2JvnCLhccKlragajr1AADAsX2e1mFwyY3SLG6mWfboD4Bbmfmdb7sm0aAFziwYxdfGvqk3lyoqQlDOlnJADSkDznenMKqwR1g8lmKJi8Xi54T38dK3L07X9IgpxcmqpgOPD5Rrs/+Y5UYKx0Akk/BTEEkutNoHaMgDlLMl7QUNp10+w04vV22BH2v0l95XDuTejBO+CG9dl130vkUj8zPrZFoZp7arm2l+c9KMDg70/T1ipx7IsnILZhJCxaL36RX00vTnr44WeIcrklXn2mmR';
    payload = '{"OTA_AirLowFareSearchRQ":{"OriginDestinationInformation":[{"DepartureDateTime":"2021-01-21T00:00:00",    "DestinationLocation":{"LocationCode":"TEST"},"OriginLocation":{"LocationCode":"TEST"},"RPH":"0"},{"DepartureDateTime":"2021-01-22T00:00:00","DestinationLocation":{"LocationCode":"TEST"},"OriginLocation":{"LocationCode":"TEST"},"RPH":"1"}],"POS":{"Source":[{"PseudoCityCode":"F9CE","RequestorID":{"CompanyName":{"Code":"TN"},"ID":"1","Type":"1"}}]},"TPA_Extensions":{"IntelliSellTransaction":{"RequestType":{"Name":"200ITINS"}}},"TravelPreferences":{"TPA_Extensions":{"DataSources":{"ATPCO":"Enable","LCC":"Disable","NDC":"Disable"},"NumTrips":{}}},"TravelerInfoSummary":{"AirTravelerAvail":[{"PassengerTypeQuantity":[{"Code":"ADT","Quantity":1}]}],"SeatsRequested":[1]},"Version":"1"}}'
    payload = json.loads(payload)

    payload['OTA_AirLowFareSearchRQ']['OriginDestinationInformation'][0]['OriginLocation']['LocationCode'] = ori
    payload['OTA_AirLowFareSearchRQ']['OriginDestinationInformation'][0]['DestinationLocation']['LocationCode'] = des
    payload['OTA_AirLowFareSearchRQ']['OriginDestinationInformation'][1]['OriginLocation']['LocationCode'] = des
    payload['OTA_AirLowFareSearchRQ']['OriginDestinationInformation'][1]['DestinationLocation']['LocationCode'] = ori
    payload = json.dumps(payload)

    url = "https://api-crt.cert.havail.sabre.com/v2/offers/shop"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + token}

    response = requests.post(url, headers=headers, data=payload)

    with open('static/ota/rq.txt', 'w') as rq:
        rq.write(payload)

    with open('static/ota/rs.txt', 'w') as rs:
        rs.write(response.text)

    results = parse_response(response)
    results = {k: v for k, v in results.items() if k < options_limit}
    return results
