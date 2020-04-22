# __SGV__
# env=myEnv

DEBUG = True

import base64, collections, datetime, json, os, platform, random, requests, time, teradata
import pandas as pd
from  functional import get_credentials as get_credentials



class Teradata:

    def __init__(self):
        self.credentials = get_credentials('teradata')

    def run_teradata_query(self, sql_query):
        # Get Creds
        host, username, password = self.credentials['server'], self.credentials['username'], self.credentials[
            'password'],

        udaExec = teradata.UdaExec(appName=host, version="1.0", logConsole=False)
        with udaExec.connect(method="odbc", system=host, username=username,
                             password=password.replace('$', '$$')) as connect:
            df = pd.read_sql(sql_query, connect)
        print(df.shape)
        return df

    def save_query_results(self, df_to_be_saved, output_path, file_name):
        df_to_be_saved.to_csv(os.path.join(output_path, file_name))
