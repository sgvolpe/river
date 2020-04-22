#@_SGV_


import csv, cx_Oracle, datetime,MySQLdb, os
from collections import OrderedDict
import pandas as pd
import pandas.io.sql as psql
from sqlalchemy import create_engine
from Oracle_Connection import Oracle_Connection
from MySQL_Connection import MySQL_Connection
from functional import function_log as function_log
from functional import timer as timer
from functional import log as log


class BAPCC:

    mysql_pcc_mapping = '''
       SELECT 
       R.pcc_code as "PCC", R.active as "Status Code",
       P.name as "PnL",
       AU.name as "Agency Using",
       AO.name as "Agency Owner",
       AP.name as "Parent Agency Name"
       FROM 
       ocean.salespcclist_relationship R

       JOIN ocean.salespcclist_agency AU
       ON R.agency_user_id = AU.id 
       JOIN ocean.salespcclist_agency AO
       ON R.agency_owner_id = AO.id 
       JOIN ocean.salespcclist_agency AP
       ON AU.id = AP.id

       JOIN ocean.salespcclist_pnl P
       ON P.id = R.pnl_id
       WHERE R.ACTIVE=1

       '''

    mysql_region_mapping = '''
       select airport_code, country_code
        from airshopping.region_hierarchy
       '''

    @timer
    def __init__(self, sql_name, parameters):
        print (parameters)
        self.create_dirs()
        self.sql_name = sql_name
        #self.parameters = {}
        self.parameters = parameters

        self.get_oracle_midt()
        self.get_mysql()
        self.process_master_df()
        try:
            self.get_current_db()
        except: pass
        self.update_db()

    @function_log
    @timer
    def create_dirs(self):
        cwd = os.getcwd()
        if 'BAPS_EXTRACTS' not in os.listdir(cwd): os.makedirs('BAPS_EXTRACTS')

    @function_log
    @timer
    def get_oracle_midt(self):
        print (' -> Connecting to Oracle MIDT Database')
        out_folder = 'BAPS_EXTRACTS'
        out_f_name = f"midt_df_{'_'.join([str(v) for k, v in self.parameters.items() if k != 'pccs']) }.csv"
        print(os.path.join(out_folder, out_f_name))
        if out_f_name in os.listdir(out_folder):
            print('Oracle DF already in Drive')
        else:
            # Execute Oracle Query
            OC = Oracle_Connection()
            OC.get_cursor()
            sql = OC.get_sql(self.sql_name, self.parameters)
            OC.run_query(sql)
            OC.save_query(f_path=os.path.join(out_folder, out_f_name))


    @function_log
    @timer
    def get_mysql(self):
        out_folder = 'BAPS_EXTRACTS'
        out_f_name = 'region_df.csv'
        if out_f_name in os.listdir(out_folder):
            print('MySQL DF already in Drive')
        else:

            mysql_connection = MySQL_Connection()
            mysql_connection.connect()
            mysql_connection.run_sql(sql=self.mysql_region_mapping, out_f_path=os.path.join(out_folder, 'region_df.csv'))
            mysql_connection.run_sql(sql=self.mysql_pcc_mapping, out_f_path=os.path.join(out_folder, 'pcc_mapping.csv'))
            mysql_connection.close_connection()

    @function_log
    @timer
    def process_master_df(self):
        out_folder = 'BAPS_EXTRACTS'

        out_f_name = f"master_df_{'_'.join([str(v) for k, v in self.parameters.items() if k != 'pccs']) }.csv"

        midt_f_name = f"midt_df_{'_'.join([str(v) for k, v in self.parameters.items() if k != 'pccs']) }.csv"
        if out_f_name in os.listdir(out_folder):
            print('Master DF already in Drive')
            self.master_df = pd.read_csv(os.path.join(out_folder,out_f_name))
        else:

            midt_df = pd.read_csv(os.path.join(out_folder, midt_f_name))
            pcc_df = pd.read_csv(os.path.join(out_folder, 'pcc_mapping.csv'))
            region_df = pd.read_csv(os.path.join(out_folder,'region_df.csv'))

            master_df = pd.merge(midt_df, pcc_df, left_on='POS_CODE', right_on='PCC', how='left')
            master_df = pd.merge(master_df, region_df, left_on='ARRIVE_AIRPORT', right_on='airport_code', how='left')
            master_df = pd.merge(master_df, region_df, left_on='BOARD_AIRPORT', right_on='airport_code', how='left',
                                 suffixes=( '-arr','-dep'))

            master_df = master_df.rename(columns=
                                         {'country_code-arr': 'arrival_country_code',
                                          'country_code-dep': 'departure_country_code',
                                          'GDS_CODE': 'gds', 'POS_CODE': 'pcc',
                                          'BOOKING_DATE': 'booking_date', 'DEPARTURE_DATE': 'departure_date',
                                          'CARRIER_CODE': 'carrier_code',
                                          'COUNTRY_CODE': 'pos',
                                          'BOARD_AIRPORT': 'board_airport', 'ARRIVE_AIRPORT': 'arrive_airport',
                                          'BOOKING_CLASS_CODE': 'rbd',
                                          'SUM(BOOKINGS_PASSENGER_COUNT)': 'gross_bookings',
                                          'SUM(CANCELS_PASSENGER_COUNT)': 'cancellations',
                                          'PNL': 'pnl', 'AGENCY_USING': 'agency_using',
                                          'AGENCY_OWNER': 'agency_owner', 'Parent Agency Name': 'parent_agency',

                                          }
                                         )

            self.master_df = master_df[['gds', 'pos', 'pcc', 'booking_date', 'departure_date',
                                   'carrier_code', 'board_airport', 'arrive_airport', 'rbd',
                                   'gross_bookings', 'cancellations',
                                   'pnl', 'agency_using', 'agency_owner', 'parent_agency',
                                   'arrival_country_code', 'departure_country_code']]

            self.master_df['unique_concat'] = self.master_df[['gds', 'pos', 'pcc', 'booking_date', 'departure_date',
                                   'carrier_code', 'board_airport', 'arrive_airport', 'rbd',
                                   'arrival_country_code', 'departure_country_code']].astype(str).apply('_'.join, axis=1)

            self.master_df['unique_concat'] = self.master_df['unique_concat'].apply(lambda x: x + '_' * (56 - len(x)) )
            #self.master_df=self.master_df.set_index('unique_concat')
            self.master_df.to_csv(os.path.join(out_folder, out_f_name), index=False)

            print(self.master_df.shape)

    @function_log
    @timer
    def get_current_db(self):
        print (' -> Getting Current DB')

        host = 'ltxw0396.sgdcelab.sabre.com'
        database = 'ocean'
        user = 'ytool'
        password = 'ytool'
        parameters = '|{host}|{database}|{user}'.format(host=host, database=database, user=user)

        db = MySQLdb.connect(host=host, user=user, passwd=password, db=database)
        out_folder = 'BAPS_EXTRACTS'
        sql = 'select * from airshopping.santi_bapcc'
        self.current_db = psql.read_sql(sql, con=db)
        self.current_db.to_csv(os.path.join(out_folder, 'current_db.csv'))

    @function_log
    @timer
    def update_db(self):
        print(' -> Update DB')
        out_folder = 'BAPS_EXTRACTS'
        self.current_db = pd.read_csv(os.path.join(out_folder, 'current_db.csv'))

        out_f_name = f"master_df_{'_'.join([str(v) for k, v in self.parameters.items() if k != 'pccs'])}.csv"
        self.master_df = pd.read_csv(os.path.join(out_folder, out_f_name))


        df = self.master_df[~self.master_df['unique_concat'].isin(list(self.current_db['unique_concat']))]

        print ('Updating DB')
        print (df.shape)
        engine = create_engine('mysql://airShopping:airShopping@ltxw0396.sgdcelab.sabre.com:3306/airShopping', echo=False)


        df.to_sql(name='santi_bapcc', con=engine, if_exists='append', index=True, chunksize=524288)

        log(log_f_folder='LOG', log_f_name='update_db.txt', to_write=f'{str(datetime.datetime.now())} | '
                                                                     f'{df.shape[0]} rows updated | {str(self.parameters)} ')
        print ('DB Updated')

# 90% Of bookings
etg_pccs = 'ATHSG38SR', '13OG', 'ATHGR28CS', 'STOSG34AA', 'ATHGR28BF', '1ADA', '4ZTH', 'SINSG38SR', 'FRASG38SR', 'OSLSG34AA', 'CPHSG34AA', 'YN4F', '9MJB', 'YN3F', '2BPB', 'A99B', 'C73B','08LA', 'HELSG34AA', 'STOSG38GB', 'STOSG38FR', 'TPESG38SR', 'AKLSG38SR', 'HKGSG38SR', 'SYDSG38SR', 'AMSSG34AA', 'TLVSG38SR', 'WQ5F', 'WQ7F'
num_ods = 1
ods_offset = 0
booking_date_from = '01-APR-2019'
booking_date_to = '01-APR-2019'

#top_onds_overall
BAPCC('oracle_etg', { 'booking_date_from': booking_date_from,'num_ods': num_ods, 'pccs': etg_pccs,
                        'booking_date_to': booking_date_to})
