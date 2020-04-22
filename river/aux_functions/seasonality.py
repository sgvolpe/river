# __SGV__
# env=myEnv


import functools, os, time, winsound
import pandas as pd
from functional import timer as timer
from teradata_connection import Teradata as teradata


class Seasonality:

    def __init__(self, pos='IS', service_start_date='2019-01-01', service_end_date='2019-12-31'):
        self.pos = pos
        self.service_start_date = service_start_date
        self.service_end_date = service_end_date

    @timer
    def download_MIDT(self):
        f_name = f'full_MIDT_{self.pos}.csv'
        f_path = os.path.join('MIDT files')
        if f_name not in os.listdir(f_path):
            print('Querying MIDT')
            sql = sql_seasonality = f'''select b.SubscriberID as SubscriberID,
                b.POSCountryCd as POSCountryCd,
                b.GDSCd as GDSCd,
                b.PNRLocatorID as PNRLocatorID,
                b.ODTrue as ODTrue,

                OrigLoc.City_Cd as OrigCity,
                DestLoc.City_Cd as DestCity,
                OrigLoc.Country_Cd as OrigCountry,
                OrigLoc.Region_Cd as OrigRegion,
                DestLoc.Country_Cd as DestCountry,
                DestLoc.Region_Cd as DestRegion,

                b.OrigAirportCd as OrigAirportCd,
                b.DestAirportCd as DestAirportCd,
                b.ServiceStartDate as ServiceStartDate,
                b.TransactionDate as TransactionDate,
                b.MarketingAirlineCode as MarketingAirlineCode,

                b.GMTDepartDate as GMTDepartDate,
                b.GMTDepartTime as GMTDepartTime,
                b.PassengerCount as PassengerCount,
                b.GMTArrivalDate as GMTArrivalDate,
                b.GMTArrivalTime as GMTArrivalTime,
                b.SegmentMiles as SegmentMiles

                from GDS_VIEWS.MIDTDailyBkgByDepartDt b 

                join (select PNRLocatorID, SubscriberID, TransactionDate 
                        from GDS_VIEWS.MIDTDailyBkgByDepartDt
                        where ServiceStartDate >= '{self.service_start_date}' and ServiceStartDate <= '{self.service_end_date}'
                        and POSCountryCd= '{self.pos}'

                        Group by 1,2,3
                        ) l
                        on b.PNRLocatorID = l.PNRLocatorID
                          and b.SubscriberID = l.SubscriberID
                          and b.TransactionDate = l.TransactionDate

                join (select location_cd, city_cd, country_cd, region_cd from EDW_VIEWS.Location_Hierarchy
                group by 1,2,3,4) OrigLoc
                on substr(b.ODTrue,1,3) = OrigLoc.Location_Cd
                join (select location_cd, city_cd, country_cd, region_cd from EDW_VIEWS.Location_Hierarchy
                group by 1,2,3,4) DestLoc
                on substr(b.ODTrue,6,3) = DestLoc.Location_Cd

                Group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22 '''

            print('Connecting to TDW')
            session = connect_to_teradata()
            print('Session Obtained')
            self.midt_df = pd.read_sql_query(sql, session)

            f_name = f'full_MIDT_{self.pos}.csv'
            f_path = os.path.join('MIDT files')
            self.midt_df.to_csv(os.path.join(f_path, f_name), encoding='utf-8')
        else:
            print('using local copy')
            self.midt_df = pd.read_csv(os.path.join(f_path, f_name), encoding='utf-8')

        print('Query Finished')

        print(f'{self.midt_df.shape}')
        print(f'Number of Total Segments by Passengers: {self.midt_df["PassengerCount"].sum()}')
        # Reduce Number of Cols
        self.midt_df = self.midt_df[['SubscriberID', 'PNRLocatorID', 'TransactionDate', 'GMTDepartDate',
                                     'ODTrue', 'MarketingAirlineCode', 'OrigCountry', 'OrigRegion', 'DestCountry',
                                     'DestRegion', 'PassengerCount'
                                     ]]

        # sort by dates
        self.midt_df = self.midt_df.sort_values(by=['PNRLocatorID', 'GMTDepartDate'])
        print(f'{self.midt_df.shape}')

        self.midt_df['bound_count'] = self.midt_df.groupby(['PNRLocatorID'
                                                            ])['ODTrue'].transform('unique').apply(lambda x: len(x))

        self.midt_df['segments'] = self.midt_df.groupby(['PNRLocatorID', 'ODTrue', 'MarketingAirlineCode'
                                                         ])['PassengerCount'].transform('sum')

        #        self.midt_df['trip_type'] = self.midt
        # Deduplicate PNRs
        self.midt_df = self.midt_df.drop_duplicates(keep='first',
                                                    subset=['PNRLocatorID', 'ODTrue', 'MarketingAirlineCode'])
        print(f'{self.midt_df.shape}')

        # Calculated & add persona
        def get_persona(x):
            if int(x) == 1:
                return 'solo'
            elif int(x) == 2:
                return 'couple'
            elif int(x) >= 3:
                return 'family'
            else:
                return 'other'

        f_name = f'MIDT_{self.pos}.csv'
        f_path = os.path.join('MIDT files')
        self.midt_df['persona'] = self.midt_df['PassengerCount'].apply(get_persona)
        self.midt_df.to_csv(os.path.join(f_path, f_name), encoding='utf-8')

    @timer
    def get_MIDT(self, override_local_copy=False):
        f_name = f'MIDT_{self.pos}.csv'
        f_path = os.path.join('MIDT files')
        print(f_name)
        print(os.listdir(f_path))
        if override_local_copy or f_name not in os.listdir(f_path):
            self.download_MIDT()
        else:
            self.midt_df = pd.read_csv(os.path.join(f_path, f_name))

        self.midt_df['SubscriberID'] = self.midt_df['SubscriberID'].apply(lambda x: x.replace(r' ', ''))

    @timer
    def load_pcc_list(self):  # TODO: extract from db
        self.pcc_df = pd.read_csv('PCC List.csv')

    def run(self):
        self.get_MIDT()
        self.load_pcc_list()
        # Merge With PCC List
        self.pcc_join_df = pd.merge(self.midt_df, self.pcc_df, left_on=['SubscriberID'], right_on=['Pcc Code'],
                                    how='left')
        f_name = f'Seasonality_out_{self.pos}.csv'
        f_path = os.path.join('Seasonality Out')
        self.pcc_join_df.to_csv(os.path.join(f_path, f_name), encoding='utf-8')



def __main__(pos_list=['IS', 'SE', 'GR', 'GB', 'DE']):
    for pos in pos_list:
        try:
            S = Seasonality(pos)
            S.run()
            winsound.Beep(500, 100)
        except Exception as e:
            print(str(e))
