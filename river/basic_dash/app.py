

import datetime, json, requests

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from django_plotly_dash import DjangoDash
import plotly.graph_objs as go

import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objs as go
import plotly.io as pio

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

def get_simple_example():
    app = DjangoDash('simple_example')   # replaces dash.Dash
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js:
        app.scripts.append_script({"external_url": js})

    app.layout = html.Div(['algo',

    ])

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
                    html.Div([dcc.Graph(id='graph-1')], className= 'twelve columns', style={'height':'500px'}),


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
        print (start)
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
        'analys_df_app':get_analys_df_app()
    }[app_name]

def get_analys_df_app():
    app = DjangoDash('analys_df_app')
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js: app.scripts.append_script({"external_url": js})

    def get_csv(path='static/dfs/test_df.csv'):
        return pd.read_csv(path)

    #COLORS = {'Alternate': '#E50000', 'Baseline': '#3399CC', 'Common': '#31B98E'}

    df = get_csv()
    print (type(df.describe()))

    columns = df.columns

    inputs = [Input('fixed-column', 'value'),Input('column', 'value')]
    outputs = [Output('chart1', 'figure'), Output('chart2', 'figure'), Output('table1', 'children'), ]
    template = 'seaborn'

    app.layout = html.Div([
        html.Hr(),
        html.Div([
            html.Div([
                    html.H4('Controls'),
                        html.P(

                            dcc.Dropdown(
                                options=[{'label': col, 'value': col} for col in columns],
                                value='',
                                className='col-6',
                                id='fixed-column'
                            )
                            # , style={'display': 'none'}
                        ),
                        ],className='col'),
            html.Div([
                      html.H4('Controls'),
                      html.P(
                          dcc.Dropdown(
                              options=[{'label': col, 'value': col} for col in columns],
                              value='',
                              className='col-6',
                              id='column'
                          )
                          # , style={'display': 'none'}
                      ),
                  ]),
        ], className="row"),
        html.Div([
            html.H3('Charts'),
            html.Div(["Chart1", dcc.Graph(id='chart1', style={'width': 1200}),], className="col", id='chart1_div'),
            html.Div(["Chart2", dcc.Graph(id='chart2', style={'width': 1200}),], className="col", id='chart2_div'),
            html.Div(id='table1', className='col-4 table-responsive', style={"margin-top": "1rem", "box-shadow": "2px 2px 2px lightgrey"}
                     )

        ], className="row", id='charts_div'),
        html.Div([
            html.H3('Itinerary Table'),
            dt.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
            ),
        ], className="row"),

    ], className="row")


    def get_chart1(column, fixed_column):
        names = df[fixed_column].unique()
        data = [
            go.Violin(  # marker=dict(color=COLORS[provider], opacity=OPACITY),
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


    def get_correlation_plots()


    @app.callback(outputs, inputs)
    def update_charts(column, fixed_column):
        chart1, chart2 = get_chart1(column=column, fixed_column=fixed_column), get_chart2(column=column, fixed_column=fixed_column)
        table1 = generate_table_simple(df.describe())
        return [chart1, chart2, table1]

    if __name__ == '__main__':
        app.run_server(debug=True)

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












