###
# Imports
import os, re, itertools, urllib, io, urllib,datetime,zlib, base64, re, datetime
import lxml.etree as ET

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn import preprocessing

from collections import OrderedDict

from matplotlib.ticker import FuncFormatter



DEBUG = True


class MichalFile:

    '''
    STEP i:
        - Open massive files from Michal analysis from input
        - for each date, for Sabre and competitor extract each combination of ond, ap, los
        - save it as a new csv on output folder
    '''
    shopping_comparison = None

    def __init__(self, shopping_comparison):
        if DEBUG: print ('Access Input Folder')
        self.shopping_comparison = shopping_comparison
        self.path = 'dashboard/static/shopping_comparison/'+ str(self.shopping_comparison.pk)
        self.input_path = self.path  +'/input'


    def log(self, text):
        log_path = self.path + '/log.txt'
        log_file = open(log_path, 'a')
        log_file.write(str( datetime.now() ) + ',' + str(text) + '\n')
        log_file.close()

    def get_alliance(self, itinerary ):
        retorno = []
        al2all = pd.read_csv('dashboard/static/alliances.csv',index_col='airline').to_dict()
        airlines = [flight[:2] for flight in itinerary.split('-')]
        for airline in airlines:

            if airline in al2all['alliance']: retorno.append( al2all['alliance'][airline] )
        else: retorno.append('na')
        return retorno

    def get_itinerary_sabre(self, legs):
        'Builds the Itinerary from Flight columns for Sabre raw data'
        ob,ib = legs[0],legs[1]
        try:
            return '-'.join([f[:2]+ (6-len(f))*'0'+f[2:] for f in ob.split(' - ')+ib.split(' - ')])
        except Exception as e:
            print ('ERROR generating ITinerary',str(e) ,legs )

    def get_itinerary_comp(self, flights):
        'Builds the Itinerary from Flight columns for competitor raw data'
        return  '-'.join([f[:2]+ (6-len(f))*'0'+f[2:] for f in flights if f!=''])

    def open_dfs(self, s_path=None,c_path=None ):
        if DEBUG: print ('''Receives a 2 Ocean raw data file set
        Returns 2 Normalized DFs one per Provider
        Open and creates extra needed columns: fare,itinerary travel time''' )

        if s_path is None:
            sdf = self.sdf
        else:
            s_cols = ['AP','LOS','market','DCXRFLIGHT','RCXRFLIGHT','TotaltravelTime','fare']
            sdf = pd.read_csv(s_path, usecols=s_cols)
        sdf['itinerary'] = sdf[[u'DCXRFLIGHT','RCXRFLIGHT']].apply(self.get_itinerary_sabre,axis=1)

        if c_path is None:
            cdf = self.sdf
        else:
            c_cols=['AP','LOS','MARKET','KEY_OUT1','KEY_OUT2','KEY_OUT3','KEY_IN1','KEY_IN2','KEY_IN3','TOTALTRAVELTIME','PRICE']
            cdf = pd.read_csv(c_path, sep=';', usecols=c_cols)
        cdf = cdf.fillna('')
        if 'KEY_OUT3' in cdf.keys() and 'KEY_IN3' in cdf.keys() :
            cdf['itinerary'] = cdf[['KEY_OUT1','KEY_OUT2','KEY_OUT3','KEY_IN1','KEY_IN2','KEY_IN3']].apply(self.get_itinerary_comp,axis=1)
        else:
            cdf['itinerary'] = cdf[['KEY_OUT1','KEY_OUT2','KEY_IN1','KEY_IN2']].apply(self.get_itinerary_comp,axis=1)


        #Cleaning of Columns and renaming
        sdf.dropna(subset=['TotaltravelTime'], inplace=True)
        sdf['travel_time'] = sdf[u'TotaltravelTime'].astype(str)
        cdf['travel_time'] = cdf[u'TOTALTRAVELTIME']
        cdf.rename(columns={'PRICE':'fare'}, inplace=True)
        cdf.rename(columns={'MARKET':'ond'}, inplace=True)
        sdf.rename(columns={'market':'ond'}, inplace=True)
        sdf['ap_los'] = sdf['AP'].astype(str) +'_'+sdf['LOS'].astype(str)
        cdf['ap_los'] = cdf['AP'].astype(str) +'_'+cdf['LOS'].astype(str)
        sdf = sdf[['itinerary','ap_los','ond','travel_time','fare']]
        cdf = cdf[['itinerary','ap_los','ond','travel_time','fare']]

        return [sdf,cdf]

    def generate_id_list(self, configuration_file_name='configuration.csv' ):
        qid_list=[]
        DF = pd.read_csv(self.path+'/'+configuration_file_name, sep=',') # Used to extract ap,los, onds

        if DEBUG: print ('Generate a concatenation of valid pos, search_dates, ap, los and onds' )
        DF['qid'] = DF['dates'].astype(str) + '_' + DF['ond']+ '_' + DF['ap'].astype(str) + '_' + DF['los'].astype(str) #TODO: if not done
        qid_list = list ( DF['qid'].unique() )
        if DEBUG: print (' I will need to generate ' + str(len( qid_list )) + ' files.')
        self.log(' I will need to generate ' + str(len( qid_list )) + ' files.')
        return qid_list

    def filter_df(self, sdf, cdf, ap_los=None, ond=None, num_options=None, truncate_to_min=False):     #,search_date


        if ap_los is not None:
            sdf = sdf[(sdf['ap_los'] == ap_los ) ]
            cdf = cdf[(cdf['ap_los'] == ap_los ) ]
        if ond is not None:
            sdf = sdf[(sdf['ond'] == ond) ]
            cdf = cdf[(cdf['ond'] == ond ) ]

        if truncate_to_min:
            num_options = min(sdf.shape[0], cdf.shape[0])
        if num_options is not None:
            sdf=sdf[:num_options]
            cdf=cdf[:num_options]
        if DEBUG: print (sdf.shape[0], cdf.shape[0] )
        return [sdf,cdf]

    # STEP i
    def generate_ind_files(self, override_files=True):
        'Input: list of ids, combination of pos, search date, ap, los and ond'
        files_created = 0
        control_date = '' # Used for controlling if need to open new df or keep using the same as before

        id_list = self.generate_id_list()
        for q_id in id_list:
            s_date,ond,ap,los = q_id.split('_')
            folder = self.path + '/input/'
            ap_los = ap + '_' + los
            #try:
            file_name = s_date + '_' + ond + '_' + ap + '_' + los + '.csv'
            #Control wether the file exists already so to avoid repeating the same task
            if file_name not in os.listdir(self.path + '/query_files/'):
                if ( s_date !=  control_date) :
                    [s_df, c_df] = self.open_dfs(folder+'sabre_'+s_date+'.csv',folder+'competitor_'+s_date+'.csv')
                #Update both control variables
                control_date = s_date

                # Filter dataframes based on id
                [S, C] = self.filter_df(s_df, c_df, ap_los, ond, truncate_to_min=True)

                #Create new DF which will be saved as to new individual file
                S['provider'] = 'sabre'
                C['provider'] = 'competitor'
                S['search_date'] = s_date
                C['search_date'] = s_date
                S['ond'] = ond
                C['ond'] = ond

                SC = pd.concat([S,C])
                #SC =process_SC(SC)
                output_path = self.path + '/query_files/'+ file_name #s_date+'_'+ond+'_'+ap+'_'+los + '.csv'
                #Control wether the file exists already so to avoid repeating the same task
                if override_files:
                    pd.DataFrame(SC).to_csv(output_path, sep=',')
                elif not os.path.exists(output_path):
                    pd.DataFrame(SC).to_csv(output_path, sep=',')

                else: pass #print 'File exist already.'
                files_created+=1
                #print 'Processed ',str(files_created), ' of ', str(len(qid_list))

            #except Exception as e: print (str(e))
        self.log(' '+ str(files_created) + ' files created. ')

    # STEP ii
    def advanced_processing(self):
        if DEBUG: print ('Advanced Processing')
        self.log(' Start of Advanced Processing')

        folder = self.path + '/query_files/'
        output_path = self.path + '/output/'
        for f in os.listdir(folder):
            f_name = f.split('.')[0]
            if DEBUG: print (f_name)

            if f_name + '-processed.csv' in os.listdir(output_path): pass
            else:
                df = pd.read_csv(folder + f )
                if df.shape[0] != 0:

                    df["is_duplicate"] = df.duplicated(subset=['itinerary'],keep=False)
                    df['price_rank_abs'] = df['fare'].rank(ascending=1,method='dense')
                    df['time_rank_abs'] = df['travel_time'].rank(ascending=1,method='dense')
                    df['price_rank'] = df.groupby('provider')['fare'].rank(ascending=1,method='dense')
                    df['time_rank'] = df.groupby('provider')['travel_time'].rank(ascending=1,method='dense')

                    # Split based on provider to later merge
                    sdf = df[ df['provider'] == 'sabre' ]
                    cdf = df[ df['provider'] != 'sabre' ]

                    #Merge of content from both providers based on itinerary
                    result = pd.merge(sdf, cdf, how='outer', on=['itinerary', 'itinerary'] ,suffixes=['_sabre','_competitor'] )

                    #CLEANING:
                    sdf = cdf =  None


                    result.fillna('')
                    result['fare_difference'] = (result['fare_sabre']-result['fare_competitor'])/result['fare_sabre']
                    result['search_date'] = result[['search_date_sabre', 'search_date_competitor']].astype(str).apply(lambda x: ''.join(x).replace('nan','')[:8], axis=1)
                    result['ap_los'] = result[['ap_los_sabre', 'ap_los_competitor']].astype(str).apply(lambda x: ''.join(x).replace('nan',''), axis=1)
                    result['ond'] = result[['ond_sabre', 'ond_competitor']].astype(str).apply(lambda x: ''.join(x).replace('nan','')[:6], axis=1)
                    result['provider'] = result[['provider_sabre', 'provider_competitor']].astype(str).apply(lambda x: '_'.join(x), axis=1)
                    result.drop(['provider_competitor','provider_sabre' ],axis=1,inplace=True)
                    result['provider'] = result['provider'].apply(lambda x: {'sabre_competitor':'both','sabre_nan':'sabre_unique','nan_competitor':'competitor_unique'}[x])
                    result['alliance'] = result['itinerary'].apply(lambda x: self.get_alliance(x))
                    result['itinerary_carrier'] = result['itinerary'].apply(lambda x: '-'.join (sorted(list(set([flight[:2] for flight in x.split('-')]))) ))
                    result['time_rank_abs'] = result['time_rank_abs_sabre']

                    result2= result[['search_date','ond','ap_los','provider','itinerary',
                                     'fare_sabre','fare_competitor','fare_difference',
                                    'travel_time_sabre','travel_time_competitor',
                                     'price_rank_abs_sabre','price_rank_abs_competitor',
                                     'time_rank_sabre', 'time_rank_competitor',
                                     'time_rank_abs_sabre','itinerary_carrier'
                                    ]]

                    result2.to_csv(output_path + f_name + '-processed.csv', sep=',')

                    #print (output_path + f_name + '-processed.csv')

        self.log(' End  of Advanced Processing')

    # STEP iii
    def process_summary(self):
        dicts = []
        input_dir = self.path + '/output/'
        output_path = self.path
        print (self.path)
        for file_path in os.listdir(input_dir):
            file_name = file_path.split('.')[0]
            di = {'file_name': file_name}
            print ('Processing: ', file_name)

            df = pd.read_csv(input_dir + file_path, sep=',')

            #Split based on provider
            sabre_options = df[df['provider'].str.contains('sabre')]
            competitor_options = df[df['provider'].str.contains('competitor')]

            di['ond'] = df['ond'][0]
            di['ap_los'] = df['ap_los'][0]
            di['search_date'] = df['search_date'][0]

            # Mean and STD Fare
            di['competitor_fare_mean']=competitor_options['fare_competitor'].mean()
            di['sabre_fare_mean']=sabre_options['fare_sabre'].mean()
            di['competitor_fare_std']=competitor_options['fare_competitor'].std()
            di['sabre_fare_std']=sabre_options['fare_sabre'].std()


            #Get cheapest option per provider
            try:di['competitor_cheapest']=competitor_options.loc[competitor_options['fare_competitor'].idxmin()]['fare_competitor']
            except: di['competitor_cheapest'] = 1.0
            try:di['sabre_cheapest']=sabre_options.loc[sabre_options['fare_sabre'].idxmin()]['fare_sabre']
            except: di['sabre_cheapest'] = 1.0

            di['lfe_fare_difference'] = (di['competitor_cheapest'] - di['sabre_cheapest'] ) / di['competitor_cheapest']

            if di['lfe_fare_difference'] == 0:  di['lfe'] = 'tie'
            elif di['lfe_fare_difference'] > 0: di['lfe'] = 'sabre'
            elif di['lfe_fare_difference'] < 0: di['lfe'] = 'competitor'



             #Get travel time mean and std
            di['competitor_time_mean']=competitor_options['travel_time_competitor'].mean()
            di['sabre_time_mean_sabre'] = sabre_options['travel_time_sabre'].mean()
            di['competitor_time_std']=competitor_options['travel_time_competitor'].std()
            di['sabre_time_std']=sabre_options['travel_time_sabre'].std()


            di['sabre_time_max'] = sabre_options['travel_time_sabre'].max()
            di['sabre_time_min'] = sabre_options['travel_time_sabre'].min()
            di['competitor_time_max']  = competitor_options['travel_time_competitor'].max()
            di['competitor_time_min']  = competitor_options['travel_time_competitor'].min()

            if di['competitor_time_min']- di['sabre_time_min'] == 0:  di['quickest'] = 'tie'
            elif di['competitor_time_min']- di['sabre_time_min'] > 0: di['quickest'] = 'sabre'
            elif di['competitor_time_min']- di['sabre_time_min'] < 0: di['quickest'] = 'competitor'


            di['sabre_only'] = 0
            di['competitor_only'] = 0
            di['both'] = 0
            try:
                di['sabre_only'] = dict(df['provider'].value_counts() )['sabre_unique']
            except Exception: pass
            try:
                di['competitor_only'] = dict( df['provider'].value_counts() )['competitor_unique']
            except Exception: pass
            try: di['both'] = dict( df['provider'].value_counts() )['both']
            except Exception: pass
            try:di['overlap']= di['both']*100.0 / (di['sabre_only'] + di['competitor_only'] - di['both']*2)
            except Exception: di['overlap'] = 100

            di['sabre_min_carrier'] = dict( sabre_options.groupby(['itinerary_carrier'])['fare_sabre'].min() )
            di['competitor_min_carrier'] = dict( competitor_options.groupby(['itinerary_carrier'])['fare_competitor'].min() )


            di['sabre_cxr_div'] = len (di['sabre_min_carrier'].keys() )
            di['competitor_cxr_div'] = len (di['competitor_min_carrier'].keys() )




            if di['competitor_cxr_div']- di['sabre_cxr_div'] == 0:  di['cxr_div'] = 'tie'
            elif di['competitor_cxr_div']- di['sabre_cxr_div'] > 0: di['cxr_div'] = 'sabre'
            elif di['competitor_cxr_div']- di['sabre_cxr_div'] < 0: di['cxr_div'] = 'competitor'

            dicts.append(di)


        out_df = pd.DataFrame(dicts)
        out_df.to_csv(output_path + '/summary.csv' )



class Ancillaries:
    ## Parameters
    ancillary_list = ['Seats', 'Baggage', 'Lounge', 'Meals', 'Pets']#, 'Medical']
    gds_list = ['sabre', 'amadeus']#, 'travelport']
    what_to_graph = ['sabre+amadeus', 'sabre+travelport', 'sabre+amadeus+travelport']
    gds_dfs = {}
    master_df = None
    bookings_df = None


    def __init__(self, pk, ancillary_list, gds_list, what_to_graph, bookings_file):
        if DEBUG: print ('Starting Ancillaries analysis')
        self.ancillary_list = ancillary_list
        self.gds_list = gds_list
        self.what_to_graph = what_to_graph
        self.bookings_file = bookings_file
        self.pk = pk

        # Load GDS content
        if DEBUG: print ('Loading GDS Content')
        if DEBUG: print ('GDS List: ', str(gds_list))
        self.sabre_loc = 'https://www.sabretravelnetwork.com/airmerchandising/export.php'
        self.amadeus_loc = 'https://merchandising.amadeus.com/export?type=csv'
        self.travelport_loc = None #amadeus_loc  # 'Travelport.csv'
        self.gds_data_loc = {'sabre': self.sabre_loc, 'amadeus': self.amadeus_loc, 'travelport': self.travelport_loc}

        self.load_data(self.gds_data_loc, self.bookings_file)
        self.bookings_df.columns = ['Bookings']

        if 'sabre' in self.gds_list:
            self.master_df = self.gds_dfs['sabre']
            aux = {}
            for k in list(self.master_df): aux[k] = k + '_sabre'

        self.master_df.rename(columns=aux, inplace=True)
        if 'amadeus' in self.gds_list:
            a_df = self.gds_dfs['amadeus']
            a_df=a_df.groupby(a_df.index).sum()
            pd.DataFrame(a_df).to_csv('adf.csv', sep=',')
            aux = {}
            for k in list(a_df): aux[k] = k + '_amadeus'
            a_df.rename(columns=aux, inplace=True)
            self.master_df = self.master_df.join(a_df, how='outer' )

        if 'travelport' in self.gds_list:
            t_df = self.gds_dfs['travelport']
            aux = {}
            for k in list(t_df): aux[k] = k + '_travelport'
            t_df.rename(columns=aux, inplace=True)
            self.master_df = self.master_df.join(t_df).fillna(0)

        self.master_df = self.master_df.fillna(0)
        if DEBUG: print (self.master_df)

    #TODO: def graph_booking_complementary(


    def import_df(self, doc_location):
        if(doc_location[:4]=='http'):
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({'https': "sg0216333:Cactus@123@www-ad-proxy.sabre.com:80"}))
            urllib.request.install_opener(opener)
            document = urllib.request.urlopen(doc_location)
        else:
            document = doc_location
        return document

    ##Loading Data
    def process_sabre_df(self, doc_location):
        'Processing Sabre DF'
        document = self.import_df(doc_location)
        df = pd.read_csv(document, index_col=1)
        df = df.fillna(0).replace('Y', 1).replace('Yes', 1).replace('No', 0).replace(' ', 0).replace('N', 0).replace('P', 0)
        df.drop([x for x in list(df) if x not in self.ancillary_list], axis=1, inplace=True)
        if DEBUG: print ('Sabre content loaded correctly. ')
        return df #.drop_duplicates(keep='first')

    def process_amadeus_df(self,doc_location):
        'Processing Amadeus DF'
        document = self.import_df(doc_location)
        df = pd.read_csv(document, index_col=1)
        df = df.fillna(0)

        df = df != 0
        df = df * 1  # replace(True, 1).replace(False, 0)
        df.rename(columns={'Company': 'Carrier', 'Seats': 'Seats', 'Unaccompanied minor': 'Unaccompanied Travel',
                           'Meals': 'Meals', 'Lounge Access': 'Lounge', 'Medical assistance': 'Medical',
                           'Family Couch with In-flight Entertainment': 'In-Flight Entertainment',
                           'Extra Bag': 'Baggage', 'Pets in Cabin': 'Pets'}, inplace=True)
        df.drop([x for x in list(df) if x not in self.ancillary_list], axis=1, inplace=True)
        if DEBUG: print ('Amadeus content loaded correctly. ')
        return df #.drop_duplicates(keep='first')

    # TODO: get the link
    def process_travelport_df(self, doc_location):
        'Processing Travelport DF'
        doc_location=r'C:\Users\sg0216333\Desktop\Django Project\project3\static\Travelport.csv'
        if DEBUG: print ('Processing Travelport Data@: ', doc_location)
        document = self.import_df(doc_location)
        df = pd.read_csv(document, index_col=1)
        df = df.fillna(0).replace('Y', 1).replace('Yes', 1).replace('No', 0).replace(' ', 0).replace('N', 0).replace('P', 0)
        df.drop([x for x in list(df) if x not in self.ancillary_list], axis=1, inplace=True)
        if DEBUG: print ('Travelport content loaded correctly. ')
        if DEBUG: print (df.index)
        #if DEBUG:   print (df.drop_duplicates(subset=df.index,keep='first'))
        #return df.drop_duplicates(keep='first')
        return df

    def load_bookings(self, bookings_loc):
        try:
            return pd.read_csv( bookings_loc , index_col=0 )
        except Exception as e:
            if DEBUG: print ('There is an error parsing booking data', str(e))


    def load_data(self, gds_data_loc, bookings_loc=None):
        'Retrieves GDS and Bookings data creates the Dataframes Standarizes and put together'

        for gds in self.gds_list:
            if gds == 'sabre':
                self.gds_dfs['sabre'] = self.process_sabre_df(gds_data_loc['sabre'])
            elif gds == 'amadeus':
                self.gds_dfs['amadeus'] = self.process_amadeus_df(gds_data_loc['amadeus'])
            elif gds == 'travelport':
                self.gds_dfs['travelport'] = self.process_travelport_df(gds_data_loc['travelport'])

        self.bookings_df = self.load_bookings(bookings_loc)
        if DEBUG: print ('content loaded correctly. ')
        if DEBUG: print ('='*55)

    def get_carrier_count(self,percentage=False):
        'Count of Carriers Offering Ancillaries per GDS'
        if DEBUG: print ('='*55)
        if DEBUG: print ('Count of Carriers Offering Ancillaries per GDS')
        master1_sum = self.master_df.sum()

        df = pd.DataFrame.from_records([(k.split('_')[0], k.split('_')[1], v) for k, v in master1_sum.iteritems()], columns=['ANC', 'GDS', 'count'])

        #Create or if doesn't exist the directory
        directory = 'dashboard/static/ancillaries_comparison/'+str(self.pk)
        if DEBUG: print (directory)
        if not os.path.exists(directory): os.makedirs(directory)
        pd.DataFrame(master1_sum).to_csv(directory+'/master1_sum.csv', sep=',')
        if DEBUG: print ('Carrier Count calc done correctly', str(percentage))
        if DEBUG: print (df)
        if DEBUG: print ('='*55)
        if DEBUG: print ()
        return df



    def get_booking_count(self,percentage=False):
        'Number of Potential Bookings Coverage per GDS'
        if DEBUG: print ('*-'*55)
        if DEBUG: print ('Number of Potential Bookings Coverage per GDS')
        total_bookings = 100
        if percentage: total_bookings = self.bookings_df['Bookings'].sum()

        master2_sum = self.master_df.multiply( self.bookings_df['Bookings'], axis='index').sum() * 100.0 / total_bookings

        master2_sum_bookings=self.master_df.join(self.bookings_df, how='outer' )

        #Create or if doesn't exist the directory
        directory = 'dashboard/static/ancillaries_comparison/'+str(self.pk)
        #if not os.path.exists(directory): os.makedirs(directory)

        if DEBUG: print (self.bookings_df['Bookings'])
        pd.DataFrame(self.bookings_df['Bookings']).to_csv(directory+'/bookings.csv', sep=',')
        pd.DataFrame(self.master_df).to_csv(directory+'/master.csv', sep=',')
        pd.DataFrame(master2_sum_bookings).to_csv(directory+'/master2_sum_bookings.csv', sep=',')
        pd.DataFrame(master2_sum).to_csv(directory+'/master2_sum.csv', sep=',')


        if DEBUG: print ('Booking Count calc done correctly', str(percentage))
        if DEBUG: print ('='*55)
        if DEBUG: print ()

        final_df = pd.DataFrame.from_records([ (k.split('_')[0],k.split('_')[1], v) for k,v in master2_sum.iteritems()],columns=['ANC','GDS','count'])
        print (final_df)



        return final_df


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
    time = 'T11:00:00'
    namespaces = {'ota': 'http://www.opentravel.org/OTA/2003/05'}
    tree_in = ET.fromstring(payload)
    OriginDestinationInformationList = tree_in.findall('ota:OriginDestinationInformation', namespaces=namespaces)
    [ob,ib] = OriginDestinationInformationList[:25]
    if 'pcc' in parameters:pass
    if 'origin' in parameters: ob.find('ota:OriginLocation', namespaces=namespaces).attrib["LocationCode"] = ib.find('ota:DestinationLocation', namespaces=namespaces).attrib["LocationCode"] = parameters['origin']
    if 'destination' in parameters:  ob.find('ota:DestinationLocation', namespaces=namespaces).attrib["LocationCode"] = ib.find('ota:OriginLocation', namespaces=namespaces).attrib["LocationCode"] =parameters['destination']
    if 'dep_date' in parameters: ob.find('ota:DepartureDateTime', namespaces=namespaces).text = parameters['dep_date']+time
    if 'ret_date' in parameters: ib.find('ota:DepartureDateTime', namespaces=namespaces).text = parameters['ret_date']+time
    return ET.tostring(tree_in,pretty_print=True, encoding='unicode')


class bfm_rs:

    def __init__(self, file_path):
        if DEBUG:print ('creating BFM RS: '+file_path)
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
        bfm_rs = ET.tostring(list(body)[0], pretty_print = True, encoding='unicode')

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
            d['ond'] = parameters['origin'] + '-' + parameters['destination']
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



    def bfm_rs_to_df(self, save=False, output_path='output_path',sep='|',parameters={'ond':'error'}):
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

        try:
            OneWayItineraries = bfm_rs.find('ota:OneWayItineraries',namespaces=namespaces)
            SimpleOneWayItineraries_list =  OneWayItineraries.findall('ota:SimpleOneWayItineraries',namespaces=namespaces)
        except Exception as e: SimpleOneWayItineraries_list = []
        options = [PricedItineraries]+SimpleOneWayItineraries_list
        try:
            priced_itineraries = ([ options[x][y] for x in range(len(options)) for y in range(len(options[x]))] )
        except Exception as e:
            priced_itineraries = []
            print (str(e))
            print ('Error on reading priced Itineraries on priced_itineraries = ([ options[x][y] for x in range(len(options)) for y in range(len(options[x]))] )')
            print (options)
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

            d['ond'] = parameters['origin']+'-'+parameters['destination']
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
        try:df['price_rank'] = df['price'].astype(float).rank(ascending=1,method='dense')
        except: df['price_rank'] = 'n/a'
        try:df['time_rank'] = df['travel_time'].astype(int).rank(ascending=1,method='dense')
        except: df['time_rank'] = 'n/a'
        try:df['price_time_rank'] = df['price_rank']*1000 + df['time_rank']
        except: df['price_time_rank'] = 'n/a'
        if save:
            self.save_bfm_df(df, output_path)
        return df
