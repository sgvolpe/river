
import random
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
from plotly.graph_objs import *
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output, State

import numpy as np
import pandas as pd
import plotly
import plotly.figure_factory as ff

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing

from . import assistant as AS


def get_mfv_app(df):
    app = DjangoDash('mfv_app')
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js","https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js:
        app.scripts.append_script({"external_url": js})

    app.layout = html.Div(
        html.Div([
            #html.Div([dcc.Graph(id='map-graph')], className= 'ten columns offset-by-one'),
            #html.Div([dcc.Graph(id='time_vs_fare-graph')], className= 'ten columns offset-by-one'),
            #html.Div([dcc.Graph(id='fare_histogram-graph')], className= 'four columns offset-by-one'),
            #html.Div([dcc.Graph(id='fare_histogram-graph2')], className= 'four columns offset-by-one'),
            #html.Div([dcc.Graph(id='time_histogram-graph')], className= 'ten columns offset-by-one'),
            #html.Div([dcc.Graph(id='heatmap-graph')], className= 'ten columns offset-by-one'),
            html.Div([dt.DataTable( rows=df.to_dict('records'), row_selectable=True, filterable=True, sortable=True, selected_row_indices=[],id='datatable')
            ], className= 'twelve columns offset-by-one')
        ],className='row')
    )



    #@app.callback(dash.dependencies.Output('time_vs_fare-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_image_src(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Time vs Fare',  ), shared_xaxes=False,shared_yaxes=False)
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)

        fig.append_trace({
            'x': df['price'],
            'y': df['travel_time'],
            'type': 'scatter',
            'opacity':0.5,
            'mode':'markers',
            'marker': {'color':'red','size': 15, 'line':{'width':2}},
            #'name': str(df['itinerary']),
            #'orientation': 'h',
        }, 1, 1)


        return fig

def get_bfm_rs_app(df):


    app = DjangoDash('bfm_rs_app')
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js","https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js:
        app.scripts.append_script({"external_url": js})

    app.layout = html.Div(
        html.Div([
            html.Div([dcc.Graph(id='map-graph')], className= 'ten columns offset-by-one'),
            html.Div([dcc.Graph(id='time_vs_fare-graph')], className= 'ten columns offset-by-one'),
            html.Div([dcc.Graph(id='fare_histogram-graph')], className= 'four columns offset-by-one'),
            html.Div([dcc.Graph(id='fare_histogram-graph2')], className= 'four columns offset-by-one'),
            html.Div([dcc.Graph(id='time_histogram-graph')], className= 'ten columns offset-by-one'),

            #html.Div([dcc.Graph(id='heatmap-graph')], className= 'ten columns offset-by-one'),



            html.Div([dt.DataTable( rows=df.to_dict('records'), row_selectable=True, filterable=True, sortable=True, selected_row_indices=[],id='datatable')
            ], className= 'ten columns offset-by-one')
        ],className='row')
    )



    @app.callback(dash.dependencies.Output('time_vs_fare-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_image_src(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Time vs Fare',  ), shared_xaxes=False,shared_yaxes=False)
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)

        fig.append_trace({
            'x': df['price'],
            'y': df['travel_time'],
            'type': 'scatter',
            'opacity':0.5,
            'mode':'markers',
            'marker': {'color':'red','size': 15, 'line':{'width':2}},
            #'name': str(df['itinerary']),
            #'orientation': 'h',
        }, 1, 1)


        return fig

    @app.callback(dash.dependencies.Output('fare_histogram-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def fare_histogram_graph(rows, selected_row_indices):
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        nrows = df.shape[0]
        data = Data([go.Histogram(x=df['price'], nbinsx=10)]) #,nbinsx = nrows // 20
        return go.Figure(data=data)

    @app.callback(dash.dependencies.Output('fare_histogram-graph2', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def fare_histogram_graph2(rows, selected_row_indices):
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        fl_count = df['flight_count'].unique()
        x = []
        group_labels = []
        for fl in fl_count:
            x.append(df[df['flight_count']==fl]['price'].astype(float))
            group_labels.append(str(fl))

        #fig['layout'].update(title='Fare Distribution by Number of Flights')
        data = Data([go.Histogram(x=x, nbinsx=1)])
        colors = ['#3A4750', '#F64E8B', '#c7f9f1','blue']
        fig = ff.create_distplot(x, group_labels, bin_size=.8, curve_type='normal', colors=colors) #

        return fig

    @app.callback(dash.dependencies.Output('time_histogram-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def time_histogram_graph(rows, selected_row_indices):
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        nrows = df.shape[0]
        data = Data([go.Histogram(x=df['travel_time'], nbinsx=15)]) #,nbinsx = nrows // 20

        #TODO:
        print (df[['travel_time','price']].astype(float).describe() )
        print(df[['travel_time','price']].astype(float).var())
        return go.Figure(data=data)


    @app.callback(dash.dependencies.Output('map-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def map(rows, selected_row_indices):
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        stopover = len(df['itinerary'][0].split('--')[0].split('-'))
        DepartureAirports=df['DepartureAirports'][0].split('-')
        #ArrivalAirports=df['DepartureAirports'][0].split('-')
        origin_iata, destination_iata = str(DepartureAirports[0]), str(DepartureAirports[stopover])

        airport_details = AS.get_airport_details([origin_iata, destination_iata])
        lat = [airport_details[iata]['lat'] for iata in [origin_iata, destination_iata]]
        lon = [airport_details[iata]['lon'] for iata  in [origin_iata, destination_iata]]
        min_lat, max_lat, min_lon, max_lon = min(lat)-10, max(lat)+10, min(lon)-10, max(lon)+10

        aux = set(zip(list(df['DepartureAirports']),list(df['ArrivalAirports'])   ))
        cities = []
        for onds in aux:
            color = 'rgb'+str( (int(random.random() * 256)%256,int(random.random() * 256)%256,int(random.random() * 256)%256) )

            (x,y) = onds
            segments = ( list ( zip ( x.split('-') , y.split('-') ) ) )
            for segment in segments:
                (ori, dest) = segment
                airports_iata_list = [ori, dest]
                airport_details = AS.get_airport_details(airports_iata_list)
                lat = [airport_details[iata]['lat'] for iata in airports_iata_list]
                lon = [airport_details[iata]['lon'] for iata in airports_iata_list]
                ap_names = [airport_details[iata]['city']+'_'+airport_details[iata]['country'] for iata in airports_iata_list]
                cities.append(
                    dict(
                        type = 'scattergeo',
                        lat = lat,lon = lon,
                        hoverinfo = 'text',
                        text = ap_names,
                        mode = 'lines',
                        line = dict(
                            width = 2,
                            color = color,
                        )
                    )
                )

        layout = dict(
                title = ' '.join(airports_iata_list),
                showlegend = False,
                geo = dict(
                    resolution = 50,
                    showland = True,
                    landcolor = 'rgb(243, 243, 243)',
                    countrycolor = 'rgb(204, 204, 204)',
                    lakecolor = 'rgb(255, 255, 255)',
                    projection = dict( type="equirectangular" ),
                    coastlinewidth = 2,
                    lataxis = dict(
                        range =[0,0],# [ min_lat, max_lat ],
                        showgrid = True,
                        tickmode = "linear",
                        dtick = 10
                    ),
                    lonaxis = dict(
                        range = [0,0],#[ min_lon, max_lon ],
                        showgrid = True,
                        tickmode = "linear",
                        dtick = 20
                    ),
                )
            )

        fig = dict( data=cities, layout=layout )

        return fig



    #@app.callback(dash.dependencies.Output('heatmap-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def heatmap(rows, selected_row_indices):
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        its = list(df['itinerary'])
        dist_m = AS.get_matrix_distance(its)
        print ('CALCULATED')
        return go.Figure(data=Data([go.Heatmap(z=dist_m )] ) )



    if __name__ == '__main__':
        app.run_server(debug=True)

    return app
