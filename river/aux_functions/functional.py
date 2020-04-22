# __SGV__
# env=myEnv
# version=3.x


import datetime, functools, json, os, time


def log(log_f_folder, log_f_name, to_write):
    if log_f_folder not in os.listdir(os.getcwd()):
        os.makedirs(os.path.join(log_f_folder))
        log = open(os.path.join(log_f_folder, log_f_name), 'w')
        log.write('# # # LOG START # # #')
        log.close()

    log = open(os.path.join(log_f_folder, log_f_name), 'a')
    log.write(to_write + '\n')
    log.close()


def function_log(func, log_f_folder='LOG',  log_f_name='generic_log.txt'):

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        to_write = f"{datetime.datetime.now()},{start_time},{end_time},{run_time:.4f} secs,{func.__name__!r}"
        log(log_f_folder, log_f_name, to_write)

        return value

    return wrapper_timer


def get_credentials(what_for, creds_path=os.path.join('Resources', 'credentials.txt')):
    file_open = open(creds_path)
    with open(creds_path) as json_file:
        print (json_file)
        json_creds = json.load(json_file, encoding='cp1252')

    json_file.close()
    return json_creds[what_for]


def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer
    
    
import MySQLdb
import datetime, os, requests
import gzip
import pandas as pd
from sqlalchemy import create_engine
import winsound
import functools
import time


def override_hierarchy_table():
    engine = create_engine('mysql://airShopping:airShopping@ltxw0396.sgdcelab.sabre.com:3306/airShopping', echo=False)

    df = pd.read_csv(r'C:\Users\SG0216333\OneDrive - Sabre\Desktop\Location Hierarchy.csv')
    df.to_sql(name='region_hierarchy', con=engine, if_exists = 'replace', index=False, chunksize=524288)




