import datetime, functools, json, os, requests, time
from collections import OrderedDict
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table as dt
from django_plotly_dash import DjangoDash
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio
import seaborn as sns
from flask_caching import Cache


def generate_table(df):
    return dt.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in df.columns  # + [df.index.name]
            # omit the id column
            # if i != 'id'
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode='multi',
        # row_selectable='multi',
        # row_deletable=True,
        selected_rows=[],
        page_action='native',
        page_current=0,
        page_size=25,
    ),


def generate_table_simple(dataframe, include_index=True, max_rows=100):
    return html.Table(
        children=
        # Header
        [html.Tr(
            [html.Th(dataframe.index.name)] +
            [html.Th(col) for col in dataframe.columns])] +
        # Body
        [html.Tr(

            [html.Td(dataframe.index[i])] +
            [
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))],
        className='table'
    )


def generate_table2(dataframe, max_rows=350):
    print('Generating table2')
    table_header = [html.Thead
        (html.Tr(
        [html.Th(col) for col in dataframe.columns]))]  # [html.Th(dataframe.index.name, scope="col")] +
    rows = [html.Tr(children=[html.Td(dataframe.iloc[i][col]) for col in dataframe.columns]) for i
            in range(min(len(dataframe), max_rows))]  # html.Th(dataframe.index[i], scope="row")] +
    table_body = [html.Tbody(rows)]

    table = dbc.Table(table_header + table_body, bordered=True,
                      dark=True,
                      hover=True,
                      responsive=True,
                      striped=True, )
    return table


def get_live_app():
    app = DjangoDash('live_app')
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js: app.scripts.append_script({"external_url": js})

    app.layout = html.Div([
        html.Div([
            html.Iframe(src='http://www.flightradar24.com/simple_index.php?lat=49.9&lon=12.3&z=8', height=500,
                        width=1200)
        ]),

        html.Div([
            html.Pre(
                id='counter_text',
                children='Active flights worldwide:'
            ),
            dcc.Graph(id='live-update-graph', style={'width': 1200}),
            dcc.Interval(
                id='interval-component',
                interval=600000,
                n_intervals=0
            )])
    ])
    counter_list = []

    @app.callback(Output('counter_text', 'children'),
                  [Input('interval-component', 'n_intervals')])
    def update_layout(n):
        url = "https://data-live.flightradar24.com/zones/fcgi/feed.js?faa=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&stats=1  "  # airline limit
        # A fake header is necessary to access the site:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = res.json()
        counter = 0
        for element in data["stats"]["total"]:
            counter += data["stats"]["total"][element]
        counter_list.append(counter)

        try:
            df = pd.read_csv('flight_df.csv', index_col=0)

            row_df = pd.DataFrame([[str(datetime.datetime.now()), counter]], columns=['date', 'count'])
            df = df.append(row_df, ignore_index=True)
            df.to_csv('flight_df.csv')
        except Exception as e:
            print(str(e))
        # log = open('flight_log.txt', 'a')
        # log.write(f'{str(datetime.datetime.now())}|{counter}\n')
        # log.close()
        return 'Active flights worldwide: {}'.format(counter)

    @app.callback(Output('live-update-graph', 'figure'),
                  [Input('interval-component', 'n_intervals')])
    def update_graph(n):
        fig = go.Figure(
            data=[go.Scatter(
                x=list(range(len(counter_list))),
                y=counter_list,
                mode='lines+markers'
            )])
        return fig

    if __name__ == '__main__':
        app.run_server(debug=True)

    return app


def log(log_f_folder='static/analysis_app', log_f_name='stats_log.txt', to_write='# # # # # # start'):
    log = open(os.path.join(log_f_folder, log_f_name), 'a')
    log.write(to_write + '\n')
    log.close()


def try_catch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        to_write = f"{datetime.datetime.now()},{start_time},{end_time},{run_time:.4f} secs,{func.__name__!r}"
        log(to_write=to_write)
        print(f'{func.__name__}______________________No Error: {run_time}')
        return value

    try:
        return wrapper
    except Exception as e:
        raise Exception(f'Error on: {func.__name__} | {str(e)}')


DEBUG = True


class AnalysisApp:

    def __init__(self, dfs_path=os.path.join('static', 'dfs'), title='Analysis Dashboard',
                 app_name='app', callback_side='backend'):
        """
            callback_side='client' is not implemented for multiple outputs yet in dash
        """

        if DEBUG: print('AnalysisApp init')
        self.dfs_path = dfs_path
        self.title = title
        self.callback_side = callback_side
        self.app_name = app_name

        self.template = self.CHART_FONT = self.opacity = None
        self.get_style()

        # Create Dahs App
        self.app = DjangoDash('analysis_app', add_bootstrap_links=True, suppress_callback_exceptions=True)
        # self.app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
        # external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
        # for js in external_js: self.app.scripts.append_script({"external_url": js})

        # Instantiate components empty
        self.input_components, self.div_charts, self.div_tables, self.function_outputs = [], [], [], []
        self.main_inputs, self.inputs_as_output, self.function_inputs, self.parameter_inputs = [], [], [], []

        # Read Data
        self.read_data()
        if DEBUG: print(' -> Data Read')

        # Initialize Components
        self.read_input_configuration()
        self.create_input_components()
        self.create_output_components()
        self.update_inputs()
        # self.update_output()

        # Create App Layout
        self.app.layout = html.Div([
            html.H2(self.title),
            dcc.Dropdown(
                id='test',
                options=[
                    {'label': 'chart1', 'value': 'chart1'},
                    {'label': 'chart2', 'value': 'chart2'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                placeholder="Select a city",
                multi=True
            ),
            self.input_components,
            self.div_charts,
            self.div_tables,
        ], className="principal")
        # self.app.config.suppress_callback_exceptions = True

        # Cache
        # self.cache = Cache(self.app.server, config={
        #    # try 'filesystem' if you don't want to setup redis
        #    'CACHE_TYPE': 'filesystem',
        #    'CACHE_DIR': 'cache-directory'
        # })
        # self.cache.memoize(timeout=5)(self.update_output)

        # Associate callbacks
        if self.callback_side == 'backend':
            self.app.callback(inputs=self.main_inputs, output=self.inputs_as_output, )(self.update_inputs)
            self.app.callback(inputs=self.function_inputs + [Input('correlation_chart', 'selectedData')],
                              output=self.function_outputs, )(self.update_output)
            self.app.callback(
                output=[Output('chart1', component_property='style'), Output('chart2', component_property='style')]
                , inputs=[Input('test', 'value')])(self.hide_charts)

        elif self.callback_side == 'client':
            ip = ','.join(self.parameter_inputs)

            self.app.clientside_callback(
                f"""
                function({ip}) {{
                    return update_inputs({ip});
                }}
                """,
                output=self.inputs_as_output,
                inputs=self.main_inputs,
            )  # (self.update_inputs)

            self.app.clientside_callback(
                f"""
                    function({ip}) {{
                         return update_output({ip});
                    }}
                """,
                output=self.function_outputs,
                inputs=self.function_inputs,
            )  # (self.update_output)

        if DEBUG: print(' -> Layout & Callbacks Ready')

    def hide_charts(self, show_charts):
        print('@@@@@@@@@@@@@@@@')
        print(show_charts)
        retorno = []
        for chart_name in ['chart1', 'chart2']:
            if chart_name in show_charts:
                retorno.append({'display': 'block'})
            else:
                retorno.append({'display': 'none'})

        return retorno

    def get_style(self):

        conf_path = os.path.join('static', 'analysis_app', 'conf_files', f'{self.app_name}.txt')
        with open(conf_path) as json_file:
            json_conf = json.load(json_file, encoding='cp1252')

        self.charts = json_conf['charts']
        self.tables = json_conf['tables']
        self.template = json_conf['style']['template']
        self.CHART_FONT = json_conf['style']['chart_font']
        self.opacity = json_conf['style']['opacity']

        if DEBUG: print(' -> Style Ready', self.template)

    @try_catch
    def get_csv(self, df_name='test_df.csv', path='static/dfs/'):
        """
            Returns a pandas dataframe from a csv
        """
        self.df = pd.read_csv(os.path.join(path, df_name))

    @try_catch
    def read_data(self, dataframe_name=None):
        # Read data
        self.dataframes = [df_name for df_name in os.listdir(self.dfs_path)]
        if dataframe_name is None: dataframe_name = self.dataframes[0]
        self.get_csv(dataframe_name)
        self.columns_str = self.df.select_dtypes(include='object').columns
        self.columns_numeric = self.df.select_dtypes(include=['float64', 'int']).columns

    @try_catch
    def get_component(self, i, v):
        """
            Generates de dcc component based on the attributes passed
        """
        if v['control_type'] == 'dropdown':
            return html.P(
                dcc.Dropdown(
                    options=[{'label': x, 'value': x} for x in v['data']],
                    value=v['data'][0], className=v['className'], id=f'{i}',
                    persistence=True, persistence_type='local',  # local|memory
                    clearable=True, searchable=True,
                    placeholder=f"Select a {i}", disabled=False,
                )
            )
        elif v['control_type'] == 'slider':
            return html.P(
                dcc.RangeSlider(
                    id=f'{i}',
                    min=v['data']['min'],
                    max=v['data']['max'],
                    step=v['data']['step'],
                    value=v['data']['value'],
                ),
            )

    @try_catch
    def read_input_configuration(self, input_f_path=''):  # TODO: read from file
        # Create the Inputs from Configuration
        self.inputs_conf = {
            'dataframe': {'property': 'value', 'control_type': 'dropdown', 'data': self.dataframes,
                          'className': 'col-6',
                          'main_control': True},
            'categorical': {'property': 'value', 'control_type': 'dropdown', 'data': self.columns_str,
                            'className': 'col-6',
                            'main_control': False},
            'numerical': {'property': 'value', 'control_type': 'dropdown', 'data': self.columns_numeric,
                          'className': 'col-6',
                          'main_control': False},
        }

        if DEBUG: print(' -> Input Configuration Ready')

    @try_catch
    def save_input_config(self, input_f_path=''):  # TODO:
        pass

    @try_catch
    def create_input_components(self):
        self.input_components = html.Div(className='row', id='controls_div', children=[])
        self.main_inputs, self.inputs_as_output, self.function_inputs = [], [], []  # Restart Components
        self.parameter_inputs = []
        for i, v in self.inputs_conf.items():
            self.input_components.children.append(html.Div(className='col', children=[
                self.get_component(i, v)
            ]), )

            if v['main_control']:
                self.main_inputs.append(Input(i, v['property']))
            else:
                self.parameter_inputs.append(i)
                self.parameter_inputs.append(f'{i}_selected_data')
                self.function_inputs.append(Input(i, v['property']))
                # self.function_inputs.append(Input(i, 'selectedData'))

                self.inputs_as_output.append(Output(i, 'options'))
                self.inputs_as_output.append(Output(i, v['property']))

        if DEBUG: print(' -> Input Components Ready')

    @try_catch
    def create_output_components(self):
        self.function_outputs = []
        self.div_charts = html.Div(className='row', id='charts_div', children=[])

        new_row = "row"
        for chart_name in self.charts:
            self.div_charts.children.append(
                html.Div([
                    html.Div([dcc.Graph(id=chart_name, style={}), ], className="col card", id=f'{chart_name}_div'),
                ], className=f"{new_row}")
            )
            self.function_outputs.append(Output(chart_name, 'figure'))

        self.div_tables = html.Div(className='row', id='tables_div', children=[])

        for table_name in self.tables:
            self.div_tables.children.append(html.Div(id=f'{table_name}', className='col card'))
            self.function_outputs.append(Output(table_name, 'children'))

        if DEBUG: print(' -> Output Components Ready')

    @try_catch
    def update_inputs(self, dataframe_name='test_df.csv'):  # self.parameter_inputs
        """ Update the values of the Input Controls """
        self.read_data(dataframe_name=dataframe_name)
        return [{'label': col, 'value': col} for col in self.columns_str], self.columns_str[0], \
               [{'label': col, 'value': col} for col in self.columns_numeric], self.columns_numeric[0]

    @try_catch
    def get_boxplot(self, categorical_column, variable_column, df):
        try:
            names = self.df[categorical_column].unique()
            data = [
                go.Box(  # marker=dict(color=COLORS[provider],
                    opacity=self.opacity,
                    name=name, x=df[df[categorical_column] == name][categorical_column],
                    y=df[df[categorical_column] == name][variable_column]
                ) for name in names
            ]
            layout = {'legend_orientation': 'h', 'title': go.layout.Title(text=f"Distribution of {variable_column}", ),
                      'template': self.template
                      }
        except Exception as e:
            print(str(e))
            data, layout = [], {}
        return go.Figure(data=data, layout=layout)

    @try_catch
    def get_histogram(self, categorical_column, variable_column, df, x_name='sepal_length', y_name='petal_length'):
        '''try:

            names = df[categorical_column].unique()
            data = [
                dict(
                    type='scatter',
                    mode='markers',
                    x=name_df[x_name],
                    y=name_df[y_name],
                    name=name,
                ) for name_df, name in [(df[df[categorical_column] == name], name) for name in names]
            ]

            layout = {
                'title': go.layout.Title(text=f"{y_name} vs {x_name}", font=CHART_FONT),
                'xaxis': go.layout.XAxis(
                    title=go.layout.xaxis.Title(text=x_name, font=CHART_FONT)),
                'yaxis': go.layout.YAxis(
                    title=go.layout.yaxis.Title(text=y_name, font=CHART_FONT)),
                'template': template,
            }
        except: data, layout = [], {}
        return go.Figure(data=data, layout=layout)'''

        return px.histogram(df, x=variable_column, y=variable_column, color=categorical_column, marginal="box",
                            # or violin, rug
                            hover_data=self.df.columns, template=self.template)

    @try_catch
    def get_null_map(self, df, columns_numeric):
        layout = {'legend_orientation': 'h', 'title': go.layout.Title(text=f"Null Distribution", ),
                  'template': self.template
                  }
        return go.Figure(data=go.Heatmap(z=self.df[columns_numeric].isnull().astype(int).to_numpy()), layout=layout)

    @try_catch
    def generate_correlation_chart(self, categorical_column, **kwargs):

        index_vals = self.df[categorical_column].astype('category').cat.codes

        fig = go.Figure(data=go.Splom(
            dimensions=[dict(label=c, values=self.df[c]) for c in self.columns_numeric],
            text=self.df[categorical_column],
            marker=dict(color=index_vals,
                        showscale=False,  # colors encode categorical variables
                        line_color='white', line_width=0.5)
        ))

        fig.update_layout(title='Correlations', template=self.template)  # ,width=600, height=600,
        return fig

    @try_catch
    def generate_outlayers(self, categorical_column):
        # def get_outlayers(self, param='Total Unsuccessful', date=None, dataframe=None):

        D = []
        for category in self.df[categorical_column].unique():
            specific_df = self.df[self.df[categorical_column] == category]
            for feature in self.columns_numeric:
                specific_df['measuring'] = specific_df[feature]

                qv1 = specific_df[feature].quantile(0.25)
                qv3 = specific_df[feature].quantile(0.75)
                qv_limit = 1.5 * (qv3 - qv1)
                un_outliers_mask = (specific_df[feature] > qv3 + qv_limit) | (specific_df[feature] < qv1 - qv_limit)
                un_outliers_data = specific_df[feature][un_outliers_mask]
                un_outliers_name = specific_df[un_outliers_mask]

                if un_outliers_data.shape[0] > 0:
                    for i in [{'feature': feature, 'category': category, 'value': val} for val in un_outliers_data]:
                        D.append(i)

        return pd.DataFrame(D)

    @try_catch  # categorical_column, variable_column ####
    def update_output(self, categorical_column, variable_column, selected_data):

        if selected_data is None:
            self.selected_df = self.df
        else:
            selected_points = [p['pointNumber'] for p in selected_data['points']]
            self.selected_df = self.df[self.df.index.isin(selected_points)]
        print(f'LENGTH OF DATAFRAME: ')
        print(self.selected_df.shape)
        outlayers = self.generate_outlayers(categorical_column)

        kwargs = {'categorical_column': categorical_column, 'variable_column': variable_column, 'df': self.selected_df}

        output_generators = OrderedDict({
            'chart1': {'function': self.get_boxplot, 'kwargs': kwargs},
            'chart2': {'function': self.get_histogram, 'kwargs': kwargs},
            'correlation_chart': {'function': self.generate_correlation_chart, 'kwargs': kwargs},
            'get_null_map': {'function': self.get_null_map,
                             'kwargs': {'df': self.df, 'columns_numeric': self.columns_numeric}},
            'table1': {'function': generate_table_simple, 'kwargs': {'dataframe': self.df.describe().round(1)}},
            'outlayers_table': {'function': generate_table_simple, 'kwargs': {'dataframe': outlayers}},
            'full_Table': {'function': generate_table_simple, 'kwargs': {'dataframe': self.df}},

        })
        return [values['function'](**values['kwargs']) for out_name, values in output_generators.items()
                if out_name in self.charts + self.tables]

    @try_catch
    def get_app(self):
        return self.app
