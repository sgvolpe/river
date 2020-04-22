# __SGV__
# env=myEnv

import MySQLdb, os
from functional import get_credentials as get_credentials
from functional import function_log as function_log
import pandas as pd
import pandas.io.sql as psql

class MySQL_Connection:

    def __init__(self):
        self.credentials = get_credentials('mysql')
        self.host = self.credentials['server']
        self.port = self.credentials['port']
        self.user = self.credentials['username']
        self.password = self.credentials['password']
        self.database = self.credentials['database']
        self.connection = None
        self.results_df = None

    @function_log
    def connect(self):
        self.connection = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.database)

    @function_log
    def run_sql(self, sql='', out_f_path=None):
        self.results_df = psql.read_sql(sql, con=self.connection)
        if out_f_path is not None:
            self.results_df.to_csv(out_f_path)

    @function_log

    def close_connection(self):
        self.connection.close()