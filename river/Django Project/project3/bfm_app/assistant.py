import os, zlib, base64, re, datetime
import numpy as np
import lxml.etree as ET
import pandas as pd
from jellyfish import levenshtein_distance
DEBUG = True

def get_matrix_distance(words_list, diagonal=True):
    M = [[[] for w in zip(words_list, words_list)] for w in zip(words_list, words_list)] #Generate Square Matrix
    for i in range(len(words_list)):
        for j in range(len(words_list)):
            if diagonal:
                if j>=i:
                    M[i][j] = levenshtein_distance(words_list[i],words_list[j]) #Fill half of it
            else: M[i][j] = levenshtein_distance(words_list[i],words_list[j]) #Fill half of it
    return M



def get_airport_details(airport_iata_list, airports_file='static/airports.csv'):
    df = pd.read_csv(airports_file, index_col=4)
    retorno = {}
    for airport_iata in airport_iata_list:
        try: retorno[airport_iata] = df.loc[airport_iata].to_dict()
        except: pass
    return retorno





def parse_mfv(file_path, DF=True):
    result = {}

    namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05'}
    file_name = file_path.split('/')[-1]
    mfv_txt = open(file_path,'r').read()
    mfv_xml = ET.fromstring(mfv_txt)


    result['ShopDateTimeStart'] = mfv_xml.attrib['ShopDateTimeStart']
    result['ShopDateTimeEnd'] = mfv_xml.attrib['ShopDateTimeEnd']
    AirItinerary_list = mfv_xml.findall('AirItinerary')

    result['options'] = []
    for AirItinerary in AirItinerary_list:
        RequestInfo = AirItinerary.find('RequestInfo',namespaces=namespaces)

        option = {}
        result['options'].append(option)
        option['ShopCount'] = AirItinerary.attrib['ShopCount']
        option['ShopTime'] = AirItinerary.attrib['ShopTime']
        #option['RequestInfo'] = RequestInfo
        option['POSCountry'] = RequestInfo.attrib['POSCountry']

        option['legs'] = []
        ItineraryLeg_list = AirItinerary.findall('ItineraryLeg',namespaces=namespaces)
        for ItineraryLeg in ItineraryLeg_list:
            leg = []
            option['legs'].append(leg)
            FlightSegment_list = ItineraryLeg.findall('FlightSegment')
            for FlightSegment in FlightSegment_list:
                flight = {}
                leg.append(flight)
                flight['Origin'] = FlightSegment.attrib['Origin']
                flight['Destination'] = FlightSegment.attrib['Destination']
                flight['CarrierCode'] = FlightSegment.attrib['CarrierCode']
                flight['FlightNumber'] = FlightSegment.attrib['FlightNumber']
                flight['DepartureDateTime'] = FlightSegment.attrib['DepartureDateTime']
                flight['ArrivalDateTime'] = FlightSegment.attrib['ArrivalDateTime']
                flight['Stops'] = FlightSegment.attrib['Stops']
                flight['BookingCode'] = FlightSegment.attrib['BookingCode']
                flight['CabinClass'] = FlightSegment.attrib['CabinClass']
                flight['SeatsRemaining'] = FlightSegment.attrib['SeatsRemaining']
                flight['MarriedFlight'] = FlightSegment.attrib['MarriedFlight']

        fare = {}
        option['fare'] = fare
        Fare = AirItinerary.find('Fare')

        fare['PassengerCode'] = Fare.attrib['PassengerCode']
        fare['PassengerNumber'] = Fare.attrib['PassengerNumber']
        fare['BaseAmount'] = Fare.attrib['BaseAmount']
        fare['TaxAmount'] = Fare.attrib['TaxAmount']
        fare['Currency'] = Fare.attrib['Currency']
        fare['Private'] = Fare.attrib['Private']
        fare['Refundable'] = Fare.attrib['Refundable']
        fare['ETicketable'] = Fare.attrib['ETicketable']

        fare['segment_list'] = []
        FareSegment_list = Fare.findall('FareSegment')
        for FareSegment in FareSegment_list:
            Start = FareSegment.attrib['Start']
            End = FareSegment.attrib['End']
            FareBasisCode = FareSegment.attrib['FareBasisCode']
            fare['segment_list'].append({'start':Start, 'end': End, 'FareBasisCode': FareBasisCode})

        fare['tax_list'] = []
        Tax_list = Fare.findall('Tax')
        for Tax in Tax_list:
            Amount = Tax.attrib['Amount']
            Code = Tax.attrib['Code']
            Currency = Tax.attrib['Currency']
            fare['tax_list'].append({'amount':Amount,'code': Code, 'currency': Currency})


    if DF:
        aux = []
        for option in result['options']:
            d = {}
            aux.append(d)
            d['ShopDateTimeStart'] = result['ShopDateTimeStart']
            d['ShopDateTimeEnd'] = result['ShopDateTimeEnd']
            d['POSCountry'] = option['POSCountry']
            d['price'] = str(float(option['fare']['BaseAmount'] ) + float( option['fare']['TaxAmount'] ))

            origins,destinations,carriers,flight_numbers,departure_datetimes,arrival_datetimes,stops,rbds,cabin,seats_remaining,marriage_ind,leg_stops_numbers = [],[],[],[],[],[],[],[],[],[],[],[]
            for leg in option['legs']:
                leg_stops_numbers.append(str(len(leg)))
                for flight in leg:
                    origins.append(flight['Origin'])
                    destinations.append(flight['Destination'])
                    carriers.append(flight['CarrierCode'])
                    flight_numbers.append(flight['FlightNumber'])
                    departure_datetimes.append(flight['DepartureDateTime'])
                    arrival_datetimes.append(flight['ArrivalDateTime'])
                    stops.append(flight['Stops'])
                    rbds.append(flight['BookingCode'])
                    cabin.append(flight['CabinClass'])
                    seats_remaining.append(flight['SeatsRemaining'])
                    marriage_ind.append(flight['MarriedFlight'])


            d['leg_stops_numbers'] = sep.join(leg_stops_numbers)
            d['origins']='|'.join(origins)
            d['destinations']='|'.join(destinations)
            d['flight_numbers']='|'.join(flight_numbers)
            d['departure_datetimes']='|'.join(departure_datetimes)
            d['arrival_datetimes']='|'.join(arrival_datetimes)
            d['stops']='|'.join(stops)
            d['rbds']='|'.join(rbds)
            d['cabin']='|'.join(cabin)
            d['seats_remaining']='|'.join(seats_remaining)
            d['marriage_ind']='|'.join(marriage_ind)
            d['itinerary'] = sep.join([c+n for (c,n) in zip(carriers , flight_numbers) ])
        print ('HERE IS YOUR DF')
        df = pd.DataFrame(aux)
        print (df)
        return df

    return result


def generate_dates(aps,loss,base_date=None):
    if base_date==None: base_date=datetime.datetime.now()
    dates = []
    for ap in aps:
        for los in loss:
            dep_date = base_date + datetime.timedelta(days=int(ap))
            ret_date = dep_date + datetime.timedelta(days=int(los))
            dates.append(str(dep_date.strftime("%Y-%m-%d"))+'/'+str(ret_date.strftime("%Y-%m-%d")))
    return dates


def payload_change(payload,parameters):
    print (parameters)
    time = 'T11:00:00'
    namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05'}
    tree_in = ET.fromstring(payload)
    OriginDestinationInformationList = tree_in.findall('ota:OriginDestinationInformation', namespaces=namespaces)

    [ob,ib] = OriginDestinationInformationList[:25]
    if 'pcc' in parameters:
        pass
    if 'origin' in parameters: ob.find('ota:OriginLocation', namespaces=namespaces).attrib["LocationCode"] = ib.find('ota:DestinationLocation', namespaces=namespaces).attrib["LocationCode"] = parameters['origin']
    if 'destination' in parameters:  ob.find('ota:DestinationLocation', namespaces=namespaces).attrib["LocationCode"] = ib.find('ota:OriginLocation', namespaces=namespaces).attrib["LocationCode"] =parameters['destination']
    if 'dep_date' in parameters: ob.find('ota:DepartureDateTime', namespaces=namespaces).text = parameters['dep_date']+time
    if 'ret_date' in parameters: ib.find('ota:DepartureDateTime', namespaces=namespaces).text = parameters['ret_date']+time

    return ET.tostring(tree_in,pretty_print=True, encoding='unicode')


class bfm_rs:

    def __init__(self, file_path):
        if DEBUG: print ('creating BFM RS')
        print (file_path)
        self.file_path = file_path


    def get_chunks(self, bfm_rs):
        #Get Chunks
        chunk_list = [x.replace('--','') for x in bfm_rs.split('--StreamingChunkBreak')]
        return chunk_list


    def save_bfm_df(self, dataframe, output_path):
        dataframe.to_csv(output_path, sep=',')


    def get_xml_from_path(self, file_path ):
        bfm_rs = open(file_path,'r').read()
        tree_in = ET.fromstring(bfm_rs)
        return tree_in


    def bfm_rs_decompress(self, bfm_xml, save_to_txt=True, file_name='decompressed.xml'):
        namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05'}
        bfm_text = bfm_xml.text
        payload = zlib.decompress(base64.b64decode(bfm_text), 16+zlib.MAX_WBITS)
        bfm_rs = ET.fromstring(payload)
        if DEBUG: print (bfm_rs)

        if save_to_txt:
            file_path='decompressed/'+file_name
            out=open(file_path+'-decompressed.xml','w')
            out.write(payload)
            out.close()
        return  bfm_rs


    def dechunk_bfm(self, chunk_list, decompress=False, file_name='1.xml',save_to_txt=True):
        namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05'}
        aux = []
        for chunk in chunk_list:
            if chunk is not '':
                bfm_rs = ET.fromstring(chunk)
                if decompress: bfm_rs = self.bfm_rs_decompress(bfm_xml, True, file_name=file_name)#Decompress
                aux.append(bfm_rs)

        rt_itineraries = aux[0].find('PricedItineraries',namespaces=namespaces)
        for b in aux[1:]:

            OneWayItineraries = aux[0].find('OneWayItineraries',namespaces=namespaces)
            if OneWayItineraries is None:
                aux[0].append(ET.fromstring('<ota:OneWayItineraries xmlns:ota="http://www.opentravel.org/OTA/2003/05"><ota:SimpleOneWayItineraries RPH="1"></ota:SimpleOneWayItineraries><ota:SimpleOneWayItineraries RPH="2" xmlns:ota="http://www.opentravel.org/OTA/2003/05"></ota:SimpleOneWayItineraries></ota:OneWayItineraries>'))
            OneWayItineraries = aux[0].find('OneWayItineraries',namespaces=namespaces) ## ota:
            ow_list = OneWayItineraries.findall('SimpleOneWayItineraries',namespaces=namespaces)
            b_OneWayItineraries = b.find('OneWayItineraries',namespaces=namespaces)
            if b_OneWayItineraries is not None:
                b_ow_list = b.find('OneWayItineraries',namespaces=namespaces)
                for ow in b_ow_list:
                    rph = int ( ow.attrib['RPH']) -1
                    ow_its =  ow.findall('PricedItinerary',namespaces=namespaces)
                    for each in ow_its:
                        ow_list[rph].append(each)

            RoundTripItineraries = b.find('PricedItineraries',namespaces=namespaces)
            if RoundTripItineraries is not None:
                RoundTripItinerary_list = RoundTripItineraries.findall('PricedItinerary',namespaces=namespaces)
                for it in RoundTripItinerary_list:
                    rt_itineraries.append(it)

        if save_to_txt:
            file_path='dechunk/'+file_name
            out=open(file_path+'-dechunked.xml','w')
            out.write(ET.tostring(aux[0], pretty_print = True))
            out.close()

        return aux[0]

    #TODEPRECATE
    def bfm_rs_to_df2(self, save=False, output_path='output_path'):
        if DEBUG: print ('bfm_rs_to_df')
        namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05', 'SOAP-ENV': 'http://schemas.xmlsoap.org/soap/envelope/'}
        compressed = chunked = json = chunked_compressed = False
        file_name = self.file_path.split('/')[-1]
        bfm_rs_ori = open(self.file_path,'r').read()
        envelope = ET.fromstring(bfm_rs_ori)
        for x in envelope:print(x)
        body = envelope.find('SOAP-ENV:Body',namespaces=namespaces)


        print (body)
        bfm_rs = ET.tostring(list(body)[0], pretty_print = True, encoding='unicode')
        print ('Remove Envelope')
        #print (bfm_rs)


        if '{' in bfm_rs_ori: json = True
        elif 'StreamingChunkBreak' in bfm_rs_ori and 'CompressedResponse' in bfm_rs: chunked_compressed = True
        elif 'StreamingChunkBreak' in bfm_rs_ori: chunked = True
        elif 'CompressedResponse' in bfm_rs_ori:  compressed = True

        if chunked_compressed:
            if DEBUG: print ('chunked_compressed')
            chunk_list = self.get_chunks(bfm_rs)
            bfm_rs = self.dechunk_bfm(chunk_list,True,file_name)
        elif chunked: #Dechunk
            if DEBUG: print ('chunked')
            chunk_list = self.get_chunks(bfm_rs)
            bfm_rs = self.dechunk_bfm(chunk_list,False,file_name)
        elif compressed: #Decompress
            if DEBUG: print ('compressed')
            bfm_rs = self.bfm_rs_decompress(ET.fromstring(bfm_rs),save_to_txt=False)
        elif json:
            print ('Json') #TODO:
            #bfm_rs = json.loads(bfm_rs)
        else:
            bfm_rs = ET.fromstring(bfm_rs)#ET.fromstring(get_xml_from_path(file_path).text)

        PricedItineraries = bfm_rs.find('ota:PricedItineraries',namespaces=namespaces)
        if DEBUG: print (PricedItineraries)
        try:
            OneWayItineraries = bfm_rs.find('ota:OneWayItineraries',namespaces=namespaces)
            SimpleOneWayItineraries_list =  OneWayItineraries.findall('ota:SimpleOneWayItineraries',namespaces=namespaces)
        except Exception as e: SimpleOneWayItineraries_list = []

        options = [PricedItineraries]+SimpleOneWayItineraries_list
        priced_itineraries = ([ options[x][y] for x in range(len(options)) for y in range(len(options[x]))] )

        di  = []
        for idx, option in enumerate(priced_itineraries):

            # ITINERARY PART
            AirItinerary = option.find('ota:AirItinerary',namespaces=namespaces)
            OriginDestinationOptions = AirItinerary.find('ota:OriginDestinationOptions',namespaces=namespaces)
            legs = OriginDestinationOptions.findall('ota:OriginDestinationOption',namespaces=namespaces)

            flight_list, flight_op_list, ElapsedTimes, booking_classes, MarriageGrps, DepartureAirports, ArrivalAirports,DepartureDateTimes, ArrivalDateTimes =[],[],[],[],[],[],[],[],[]
            for leg in legs:
                leg_flights, leg_flights_op = [],[]
                ElapsedTime = leg.attrib['ElapsedTime']

                flights = leg.findall('ota:FlightSegment',namespaces=namespaces)
                for flight in flights:
                    DepartureDateTimes.append(flight.attrib['DepartureDateTime'])
                    ArrivalDateTimes.append(flight.attrib['ArrivalDateTime'] )
                    FlightNumber, StopQuantity = flight.attrib['FlightNumber'], flight.attrib['StopQuantity']
                    try: ResBookDesigCode = flight.attrib['ResBookDesigCode']
                    except: ResBookDesigCode='n/a'

                    DepartureAirport = flight.find('ota:DepartureAirport',namespaces=namespaces).attrib['LocationCode']
                    ArrivalAirport = flight.find('ota:ArrivalAirport',namespaces=namespaces).attrib['LocationCode']
                    OperatingAirline = flight.find('ota:OperatingAirline',namespaces=namespaces).attrib['Code']
                    OperatingFlightNumber = flight.find('ota:OperatingAirline',namespaces=namespaces).attrib['FlightNumber']
                    MarketingAirline = flight.find('ota:MarketingAirline',namespaces=namespaces).attrib['Code']
                    MarriageGrp = flight.find('ota:MarriageGrp',namespaces=namespaces).text

                    leg_flights.append(MarketingAirline + (4 - len(FlightNumber))*'0'+  FlightNumber)
                    leg_flights_op.append(OperatingAirline + (4 - len(OperatingFlightNumber))*'0'+  OperatingFlightNumber)
                    booking_classes.append(ResBookDesigCode)
                    MarriageGrps.append(MarriageGrp)
                    DepartureAirports.append(DepartureAirport)
                    ArrivalAirports.append(ArrivalAirport)


                flight_list.append(leg_flights)
                flight_op_list.append(leg_flights_op)
                ElapsedTimes.append(ElapsedTime)

            ITINERARY = '--'.join(['-'.join(x) for x in flight_list])
            ITINERARY_OP = '--'.join(['-'.join(x) for x in flight_op_list])


            d = {'idx':idx, 'option_number':option.attrib['SequenceNumber'], 'itinerary':ITINERARY}
            d['DepartureAirports']='|'.join(DepartureAirports)
            d['ArrivalAirports']='|'.join(ArrivalAirports)
            d['DepartureDateTime']='|'.join(DepartureDateTimes)
            d['ArrivalDateTime']= '-'.join(ArrivalDateTimes)
            d['booking_classes']='|'.join(booking_classes)
            d['marriage_indicators']='|'.join(MarriageGrps)
            d['travel_time_list']='|'.join(ElapsedTimes)
            d['travel_time']= sum([int(x) for x in ElapsedTimes])
            d['flight_count'] = len( ITINERARY.replace('--','-').split('-') )
            d['mktg_optg_set'] = str ([x[:2]+'('+y[:2]+')' for (x, y )in zip(ITINERARY.replace('--','-').split('-'), ITINERARY_OP.replace('--','-').split('-') )] ).replace("'","")

            DepartureDateTimes = [datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S') for x in DepartureDateTimes ] # Convert to datetime object
            ArrivalDateTimes = [datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S') for x in ArrivalDateTimes ]     # Convert to datetime object
            cnx_time = [ str(int((d-a).total_seconds() / 60 )) for (d, a) in zip(DepartureDateTimes[1:], ArrivalDateTimes[:-1])]         # Get the difference in minutes
            d['cnx_time'] = '-'.join(cnx_time)

            #FARE PART
            AirItineraryPricingInfo = option.find('ota:AirItineraryPricingInfo',namespaces=namespaces)
            ItinTotalFare = AirItineraryPricingInfo.find('ota:ItinTotalFare',namespaces=namespaces)
            TotalFare = ItinTotalFare.find('ota:TotalFare',namespaces=namespaces)
            TotalFare_Amount = TotalFare.attrib['Amount']
            TotalFare_CurrencyCode = TotalFare.attrib['CurrencyCode']
            d['price'] = TotalFare_Amount
            d['currency'] = TotalFare_CurrencyCode
            Tickets = AirItineraryPricingInfo.find('Tickets',namespaces=namespaces)
            d['multi_ticket'] = str (Tickets is not None)
            TPA_Extensions = option.find('ota:TPA_Extensions',namespaces=namespaces)
            AdditionalFares = option.find('ota:TPA_Extensions',namespaces=namespaces) # OPTIONAL
            additional_prices = []
            try:
                additional_fares = AdditionalFares.findall('ota:AirItineraryPricingInfo',namespaces=namespaces)
                for AdditionalFares in additional_fares:
                    ItinTotalFare = AdditionalFares.find('ota:ItinTotalFare',namespaces=namespaces)
                    TotalFare_i = ItinTotalFare.find('ota:TotalFare',namespaces=namespaces)
                    additional_prices.append(TotalFare_i)
            except: pass
            d['additional_prices'] = additional_prices

            di.append(d)

        df = pd.DataFrame(di,index=range(len(di)))
        df['price_rank'] = df['price'].astype(float).rank(ascending=1,method='dense')
        df['time_rank'] = df['travel_time'].astype(int).rank(ascending=1,method='dense')

        df['price_time_rank'] = df['price_rank']*1000 + df['time_rank']
        if save:
            self.save_bfm_df(df, output_path)

        return df



    def bfm_rs_to_df(self, save=False, output_path='output_path',sep='|'):
        if DEBUG: print ('bfm_rs_to_df')
        namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05', 'SOAP-ENV': 'http://schemas.xmlsoap.org/soap/envelope/'}
        compressed = chunked = json = chunked_compressed = False
        file_name = self.file_path.split('/')[-1]
        bfm_rs_txt = open(self.file_path,'r').read()
        envelope = ET.fromstring(bfm_rs_txt)
        body = envelope.find('SOAP-ENV:Body',namespaces=namespaces)
        bfm_rs = ET.tostring(list(body)[0], pretty_print = True, encoding='unicode')


        if '{' in bfm_rs_txt: json = True
        elif 'StreamingChunkBreak' in bfm_rs_txt and 'CompressedResponse' in bfm_rs: chunked_compressed = True
        elif 'StreamingChunkBreak' in bfm_rs_txt: chunked = True
        elif 'CompressedResponse' in bfm_rs_txt:  compressed = True

        if chunked_compressed:
            if DEBUG: print ('chunked_compressed')
            chunk_list = self.get_chunks(bfm_rs)
            bfm_rs = self.dechunk_bfm(chunk_list,True,file_name)
        elif chunked: #Dechunk
            if DEBUG: print ('chunked')
            chunk_list = self.get_chunks(bfm_rs)
            bfm_rs = self.dechunk_bfm(chunk_list,False,file_name)
        elif compressed: #Decompress
            if DEBUG: print ('compressed')
            bfm_rs = self.bfm_rs_decompress(ET.fromstring(bfm_rs),save_to_txt=False)
        elif json:
            print ('Json') #TODO:
            #bfm_rs = json.loads(bfm_rs)
        else:
            bfm_rs = ET.fromstring(bfm_rs)#ET.fromstring(get_xml_from_path(file_path).text)

        PricedItineraries = bfm_rs.find('ota:PricedItineraries',namespaces=namespaces)
        if DEBUG: print (PricedItineraries)
        try:
            OneWayItineraries = bfm_rs.find('ota:OneWayItineraries',namespaces=namespaces)
            SimpleOneWayItineraries_list =  OneWayItineraries.findall('ota:SimpleOneWayItineraries',namespaces=namespaces)
        except Exception as e: SimpleOneWayItineraries_list = []

        options = [PricedItineraries]+SimpleOneWayItineraries_list
        priced_itineraries = ([ options[x][y] for x in range(len(options)) for y in range(len(options[x]))] )

        di  = []
        for idx, option in enumerate(priced_itineraries):

            # ITINERARY PART
            AirItinerary = option.find('ota:AirItinerary',namespaces=namespaces)
            OriginDestinationOptions = AirItinerary.find('ota:OriginDestinationOptions',namespaces=namespaces)
            legs = OriginDestinationOptions.findall('ota:OriginDestinationOption',namespaces=namespaces)

            flight_list, flight_op_list, ElapsedTimes, booking_classes, MarriageGrps, DepartureAirports, ArrivalAirports,DepartureDateTimes, ArrivalDateTimes =[],[],[],[],[],[],[],[],[]
            for leg in legs:
                leg_flights, leg_flights_op = [],[]
                ElapsedTime = leg.attrib['ElapsedTime']

                flights = leg.findall('ota:FlightSegment',namespaces=namespaces)
                for flight in flights:
                    DepartureDateTimes.append(flight.attrib['DepartureDateTime'])
                    ArrivalDateTimes.append(flight.attrib['ArrivalDateTime'] )
                    FlightNumber, StopQuantity = flight.attrib['FlightNumber'], flight.attrib['StopQuantity']
                    try: ResBookDesigCode = flight.attrib['ResBookDesigCode']
                    except: ResBookDesigCode='n/a'

                    DepartureAirport = flight.find('ota:DepartureAirport',namespaces=namespaces).attrib['LocationCode']
                    ArrivalAirport = flight.find('ota:ArrivalAirport',namespaces=namespaces).attrib['LocationCode']
                    OperatingAirline = flight.find('ota:OperatingAirline',namespaces=namespaces).attrib['Code']
                    OperatingFlightNumber = flight.find('ota:OperatingAirline',namespaces=namespaces).attrib['FlightNumber']
                    MarketingAirline = flight.find('ota:MarketingAirline',namespaces=namespaces).attrib['Code']
                    MarriageGrp = flight.find('ota:MarriageGrp',namespaces=namespaces).text

                    leg_flights.append(MarketingAirline + (4 - len(FlightNumber))*'0'+  FlightNumber)
                    leg_flights_op.append(OperatingAirline + (4 - len(OperatingFlightNumber))*'0'+  OperatingFlightNumber)
                    booking_classes.append(ResBookDesigCode)
                    MarriageGrps.append(MarriageGrp)
                    DepartureAirports.append(DepartureAirport)
                    ArrivalAirports.append(ArrivalAirport)


                flight_list.append(leg_flights)
                flight_op_list.append(leg_flights_op)
                ElapsedTimes.append(ElapsedTime)

            ITINERARY = (sep*2).join([sep.join(x) for x in flight_list])
            ITINERARY_OP = (sep*2).join([sep.join(x) for x in flight_op_list])


            d = {'idx':idx, 'option_number':option.attrib['SequenceNumber'], 'itinerary':ITINERARY}
            d['DepartureAirports']='|'.join(DepartureAirports)
            d['ArrivalAirports']='|'.join(ArrivalAirports)
            d['DepartureDateTime']='|'.join(DepartureDateTimes)
            d['ArrivalDateTime']= '|'.join(ArrivalDateTimes)
            d['booking_classes']='|'.join(booking_classes)
            d['marriage_indicators']='|'.join(MarriageGrps)
            d['travel_time_list']='|'.join(ElapsedTimes)
            d['travel_time']= sum([int(x) for x in ElapsedTimes])
            d['flight_count'] = len( ITINERARY.replace( (sep*2),sep ).split(sep) )
            d['mktg_optg_set'] = str ([x[:2]+'('+y[:2]+')' for (x, y )in zip(ITINERARY.replace((sep*2),sep).split(sep), ITINERARY_OP.replace((sep*2),sep).split(sep) )] ).replace("'","")

            DepartureDateTimes = [datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S') for x in DepartureDateTimes ] # Convert to datetime object
            ArrivalDateTimes = [datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S') for x in ArrivalDateTimes ]     # Convert to datetime object
            cnx_time = [ str(int((d-a).total_seconds() / 60 )) for (d, a) in zip(DepartureDateTimes[1:], ArrivalDateTimes[:-1])]         # Get the difference in minutes
            d['cnx_time'] = sep.join(cnx_time)

            #FARE PART
            AirItineraryPricingInfo = option.find('ota:AirItineraryPricingInfo',namespaces=namespaces)
            ItinTotalFare = AirItineraryPricingInfo.find('ota:ItinTotalFare',namespaces=namespaces)
            TotalFare = ItinTotalFare.find('ota:TotalFare',namespaces=namespaces)
            TotalFare_Amount = TotalFare.attrib['Amount']
            TotalFare_CurrencyCode = TotalFare.attrib['CurrencyCode']
            d['price'] = TotalFare_Amount
            d['currency'] = TotalFare_CurrencyCode
            Tickets = AirItineraryPricingInfo.find('Tickets',namespaces=namespaces)
            d['multi_ticket'] = str (Tickets is not None)
            TPA_Extensions = option.find('ota:TPA_Extensions',namespaces=namespaces)
            AdditionalFares = option.find('ota:TPA_Extensions',namespaces=namespaces) # OPTIONAL
            additional_prices = []
            try:
                additional_fares = AdditionalFares.findall('ota:AirItineraryPricingInfo',namespaces=namespaces)
                for AdditionalFares in additional_fares:
                    ItinTotalFare = AdditionalFares.find('ota:ItinTotalFare',namespaces=namespaces)
                    TotalFare_i = ItinTotalFare.find('ota:TotalFare',namespaces=namespaces)
                    additional_prices.append(TotalFare_i)
            except: pass
            d['additional_prices'] = additional_prices

            di.append(d)

        df = pd.DataFrame(di,index=range(len(di)))
        df['price_rank'] = df['price'].astype(float).rank(ascending=1,method='dense')
        df['time_rank'] = df['travel_time'].astype(int).rank(ascending=1,method='dense')

        df['price_time_rank'] = df['price_rank']*1000 + df['time_rank']
        if save:
            self.save_bfm_df(df, output_path)

        return df
