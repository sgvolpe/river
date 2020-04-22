# __SGV__
# env=myEnv


import csv, cx_Oracle, datetime, os
import pandas as pd

from collections import OrderedDict
from functional import get_credentials as get_credentials
from functional import timer as timer
from functional import function_log as function_log

sql_list = {


'new_query2': '''
SELECT 
    DB.COUNTRY_CODE as "pos", DB.BOOKING_DATE as "booking_date", DB.GDS_CODE AS "gds",
    DB.TRUE_AIRPP_DIR_AIRP_PAIR as "OnD", 
    DB.CARRIER_CODE as "carrier_code",DB.POS_CODE as "pcc",
    sum(DB.bookings_passenger_count) - sum(DB.CANCELS_PASSENGER_COUNT) as "net_segments"  
            
FROM DAILY_TRANSACTION_AGG DB
JOIN 
    
    (
    SELECT * FROM (
    SELECT DB2.AIRPP_DIR_AIRP_PAIR, sum(DB2.bookings_passenger_count) - sum(DB2.CANCELS_PASSENGER_COUNT) as "net_segments"   
    FROM DAILY_TRANSACTION_AGG DB2
    WHERE 
        DB2.BOOKING_DATE >=  '{from_date}' AND DB2.BOOKING_DATE <=  '{to_date}' AND DB2.COUNTRY_CODE = '{pos}'    
    GROUP BY DB2.AIRPP_DIR_AIRP_PAIR
    ORDER BY  sum(DB2.bookings_passenger_count) - sum(DB2.CANCELS_PASSENGER_COUNT) DESC    
    ) X
    WHERE ROWNUM <=100    
    ) TOP_ONDS
    ON DB.AIRPP_DIR_AIRP_PAIR =TOP_ONDS.AIRPP_DIR_AIRP_PAIR
WHERE 
    DB.BOOKING_DATE >=  '{from_date}' AND DB.BOOKING_DATE <=  '{to_date}' AND DB.COUNTRY_CODE = '{pos}'    
GROUP BY 
    DB.COUNTRY_CODE, DB.BOOKING_DATE, DB.GDS_CODE, DB.BOARD_AIRPORT, DB.ARRIVE_AIRPORT, DB.CARRIER_CODE, DB.POS_CODE
    
ORDER BY  sum(DB.bookings_passenger_count) - sum(DB.CANCELS_PASSENGER_COUNT) DESC

''',
'new_query' : '''
    
SELECT 
    DB.COUNTRY_CODE as "pos", DB.BOOKING_DATE as "booking_date", DB.GDS_CODE AS "gds",
    DB.BOARD_AIRPORT as "departure_airport", DB.ARRIVE_AIRPORT as "arrival_airport", 
    DB.CARRIER_CODE as "carrier_code",DB.POS_CODE as "pcc",
    sum(DB.bookings_passenger_count) - sum(DB.CANCELS_PASSENGER_COUNT) as "net_segments"  
            
FROM DAILY_TRANSACTION_AGG DB
JOIN 
    
    (
    SELECT * FROM (
    SELECT DB2.AIRPP_DIR_AIRP_PAIR, sum(DB2.bookings_passenger_count) - sum(DB2.CANCELS_PASSENGER_COUNT) as "net_segments"   
    FROM DAILY_TRANSACTION_AGG DB2
    WHERE 
        DB2.BOOKING_DATE >=  '01-MAR-19' AND DB2.BOOKING_DATE <=  '01-MAR-19' AND DB2.COUNTRY_CODE = 'UY'
    
    GROUP BY DB2.AIRPP_DIR_AIRP_PAIR
    ORDER BY  sum(DB2.bookings_passenger_count) - sum(DB2.CANCELS_PASSENGER_COUNT) DESC
    
    ) X
    WHERE ROWNUM <=5
    
    ) TOP_ONDS


    ON DB.AIRPP_DIR_AIRP_PAIR =TOP_ONDS.AIRPP_DIR_AIRP_PAIR

WHERE 
    DB.BOOKING_DATE >=  '01-MAR-19' AND DB.BOOKING_DATE <=  '01-MAR-19' AND DB.COUNTRY_CODE = 'UY'
    
GROUP BY 
    DB.COUNTRY_CODE, DB.BOOKING_DATE, DB.GDS_CODE, DB.BOARD_AIRPORT, DB.ARRIVE_AIRPORT, DB.CARRIER_CODE, DB.POS_CODE
    
ORDER BY  sum(DB.bookings_passenger_count) - sum(DB.CANCELS_PASSENGER_COUNT) DESC
;


''',
'pos_benchmark_group_tracked2': '''
SELECT 
    DB.COUNTRY_CODE as "pos", DB.BOOKING_DATE as "booking_date", DB.GDS_CODE AS "gds",
    DB.BOARD_AIRPORT as "departure_airport", DB.ARRIVE_AIRPORT as "arrival_airport", 
    DB.CARRIER_CODE as "carrier_code",
    sum(DB.bookings_passenger_count) - sum(DB.CANCELS_PASSENGER_COUNT) as "net_segments"   
    ,( CASE 
        WHEN DB.POS_CODE IN ('{pccs}') THEN DB.POS_CODE
        ELSE 'Not Tracked' 
        END 
    ) AS "pcc"

FROM DAILY_TRANSACTION_AGG DB
WHERE 
    DB.BOOKING_DATE >=  '{from_date}' AND DB.BOOKING_DATE <=  '{to_date}' AND DB.COUNTRY_CODE = '{pos}'

GROUP BY 
    DB.COUNTRY_CODE, DB.BOOKING_DATE, DB.GDS_CODE, DB.BOARD_AIRPORT, DB.ARRIVE_AIRPORT, DB.CARRIER_CODE ,
    ( CASE 
        WHEN DB.POS_CODE IN ('{pccs}') THEN DB.POS_CODE
        ELSE 'Not Tracked' 
        END 
    )

ORDER BY "net_segments"  DESC      

''',
'pos_benchmark_group_tracked':'''
SELECT 
    DB.COUNTRY_CODE as "pos", DB.BOOKING_DATE as "booking_date", DB.GDS_CODE AS "gds",
    DB.BOARD_AIRPORT as "departure_airport", DB.ARRIVE_AIRPORT as "arrival_airport", 
    DB.CARRIER_CODE as "carrier_code",DB.POS_CODE as "pcc", 
    sum(DB.bookings_passenger_count) - sum(DB.CANCELS_PASSENGER_COUNT) as "net_segments"   
    ,( CASE 
        WHEN DB.POS_CODE IN ('{pccs}') THEN 'Tracked'
        ELSE 'Not Tracked' 
        END 
    ) AS "PCC_GROUP"
            
FROM DAILY_TRANSACTION_AGG DB
WHERE 
    DB.BOOKING_DATE >=  '{from_date}' AND DB.BOOKING_DATE <=  '{to_date}' AND DB.COUNTRY_CODE = '{pos}'
    
GROUP BY 
    DB.COUNTRY_CODE, DB.BOOKING_DATE, DB.GDS_CODE, DB.BOARD_AIRPORT, DB.ARRIVE_AIRPORT, DB.CARRIER_CODE ,DB.POS_CODE,
    ( CASE 
        WHEN DB.POS_CODE IN ('{pccs}') THEN 'Tracked'
        ELSE 'Not Tracked' 
        END 
    )
            
ORDER BY "net_segments"  DESC      

''',

'pos_benchmark_with_pcc':'''

SELECT 
    DB.COUNTRY_CODE as "pos", DB.BOOKING_DATE as "booking_date", DB.GDS_CODE AS "gds",
    DB.BOARD_AIRPORT as "departure_airport", DB.ARRIVE_AIRPORT as "arrival_airport", 
    DB.CARRIER_CODE as "carrier_code",DB.POS_CODE as "pcc", 
    sum(DB.bookings_passenger_count) - sum(DB.CANCELS_PASSENGER_COUNT) as "net_segments"   
FROM DAILY_TRANSACTION_AGG DB
WHERE 
    DB.BOOKING_DATE >=  '{from_date}' AND DB.BOOKING_DATE <=  '{to_date}' AND DB.COUNTRY_CODE = '{pos}'
    AND DB.POS_CODE IN ('{pccs}')
GROUP BY 
    DB.COUNTRY_CODE, DB.BOOKING_DATE, DB.GDS_CODE, DB.BOARD_AIRPORT, DB.ARRIVE_AIRPORT, DB.CARRIER_CODE ,DB.POS_CODE
ORDER BY "net_segments"  DESC      

''' ,

'pos_benchmark':'''

SELECT 
    DB.COUNTRY_CODE as "pos", DB.BOOKING_DATE as "booking_date", DB.GDS_CODE AS "gds",
    DB.BOARD_AIRPORT as "departure_airport", DB.ARRIVE_AIRPORT as "arrival_airport", 
    DB.CARRIER_CODE as "carrier_code",DB.POS_CODE as "pcc", 
    sum(DB.bookings_passenger_count) - sum(DB.CANCELS_PASSENGER_COUNT) as "net_segments"   
FROM DAILY_TRANSACTION_AGG DB
WHERE 
    DB.BOOKING_DATE >=  '{from_date}' AND DB.BOOKING_DATE <=  '{to_date}' AND DB.COUNTRY_CODE = '{pos}'
GROUP BY 
    DB.COUNTRY_CODE, DB.BOOKING_DATE, DB.GDS_CODE, DB.BOARD_AIRPORT, DB.ARRIVE_AIRPORT, DB.CARRIER_CODE ,DB.POS_CODE
ORDER BY "net_segments"  DESC      

''' ,

'oracle_etg' :'''
SELECT gds_code, COUNTRY_CODE, pos_code, booking_date, departure_date, carrier_code, board_airport, Arrive_airport, booking_class_code, sum(bookings_passenger_count), sum(cancels_passenger_count)
FROM MDAIS.DAILY_TRANSACTION_AGG  A 
INNER JOIN (
    SELECT * FROM  (
        SELECT
            airpp_dir_airp_pair, sum(bookings_passenger_count) - sum(cancels_passenger_count) AS "Net Passenger Count" 
            FROM MDAIS.DAILY_TRANSACTION_AGG  DAILY_TRANSACTION_AGG
            WHERE booking_date >= '{booking_date_from}' AND booking_date <= '{booking_date_to}' 
            AND pos_code IN {pccs} 
            GROUP BY airpp_dir_airp_pair ORDER BY "Net Passenger Count"  DESC     
     )  WHERE ROWNUM <= {num_ods}
)  B  
ON A.airpp_dir_airp_pair = B.airpp_dir_airp_pair
WHERE booking_date >= '{booking_date_from}' AND booking_date <= '{booking_date_to}'  
GROUP BY
gds_code, COUNTRY_CODE, pos_code,   booking_date, departure_date, carrier_code, board_airport, Arrive_airport, booking_class_code

'''
,
'oracle_no_pcc' : '''
select gds_code, COUNTRY_CODE, pos_code,   booking_date, departure_date, carrier_code, board_airport, Arrive_airport, booking_class_code, sum(bookings_passenger_count), sum(cancels_passenger_count)
 from MDAIS.DAILY_TRANSACTION_AGG  A 
 INNER JOIN 

     ( SELECT * FROM  (
     select airpp_dir_airp_pair, sum(bookings_passenger_count) AS "COUNT"
     from MDAIS.DAILY_TRANSACTION_AGG  DAILY_TRANSACTION_AGG      
     WHERE booking_date >= '{booking_date_from}' AND booking_date <= '{booking_date_to}'     

     GROUP BY airpp_dir_airp_pair ORDER BY COUNT DESC      
     )  WHERE ROWNUM <= {num_ods}
     )  B  
 ON A.airpp_dir_airp_pair = B.airpp_dir_airp_pair
 WHERE booking_date >= '{booking_date_from}' AND booking_date <= '{booking_date_to}' 
 GROUP BY
 gds_code, COUNTRY_CODE, pos_code,   booking_date, departure_date, carrier_code, board_airport, Arrive_airport, booking_class_code
'''
}

class Oracle_Connection:
    con = None
    cur = None
    result = None
    credentials = get_credentials('oracle')
    DEBUG = True

    CONN_INFO = {
    'host': credentials['server'],
    'port': 1521,
    'user': credentials['username'],
    'psw': credentials['password'],
    'service': 'GDS',
}

    @function_log
    @timer
    def get_sql(self, sql_name, parameters):
        if self.DEBUG: print (sql_name, parameters)
        sql = sql_list[sql_name].format(**parameters)
        if self.DEBUG: print (sql)
        return sql

    @function_log
    @timer
    def get_cursor(self):
        try:
            print('Creating Cursor')
            CONN_STR = '{user}/{psw}@{host}:{port}/{service}'.format(**self.CONN_INFO)
            print (CONN_STR)
            self.con = cx_Oracle.connect(CONN_STR)
            self.cur = self.con.cursor()
            print('Cursor Created')
        except Exception as e:
            print(str(e))
            self.log(str(e))
            return None

    @function_log
    @timer
    def run_query(self, query):
        print('running query')
        self.result = self.cur.execute(query)
        self.result_df = pd.DataFrame(self.result)
        self.result_df.columns = [i[0] for i in self.cur.description]
        self.result_df
        print('query run')

    @function_log
    @timer
    def save_query(self, f_path):
        print('Saving Query')
        self.result_df.to_csv(f_path, sep=',', line_terminator='\n')
        print(f'Query Saved: {f_path}')