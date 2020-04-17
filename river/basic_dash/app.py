

import datetime

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from django_plotly_dash import DjangoDash
import plotly.graph_objs as go

import pandas as pd
import pandas_datareader.data as web


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

def get_app2(file_path=r''):
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


def get_stock_app(file_path=r''):
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