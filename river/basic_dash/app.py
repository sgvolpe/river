

import datetime, json, os, requests

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from django_plotly_dash import DjangoDash

import plotly.express as px

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objs as go
import plotly.io as pio
import seaborn as sns

def generate_table(df):
    return dt.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in df.columns #+ [df.index.name]
            # omit the id column
            #if i != 'id'
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode='multi',
        #row_selectable='multi',
        #row_deletable=True,
        selected_rows=[],
        page_action='native',
        page_current= 0,
        page_size= 25,
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
    print ('Generating table2')
    table_header = [ html.Thead(html.Tr( [html.Th(col) for col in dataframe.columns])) ] #[html.Th(dataframe.index.name, scope="col")] +
    rows = [ html.Tr(children=[html.Td(dataframe.iloc[i][col]) for col in dataframe.columns]) for i
             in range(min(len(dataframe), max_rows)) ] # html.Th(dataframe.index[i], scope="row")] +
    table_body = [html.Tbody(rows)]

    table = dbc.Table(table_header + table_body, bordered=True,
    dark=True,
    hover=True,
    responsive=True,
    striped=True,)
    return table

def get_simple_example():
    app = DjangoDash('simple_example',add_bootstrap_links=True)   # replaces dash.Dash
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js:
        app.scripts.append_script({"external_url": js})

    app.layout = html.Div(
        children=[
            html.Div([
                html.Div(['1123'], className="col"),
                html.Div(['12312'], className="col"),
                html.Div(['234234'], className="col"),
            ], className="row")

        ],className="container"
    )


    if __name__ == '__main__':
        app.run_server(debug=True)

    return app

def get_app2():
    app = DjangoDash('app2')

    df = pd.DataFrame({'num_legs': [2, 4, 8, 0],
                       'num_wings': [2, 0, 0, 0],
                       'num_specimen_seen': [10, 2, 1, 8],
                       'name': ['falcon', 'dog', 'spider', 'fish']},
                      index=[1,2,3,4])

    print(df)
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js","https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js:
        app.scripts.append_script({"external_url": js})

    app.layout = html.Div(
        html.Div([
            html.Div([
                html.Div(children=[
                    html.H1(children='A'),
                ],className='row'),
                html.Div([
                    html.Div([
                        html.A(['Print PDF'],className="button no-print print",style={}),
                        html.H3('Choose Provider:'),
                    ],className='six columns'),
                    html.Div([dcc.Graph(id='graph-1')], className= 'twelve columns', style={}),


                ],className='row', style={'margin-top': '10'}),

            ], className="row"),

            html.Div(
                [
                html.Div([dcc.Graph(figure=go.Figure(),id='overlap_pie-graph')], className= 'six columns'),
                html.Div([dcc.Graph(id='violin-graph')], className= 'six columns'),
            ], className="ten columns"),

            html.Div([
                html.Div([
                        html.H3('Itinerary Table'),
                        dt.DataTable(
                            id='table',
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df.to_dict('records'),
                        ),

                    ], className="twelve columns"),
            ], style={'width': '100%', 'font-size': '0.8em'})

        ], className='ten columns offset-by-one')
    )

    if __name__ == '__main__':
        app.run_server(debug=True)

    return app


def get_stock_app():
    app = DjangoDash('stock_app')
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js","https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js: app.scripts.append_script({"external_url": js})
    # read a .csv file, make a dataframe, and build a list of Dropdown options
    nsdq = pd.read_csv('static/dfs/NASDAQcompanylist.csv')
    nsdq.set_index('Symbol', inplace=True)
    options = []
    for tic in nsdq.index:
        options.append({'label':'{} {}'.format(tic,nsdq.loc[tic]['Name']), 'value':tic})


    app.layout = html.Div([
        html.H1('Stock Ticker Dashboard'),
        html.Div([
            html.H3('Select stock symbols:', style={'paddingRight': '30px'}),
            # replace dcc.Input with dcc.Options, set options=options
            dcc.Dropdown(
                id='my_ticker_symbol',
                options=options,
                value=['TSLA'],
                multi=True
            )
            # widen the Div to fit multiple inputs
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}),
        html.Div([
            html.H3('Select start and end dates:'),
            dcc.DatePickerRange(
                id='my_date_picker',
                min_date_allowed=datetime.datetime(2015, 1, 1),
                max_date_allowed=datetime.datetime.today(),
                start_date=datetime.datetime(2018, 1, 1),
                end_date=datetime.datetime.today()
            )
        ], style={'display': 'inline-block'}),
        html.Div([
            html.Button(
                id='submit-button',
                n_clicks=0,
                children='Submit',
                style={'fontSize': 24, 'marginLeft': '30px'}
            ),
        ], style={'display': 'inline-block'}),
        dcc.Graph(
            id='my_graph',
            figure={
                'data': [
                    {'x': [1, 2], 'y': [3, 1]}
                ]
            }
        )
    ])

    @app.callback(
        Output('my_graph', 'figure'),
        [Input('submit-button', 'n_clicks')],
        [State('my_ticker_symbol', 'value'),
         State('my_date_picker', 'start_date'),
         State('my_date_picker', 'end_date')])
    def update_graph(n_clicks, stock_ticker, start_date, end_date):
        start = datetime.datetime.strptime(start_date[:10], '%Y-%m-%d')

        end = datetime.datetime.strptime(end_date[:10], '%Y-%m-%d')
        # since stock_ticker is now a list of symbols, create a list of traces
        traces = []
        for tic in stock_ticker:
            df = web.DataReader(tic, 'yahoo', start, end)
            traces.append({'x': df.index, 'y': df.Close, 'name': tic})
        fig = {
            # set data equal to traces
            'data': traces,
            # use string formatting to include all symbols in the chart title
            'layout': {'title': ', '.join(stock_ticker) + ' Closing Prices'}
        }
        return fig

    if __name__ == '__main__':
        app.run_server(debug=True)

    return app


def get_live_app():
    app = DjangoDash('live_app')
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js: app.scripts.append_script({"external_url": js})

    app.layout = html.Div([
        html.Div([
            html.Iframe(src='http://www.flightradar24.com/simple_index.php?lat=49.9&lon=12.3&z=8', height=500, width=1200)
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
        url = "https://data-live.flightradar24.com/zones/fcgi/feed.js?faa=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&stats=1"# airline limit
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
        except Exception as e: print(str(e))
        #log = open('flight_log.txt', 'a')
        #log.write(f'{str(datetime.datetime.now())}|{counter}\n')
        #log.close()
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


def get_app(app_name):
    return {
        'analys_df_app': get_analys_df_app(),
        'stock_app': get_stock_app(),
        'simple_example': get_simple_example(),
        'linear_regression': get_linear_regression(),
    }[app_name]

def get_analys_df_app():
    app = DjangoDash('analys_df_app', add_bootstrap_links=True)
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js: app.scripts.append_script({"external_url": js})

    def get_csv(path='static/dfs/test_df.csv'):
        return pd.read_csv(path)

    #COLORS = {'Alternate': '#E50000', 'Baseline': '#3399CC', 'Common': '#31B98E'}

    df = get_csv()

    columns_str = df.select_dtypes(include='object').columns
    columns_numeric = df.select_dtypes(include=['float64', 'int']).columns

    template = 'seaborn'

    inputs = [Input('fixed-column', 'value'),Input('column', 'value')]
    outputs = []

    div_charts = html.Div(className='row', id='charts_div', children=[

    ])

    charts = ['chart1', 'chart2', 'correlation_chart']
    for chart_name in charts:
        div_charts.children.append(html.Div([dcc.Graph(id=chart_name, style={}), ],
                                            className="col-6", id=f'{chart_name}_div'),)
        outputs.append(Output(chart_name, 'figure'))

    outputs.append(Output('table1', 'children'))
    outputs.append(Output('outlayers_table', 'children'))
    outputs.append(Output('full_Table', 'children'))

    div_charts.children.append(html.Div(id='table1', className='col-6'))
    div_charts.children.append(html.Div(id='outlayers_table', className='col-6'))
    div_charts.children.append(html.Div(id='full_Table', className='col-6'))

    # Layout
    app.layout = html.Div([
        #html.Div(children=dcc.Loading(type="circle", id='dynamic_controls', color='red', children=[
            html.Hr(),
            html.Div(className='row', id='controls_div', children=[

                html.Div(className='col', children=[
                    html.H3('Metric'),
                    html.P(
                        dcc.Dropdown(
                            options=[{'label': col, 'value': col} for col in columns_numeric],
                            value=columns_numeric[0],
                            className='col-6',
                            id='fixed-column'
                        )
                        # , style={'display': 'none'}
                    )
                ]),
                html.Div(className='col', children=[
                    html.H3('Variable'),
                    html.P(
                        dcc.Dropdown(
                            options=[{'label': col, 'value': col} for col in columns_str],
                            value=columns_str[0],
                            className='col-6',
                            id='column'
                        )
                        # , style={'display': 'none'}
                    ),
                ])
            ]),
            div_charts,

        #                                  ])),

    ], className="principal")



    def get_chart1(column, fixed_column):
        names = df[fixed_column].unique()
        data = [
            go.Box(  # marker=dict(color=COLORS[provider], opacity=OPACITY),
                name=name, x=df[df[fixed_column] == name][fixed_column],
                y=df[df[fixed_column] == name][column]
            ) for name in names
        ]
        return go.Figure(data=data, layout={'legend_orientation': 'h','title': go.layout.Title(text=f"Distribution of {column}",),
                                            'template': template})


    def get_chart2(column, fixed_column, x_name='sepal_length', y_name='petal_length'):
        names = df[fixed_column].unique()

        data = [
            dict(
                type='scatter',
                mode='markers',
                x=name_df[x_name],
                y=name_df[y_name],
                name=name,
            ) for name_df, name in [(df[df[fixed_column] == name], name) for name in names]
        ]
        CHART_FONT = dict(family="inherit", size=15#, color=colors['chart-title']
                                 )

        layout = {
            'title': go.layout.Title(text=f"{y_name} vs {x_name}", font=CHART_FONT),
            'xaxis': go.layout.XAxis(
                title=go.layout.xaxis.Title(text=x_name, font=CHART_FONT)),
            'yaxis': go.layout.YAxis(
                title=go.layout.yaxis.Title(text=y_name, font=CHART_FONT)),
            'template': template,
        }
        return go.Figure(data=data, layout=layout)

    def generate_correlation_chart(fixed_column):

        index_vals = df[fixed_column].astype('category').cat.codes

        fig = go.Figure(data=go.Splom(
            dimensions=[dict(label=c, values=df[c]) for c in columns_numeric],

            text=df[fixed_column],
            marker=dict(color=index_vals,
                        showscale=False,  # colors encode categorical variables
                        line_color='white', line_width=0.5)
        ))

        fig.update_layout(
            title='Iris Data set',
            width=600,
            height=600,
        )

        return fig

    def generate_outlayers(fixed_column):
        #def get_outlayers(self, param='Total Unsuccessful', date=None, dataframe=None):

        D = []
        for category in df[fixed_column].unique():
            specific_df = df[df[fixed_column] == category]
            for feature in columns_numeric:
                specific_df['measuring'] = specific_df[feature]

                qv1 = specific_df[feature].quantile(0.25)
                qv3 = specific_df[feature].quantile(0.75)
                qv_limit = 1.5 * (qv3 - qv1)
                un_outliers_mask = (specific_df[feature] > qv3 + qv_limit) | (specific_df[feature] < qv1 - qv_limit)
                un_outliers_data = specific_df[feature][un_outliers_mask]
                un_outliers_name = specific_df[un_outliers_mask]

                if un_outliers_data.shape[0] >0 :
                    for i in [{'feature': feature, 'category': category, 'value': val} for val in un_outliers_data]:
                        D.append(i)

        return pd.DataFrame(D)



    @app.callback(outputs, inputs)
    def update_charts(column, fixed_column):
        try:
            generate_outlayers(fixed_column)
            chart1, chart2 = get_chart1(column=column, fixed_column=fixed_column), get_chart2(column=column, fixed_column=fixed_column)
            table1 = generate_table_simple(df.describe().round(1))
            outlayers = generate_outlayers(fixed_column)
            outlayers_table = generate_table_simple(outlayers)
            correlation_chart = generate_correlation_chart(fixed_column)
            full_Table = generate_table_simple(df)
            return [chart1, chart2, correlation_chart, table1, outlayers_table,full_Table]
        except Exception as e: return [f'Error: {str(e)}' for i in outputs]

    if __name__ == '__main__':
        try:
            app.run_server(debug=True)
        except Exception as e: return f'Error: {str(e)}'
    print('APP LOADED')

    return app


def get_linear_regression():
    app = DjangoDash('linear_regression', add_bootstrap_links=True)
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js: app.scripts.append_script({"external_url": js})

    df_path = os.path.join('static/dfs/USA_Housing.csv')
    USAhousing = pd.read_csv(df_path)

    features = ['Avg. Area Income', 'Avg. Area House Age', 'Avg. Area Number of Rooms',
               'Avg. Area Number of Bedrooms', 'Area Population']
    variable = ['Price']

    columns_str = USAhousing.select_dtypes(include='object').columns
    columns_numeric = USAhousing.select_dtypes(include=['float64', 'int']).columns



    div_charts = html.Div(className='row', id='charts_div', children=[])
    div_tables = html.Div(className='row', id='tables_div', children=[])

    charts = {'my_graph': {'className': 'col-6', 'style': {}},
              'correlation_graph': {'className': 'col-12', 'style': {}},
              }
    outputs = []
    for chart_name, settings in charts.items():
        div_charts.children.append(html.Div([dcc.Graph(id=chart_name, style=settings['style']), ], className=settings['className'], id=f'{chart_name}_div'), )
        outputs.append(Output(chart_name, 'figure'))

    tables = ['table1']
    for table_name in tables:
        div_tables.children.append(html.Div(id=f'{table_name}', className='col-6'))
        outputs.append(Output(table_name, 'children'))

    app.layout = html.Div([
        # html.Div(children=dcc.Loading(type="circle", id='dynamic_controls', color='red', children=[
        html.Hr(),
        html.Div(className='row', id='controls_div', children=[
            html.H1('Linear Regression Model'),

            html.Div(className='col', children=[
                html.H3('Metric'),
                html.P(
                    dcc.Dropdown(
                        options=[{'label': col, 'value': col} for col in columns_numeric],
                        value=columns_numeric[0],
                        className='col-6',
                        id='fixed-column'
                    )
                    # , style={'display': 'none'}
                )
            ]),
            html.Div(className='col', children=[
                html.H3('Variable'),
                html.P(
                    dcc.Dropdown(
                        options=[{'label': col, 'value': col} for col in columns_str],
                        value=columns_str[0],
                        className='col-6',
                        id='column'
                    )
                    # , style={'display': 'none'}
                ),
                html.Button(
                    id='submit-button',
                    n_clicks=0,
                    children='Submit',
                    style={'fontSize': 24, 'marginLeft': '30px'}
                ),
            ])
        ]),
        div_charts,
        div_tables,

        #                                  ])),

    ], className="principal")



    inputs = [Input('submit-button', 'n_clicks'), ]


    @app.callback(outputs, inputs)
    def update_outputs(n_clicks):
        print('Generating Output')

        return get_charts()

    def generate_correlation_chart(df):
        #index_vals = df[fixed_column].astype('category').cat.codes

        fig = go.Figure(data=go.Splom(
            dimensions=[dict(label=c, values=df[c]) for c in columns_numeric],

         #   text=df[fixed_column],
            marker=dict(#color=index_vals,
                        #showscale=False,  # colors encode categorical variables
                        line_color='white', line_width=0.5)
        ))

        fig.update_layout(
            title='Iris Data set',
            width=600,
            height=600,
        )

        return fig

    def get_charts():
        print ('getting')
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression
        from sklearn import metrics

        X = USAhousing[['Avg. Area Income', 'Avg. Area House Age', 'Avg. Area Number of Rooms',
                        'Avg. Area Number of Bedrooms', 'Area Population']]
        y = USAhousing['Price']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=101)

        lm = LinearRegression()
        lm.fit(X_train, y_train)
        coeff_df = pd.DataFrame(lm.coef_, X.columns, columns=['Coefficient'])
        predictions = lm.predict(X_test)

        #sns.distplot((y_test-predictions),bins=50);

        print('MAE:', metrics.mean_absolute_error(y_test, predictions))
        print('MSE:', metrics.mean_squared_error(y_test, predictions))
        print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, predictions)))

        fig = go.Figure(
            data=[go.Scatter(
                x=y_test,
                y=predictions,
                mode='markers',#'lines+markers'
            )])
        return [fig, generate_correlation_chart(USAhousing), generate_table_simple(coeff_df)]

    if __name__ == '__main__':
        try:
            print ('loading')

            app.run_server(debug=True)
        except Exception as e:
            print ('error')
            return f'Error: {str(e)}'
    print('APP LOADED')

    return app


def read_flight_radar(path='static/dfs/flight_radar24_example.csv'):
    with open(path) as json_file:
        json_data = json.load(json_file)
        del json_data['full_count']
        del json_data['version']
        del json_data['stats']

    keys, rows = json_data.keys(), [row[11:14] for row in json_data.values()]
    df = pd.DataFrame(rows, index=keys, columns=['ori', 'des', 'fln'])
    print (df.shape)

    print (df.ori)
    df.to_csv('test.csv')


#read_flight_radar()

def test():
    df = pd.read_csv('flight_df.csv', index_col=0)


    row_df = pd.DataFrame([[str(datetime.datetime.now()), 10]], columns=['date', 'count'])
    df = df.append(row_df, ignore_index=True)

    df.to_csv('flight_df.csv')












