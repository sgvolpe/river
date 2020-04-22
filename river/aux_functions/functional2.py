


def download_dataframe(request, model_class):
    kwargs = {}
    for parameter in [p for p in request.GET if p not in ['download_all', 'bypass', 'schema'] ]:
        value = request.GET.get(parameter, None)
        if value is not None:
            kwargs['{0}'.format(parameter)] = value
    queryset = model_class.objects.filter(**kwargs)



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
