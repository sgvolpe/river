import os, zlib,base64, re
import numpy as np
import lxml.etree as ET
import pandas as pd




#Decompress
#Concatenate
# parse





def get_chunks(bfm_rs):    
    #Get Chunks
    chunk_list = [x.replace('--','') for x in bfm_rs.split('--StreamingChunkBreak')]
    return chunk_list
        

      
def save_bfm_df(dataframe, output_path):
    dataframe.to_csv(output_path, sep=',')
    

def get_xml_from_path(file_path ):    
    bfm_rs = open(file_path,'r').read()    
    tree_in = ET.fromstring(bfm_rs)
    return tree_in


def bfm_rs_decompress(bfm_xml, save_to_txt=True, file_name='decompressed.xml'):
    namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05'}    
    
    bfm_text = bfm_xml.text
    payload = zlib.decompress(base64.b64decode(bfm_text), 16+zlib.MAX_WBITS)
    bfm_rs = ET.fromstring(payload)
    
    if save_to_txt:
        file_path='decompressed/'+file_name
        out=open(file_path+'-decompressed.xml','w')
        out.write(payload)
        out.close()
    return  bfm_rs


def dechunk_bfm(chunk_list, decompress=False, file_name='1.xml',save_to_txt=True):
    namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05'}  
    aux = []
    for chunk in chunk_list:
        if chunk is not '':           
            bfm_rs = ET.fromstring(chunk)        
            if decompress: bfm_rs = bfm_rs_decompress(bfm_xml, True, file_name=file_name)#Decompress
            aux.append(bfm_rs)
    
    
    rt_itineraries = aux[0].find('ota:PricedItineraries',namespaces=namespaces)    
    for b in aux[1:]:

        
        
        OneWayItineraries = aux[0].find('ota:OneWayItineraries',namespaces=namespaces) 
        if OneWayItineraries is None:            
            aux[0].append(ET.fromstring('<ota:OneWayItineraries xmlns:ota="http://www.opentravel.org/OTA/2003/05"><ota:SimpleOneWayItineraries RPH="1"></ota:SimpleOneWayItineraries><ota:SimpleOneWayItineraries RPH="2" xmlns:ota="http://www.opentravel.org/OTA/2003/05"></ota:SimpleOneWayItineraries></ota:OneWayItineraries>'))            
        OneWayItineraries = aux[0].find('ota:OneWayItineraries',namespaces=namespaces) ## ota:            
        ow_list = OneWayItineraries.findall('ota:SimpleOneWayItineraries',namespaces=namespaces)
        b_OneWayItineraries = b.find('ota:OneWayItineraries',namespaces=namespaces)
        if b_OneWayItineraries is not None:
            b_ow_list = b.find('ota:OneWayItineraries',namespaces=namespaces)
            for ow in b_ow_list:
                rph = int ( ow.attrib['RPH']) -1
                ow_its =  ow.findall('ota:PricedItinerary',namespaces=namespaces)
                for each in ow_its:                      
                    ow_list[rph].append(each)


            
        RoundTripItineraries = b.find('ota:PricedItineraries',namespaces=namespaces)
        if RoundTripItineraries is not None:
            RoundTripItinerary_list = RoundTripItineraries.findall('ota:PricedItinerary',namespaces=namespaces)
            for it in RoundTripItinerary_list:
                rt_itineraries.append(it)
           
    if save_to_txt:
        file_path='dechunk/'+file_name
        out=open(file_path+'-dechunked.xml','w')
        out.write(ET.tostring(aux[0], pretty_print = True))
        out.close()
   
        
        
    return aux[0]
    
      
def bfm_rs_parse(bfm_rs):
    pass

def bfm_rs_to_df(file_path):
    namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05'}     
    compressed = False
    chunked = False
    json = False
    chunked_compressed=False

    file_name = file_path.split('/')[-1]
    #Read path
    bfm_rs = open(file_path,'r').read()           

    if '{' in bfm_rs: json = True
    elif 'StreamingChunkBreak' in bfm_rs and 'CompressedResponse' in bfm_rs: chunked_compressed = True
    elif 'StreamingChunkBreak' in bfm_rs: chunked = True
    elif 'CompressedResponse' in bfm_rs:  compressed = True

    if chunked_compressed:        
        chunk_list = get_chunks(bfm_rs)        
        bfm_rs = dechunk_bfm(chunk_list,True,file_name)   
    elif chunked: #Dechunk
        chunk_list = get_chunks(bfm_rs)        
        bfm_rs = dechunk_bfm(chunk_list,False,file_name)   
    elif compressed: #Decompress
        print 'compressed'
        bfm_rs = bfm_rs_decompress(ET.fromstring(bfm_rs))
    elif json:
        print 'Json'
        return 'error'
        
        #bfm_rs = json.loads(bfm_rs)
        
    else:
        bfm_rs = ET.fromstring(bfm_rs)#ET.fromstring(get_xml_from_path(file_path).text)      
    
    PricedItineraries = bfm_rs.find('ota:PricedItineraries',namespaces=namespaces)
    try:
        OneWayItineraries = bfm_rs.find('ota:OneWayItineraries',namespaces=namespaces)
        SimpleOneWayItineraries_list =  OneWayItineraries.findall('ota:SimpleOneWayItineraries',namespaces=namespaces)        
    except Exception as e:
        print 'Dont worry theres no ow',str(e)
        SimpleOneWayItineraries_list = []
       
    options = [PricedItineraries]+SimpleOneWayItineraries_list
    priced_itineraries = ([ options[x][y] for x in range(len(options)) for y in range(len(options[x]))] )

    di  = []
    for idx, option in enumerate(priced_itineraries):
        
        # ITINERARY PART
        AirItinerary = option.find('ota:AirItinerary',namespaces=namespaces)
        OriginDestinationOptions = AirItinerary.find('ota:OriginDestinationOptions',namespaces=namespaces)
        legs = OriginDestinationOptions.findall('ota:OriginDestinationOption',namespaces=namespaces)

        flight_list = []
        ElapsedTimes=[]
        for leg in legs:
            ElapsedTime = leg.attrib['ElapsedTime']
            flights = leg.findall('ota:FlightSegment',namespaces=namespaces)
            aux = []
            rbds = []
            MarriageGrps = []
            for flight in flights:
                
                DepartureDateTime = flight.attrib['DepartureDateTime']
                ArrivalDateTime = flight.attrib['ArrivalDateTime']
                FlightNumber = flight.attrib['FlightNumber']
                try: ResBookDesigCode = flight.attrib['ResBookDesigCode']
                except: ResBookDesigCode='n/a'
                StopQuantity = flight.attrib['StopQuantity']

                DepartureAirport = flight.find('ota:DepartureAirport',namespaces=namespaces).attrib['LocationCode']
                ArrivalAirport = flight.find('ota:ArrivalAirport',namespaces=namespaces).attrib['LocationCode']
                OperatingAirline = flight.find('ota:OperatingAirline',namespaces=namespaces).attrib['Code']
                MarketingAirline = flight.find('ota:MarketingAirline',namespaces=namespaces).attrib['Code']
                MarriageGrp = flight.find('ota:MarriageGrp',namespaces=namespaces).text
                
                flightNumber =  (4 - len(FlightNumber))*'0'+  FlightNumber
                aux.append(MarketingAirline + flightNumber)

                rbds.append(ResBookDesigCode)
                MarriageGrps.append(MarriageGrp)
                
            flight_list.append(aux)
            ElapsedTimes.append(ElapsedTime)

        ITINERARY = '--'.join(['-'.join(x) for x in flight_list])
   
        

        d = {'idx':idx, 'option_number':option.attrib['SequenceNumber'], 'itinerary':ITINERARY}
        d['DepartureAirport']=DepartureAirport
        d['ArrivalAirport']=ArrivalAirport
        d['DepartureDateTime']=DepartureDateTime
        d['ArrivalDateTime']=ArrivalDateTime
        d['booking_classes']='-'.join(rbds)
        d['marriage_indicators']='-'.join(MarriageGrps)
        d['travel_time']='-'.join(ElapsedTimes)
        

        #FARE PART
        
        AirItineraryPricingInfo = option.find('ota:AirItineraryPricingInfo',namespaces=namespaces)
        ItinTotalFare = AirItineraryPricingInfo.find('ota:ItinTotalFare',namespaces=namespaces)
        TotalFare = ItinTotalFare.find('ota:TotalFare',namespaces=namespaces)
        TotalFare_Amount = TotalFare.attrib['Amount']
        TotalFare_CurrencyCode = TotalFare.attrib['CurrencyCode']


        d['price'] = TotalFare_Amount
        d['currency'] = TotalFare_CurrencyCode


        Tickets = AirItineraryPricingInfo.find('ota:Tickets',namespaces=namespaces)

        d['multi_ticket'] = Tickets is not None



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

    
            
                
                
    return df
        
    
    
    

    
def create_dfs():
    payload_folder = 'BFM_payloads/'
    files = os.listdir(payload_folder)
    file_count = len(files)
    print 'Need to process ' , str(file_count) , 'files.'

    for file_name in files:
        print file_name
        [origin,d_date,repeat,itins_chunk,streaming,payload_rq,destination,r_date,method] = file_name.split('_')    
        file_base_name = file_name.split('/')[-1].split('.')[0]
        output_path = 'BFM DFS/'+file_base_name+'.csv'
        dataframe = bfm_rs_to_df(payload_folder+file_name)
        if type(dataframe) is not str:
            save_bfm_df(dataframe, output_path)



folder = 'BFM DFS/'

fi_list =  os.listdir(folder)


def process_dfs(df1_name,df2_name):
    df1 = pd.read_csv(df1_name)
    df2 = pd.read_csv(df2_name)
    di = []
    itinerary1 = list(df1['itinerary'])
    itinerary2 = list(df2['itinerary'])


    for it in itinerary1:
        di.append({'f_name':df1_name,'itinerary':it})
    for it in itinerary2:
        di.append({'f_name':df2_name,'itinerary':it})
    df = pd.DataFrame(di)

    df.to_csv('cases/'+df1_name+'.csv', sep=',')
    
    common_itins  = len( [ it for it in itinerary1 if it     in itinerary2 ] )
    unique_itins1 = len( [ it for it in itinerary1 if it not in itinerary2 ] )
    unique_itins2 = len( [ it for it in itinerary2 if it not in itinerary1 ] )
    retorno = {'common_itins':common_itins,'unique_itins1':unique_itins1,'unique_itins2':unique_itins2}
    print  common_itins*2+unique_itins2+unique_itins1 == len(itinerary1) + len(itinerary2)
    
    return retorno
    
    
    
    


def compare_results():
    aux = []
    while(len(fi_list) >0):
        
        fi = fi_list[0]
        [origin,d_date,repeat,itins_chunk,streaming,payload_rq,destination,r_date,method] = fi.split('_')    
        if streaming == 'Y':streaming2 = 'N'
        else : streaming2 = 'Y'
        fi2 = '_'.join([origin,d_date,repeat,itins_chunk,streaming2,payload_rq,destination,r_date,method])
        print fi
        print fi2
        if fi in fi_list and fi2 in fi_list:
            d = process_dfs(folder+fi,folder+fi2)
            d['f_name1']=fi
            d['f_name2']=fi2
            aux.append(d)
        try:
            fi_list.remove(fi)
        except Exception as e: print str(e)
        try: 
            fi_list.remove(fi2)
        except Exception as e: print str(e)
        print len(fi_list)
    df = pd.DataFrame(aux)

    df.to_csv('output.csv', sep=',')



create_dfs()
compare_results()