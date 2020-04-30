
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
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing




def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th('col')]+[html.Th(col) for col in dataframe.columns])] +

        # Body        
        [html.Tr([html.Td(dataframe.index[i])] + [
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


def get_ancillaries(file_path=r'', ancillaries_object=None):
    app = DjangoDash('ancillaries_app')
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js","https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js:
        app.scripts.append_script({"external_url": js})

    df = pd.read_csv(file_path) ## bookings df


    app.layout = html.Div(
        html.Div([
            html.Div([ dcc.Graph(id='carriers_count-graph') ], className= 'four columns offset-by-one'),
            html.Div([ dcc.Graph(id='bookings_count-graph') ], className= 'four columns offset-by-one'),
            html.Div([ dcc.Graph(id='carriers_coverage-graph') ], className= 'four columns offset-by-one'),
            html.Div([ dcc.Graph(id='bookings_coverage-graph') ], className= 'four columns offset-by-one'),
            html.Div([
                dt.DataTable( rows=df.to_dict('records'), row_selectable=True, filterable=True, sortable=True, selected_row_indices=[],
                id='datatable')
            ], className= 'ten columns offset-by-one')
        ])
    )

    @app.callback(dash.dependencies.Output('carriers_count-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_carriers_count_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Carrier Count per Provider',  ))
        df = ancillaries_object.get_carrier_count()
        p = ['sabre','travelport'] #TODO: gget gds list auto
        c = ['red', 'blue']
        for x in range(len(p)):
            x_ = df[df['GDS'] == p[x] ]['ANC']
            y_ = df[df['GDS'] == p[x] ]['count']
            fig.append_trace({
                'x': x_,
                'y': y_,
                'type': 'bar',
                'opacity':0.5,
                'marker': {'color':c[x], 'line':{'width':2}},
                'name': p[x],
            }, 1, 1)

        return fig

    @app.callback(dash.dependencies.Output('bookings_count-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_bookings_count_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Bookings Count per Provider',  ))
        df = ancillaries_object.get_booking_count()
        p = ['sabre','travelport'] #TODO: gget gds list auto
        c = ['red', 'blue']
        for x in range(len(p)):
            x_ = df[df['GDS'] == p[x] ]['ANC']
            y_ = df[df['GDS'] == p[x] ]['count']
            fig.append_trace({
                'x': x_,
                'y': y_,
                'type': 'bar',
                'opacity':0.5,
                'marker': {'color':c[x], 'line':{'width':2}},
                'name': p[x],
            }, 1, 1)

        return fig


    @app.callback(dash.dependencies.Output('carriers_coverage-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def carriers_coverage_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Carriers Percentage per Provider',  ))
        df = ancillaries_object.get_carrier_count(percentage=True)
        p = ['sabre','travelport'] #TODO: gget gds list auto
        c = ['red', 'blue']
        for x in range(len(p)):
            x_ = df[df['GDS'] == p[x] ]['ANC']
            y_ = df[df['GDS'] == p[x] ]['count']
            fig.append_trace({
                'x': x_,
                'y': y_,
                'type': 'bar',
                'opacity':0.5,
                'marker': {'color':c[x], 'line':{'width':2}},
                'name': p[x],
            }, 1, 1)

        return fig

    @app.callback(dash.dependencies.Output('bookings_coverage-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def bookings_coverage_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Bookings Percentage per Provider',  ))
        df = ancillaries_object.get_booking_count(percentage=True)
        p = ['sabre','travelport'] #TODO: gget gds list auto
        c = ['red', 'blue']
        for x in range(len(p)):
            x_ = df[df['GDS'] == p[x] ]['ANC']
            y_ = df[df['GDS'] == p[x] ]['count']
            fig.append_trace({
                'x': x_,
                'y': y_,
                'type': 'bar',
                'opacity':0.5,
                'marker': {'color':c[x], 'line':{'width':2}},
                'name': p[x],
            }, 1, 1)

        return fig


    if __name__ == '__main__':
            app.run_server(debug=True)

    return app



def get_summary_app(file_path=r'', providers = ['sabre','competitor']):
    app = DjangoDash('summary_app')
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js","https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js:
        app.scripts.append_script({"external_url": js})

    df = pd.read_csv(file_path)
    p = [x+j for j in ['_cheapest','_cheapest','_only','_only','_time_min','_fare_mean','_fare_std'] for x in providers]
    columns = ['ond','search_date','ap_los','lfe','quickest','cxr_div','both']+p


    app.layout = html.Div(
        html.Div([
            html.Div([
                dt.DataTable( rows=df[columns].to_dict('records'), row_selectable=True, filterable=True, sortable=True, selected_row_indices=[],
                id='datatable')
            ], className= 'ten columns offset-by-one',),
            html.Div(id='results_table', className= 'ten columns offset-by-one', style={'height':'500px'}),
            html.Div([dcc.Graph(id='lfe_cross-graph')], className= 'three columns offset-by-one', style={'height':'500px'}),
            html.Div([dcc.Graph(id='overlap-graph_across')], className= 'three columns offset-by-one', style={'height':'500px'}),
            html.Div([dcc.Graph(id='polar-graph')], className= 'three columns offset-by-one', style={'height':'500px'}),
            html.Div([dcc.Graph(id='lfe-quick-graph')], className= 'ten columns offset-by-one'),
            html.Div([dcc.Graph(id='fare_time-graph')], className= 'ten columns offset-by-one'),
            html.Div([dcc.Graph(id='overlap-graph')], className= 'four columns offset-by-one', style={'height':'500px'}),
            html.Div([dcc.Graph(id='overlap-ond-graph')], className= 'four columns offset-by-one', style={'height':'500px'}),


            #html.Div([dcc.Graph(id='quick-graph')], className= 'ten columns', style={'height':'500px'}),

        ],className='row')


    )


    @app.callback(dash.dependencies.Output('results_table', 'children'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_results_table(rows, selected_row_indices):
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        lfe_dict = dict((df['lfe'].value_counts()))
        quickest_dict = dict((df['quickest'].value_counts()))
        cxr_div_dict = dict((df['cxr_div'].value_counts()))

        new_df = pd.DataFrame( [lfe_dict,quickest_dict,cxr_div_dict], index=['LFE','Quic','CXR Div'] )
        print (new_df)
        return generate_table(new_df)


        return go.Figure(data=data,layout=layout)



    @app.callback(dash.dependencies.Output('lfe_cross-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_lfe_cross_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Overlap',  ))
        fig.layout = go.Layout(barmode='stack')
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        lfe_dict = dict((df['lfe'].value_counts()))
        data = Data([go.Pie(values=list(lfe_dict.values()), labels=list(lfe_dict.keys()))])
        layout = go.Layout( title='LFE')
        return go.Figure(data=data,layout=layout)

    @app.callback(dash.dependencies.Output('overlap-graph_across', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_overlap_graph(rows, selected_row_indices):
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        p = ['both']+[p + '_only' for p in providers]
        c = ['green', 'red', 'blue']
        p_list = [df[x].sum() for x in p ]
        layout = go.Layout( title='Overlap Across')
        return go.Figure(data=[go.Pie(values=p_list, labels=p)], layout=layout)

    @app.callback(dash.dependencies.Output('polar-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_polar_graph(rows, selected_row_indices):
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        lfe_dict = dict((df['lfe'].value_counts()))
        quickest_dict = dict((df['quickest'].value_counts()))
        cxr_div_dict = dict((df['cxr_div'].value_counts()))

        provider_list = providers #['sabre', 'competitor']
        data = []
        for x in range(len(provider_list)):
            if provider_list[x] not in lfe_dict: lfe_dict[provider_list[x]] = 0
            if provider_list[x] not in quickest_dict: quickest_dict[provider_list[x]] = 0
            if provider_list[x] not in cxr_div_dict: cxr_div_dict[provider_list[x]] = 0
            data.append(
                go.Scatterpolar(
                  r = [ lfe_dict[provider_list[x]], quickest_dict[provider_list[x]], cxr_div_dict[provider_list[x]] ],
                  theta = ['lfe','quickest','cxr_div'],
                  fill = 'toself',
                  name = provider_list[x]
              )
            )
        layout = go.Layout(
                title = "Winner Metrics", #font = dict(size = 15),
                polar = dict( #bgcolor = "rgb(223, 223, 223)",
                  angularaxis = dict(
                    tickwidth = 2,
                    linewidth = 3,
                    layer = "below traces"
                  )
                )
        )
        return go.Figure(data=data,layout=layout)


    @app.callback(dash.dependencies.Output('fare_time-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_fare_time_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Fare vs Time',  ))
        fig.layout = go.Layout(barmode='stack',title = "Price vs Time",)
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)

        p = providers
        c = ['red', 'blue']
        for x in range(len(p)):
            fig.append_trace({
                'y': df[p[x]+'_cheapest' ],
                'x': df[p[x] + '_time_min' ],
                'type': 'scatter',
                'opacity':0.5,
                'mode':'markers',
                'marker': {'color':c[x],'size': 15, 'line':{'width':2}},
                'name': p[x],
                'orientation': 'h',
            }, 1, 1)
        return fig




    @app.callback(dash.dependencies.Output('overlap-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_overlap_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, shared_xaxes=True,shared_yaxes=False)
        fig.layout = go.Layout(barmode='stack',title='Overlap per Query')
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        p = ['both']+[p + '_only' for p in providers]
        c = ['green', 'red', 'blue']
        for x in range(len(p)):
            fig.append_trace({
                'y': df['ond'].astype(str)+df['ap_los'].astype(str), #+df['search_date'].astype(str)
                'x': df[p[x]].astype(float) / (df['both'].astype(float)+df[p[1]].astype(float)+df[p[2]].astype(float)),
                'type': 'bar',
                'opacity':0.5,
                'marker': {'color':c[x],'line':{'color': c[x],'width':1.5}},
                'name': p[x],
                'orientation': 'h',
            }, 1, 1)

        return fig

    @app.callback(dash.dependencies.Output('overlap-ond-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_overlap_ond_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=2, subplot_titles=('Overlap per Query','Overlap per OnD'  ), shared_xaxes=True,shared_yaxes=False)
        fig.layout = go.Layout(barmode='stack', title='Overlap per Ond')
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        p = ['both']+[p + '_only' for p in providers]
        df = df.groupby(['ond'],as_index=True)[p].sum()

        c = ['green', 'red', 'blue']
        for x in range(len(p)):
            fig.append_trace({
                'y': df.index,
                'x': df[p[x]].astype(float)/(df['both'].astype(float)+df[p[1]].astype(float)+df[p[2]].astype(float)),
                'type': 'bar',
                'opacity':0.5,
                'marker': {'color':c[x],'line':{'color': c[x],'width':1.5}},
                'name': p[x],
                'orientation': 'h',
            }, 1, 1)


        return fig


    @app.callback(dash.dependencies.Output('lfe-quick-graph', 'figure'),[Input('datatable', 'rows'), Input('datatable', 'selected_row_indices')])
    def update_lfe_quick_graph(rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=3, cols=1, subplot_titles=('Quickest Option', 'Cheapest Option', 'Fare Mean | STDEV' ), shared_xaxes=True,shared_yaxes=False)
        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        provider_list = providers #['sabre', 'competitor']
        colors = ['red', 'blue']
        x_list = df['ond'].astype(str)+df['search_date'].astype(str)+df['ap_los'].astype(str)
        for i in range(len(provider_list)):
            fig.append_trace({
                'y': df[ provider_list[i] +'_time_min'],
                'x': x_list,
                'type':'scatter',
                'name':provider_list[i]+'_time_min',
                'marker': {'color': colors[i]},
                'opacity':0.5,
                'orientation': 'h',
            } ,1, 1)

            fig.append_trace({
                'y': df[provider_list[i] + '_cheapest'],
                'x': x_list,
                'type':'bar',
                'name': provider_list[i]+ '_cheapest',
                'marker':{'color': colors[i]},
                'opacity':0.5,
            } ,2, 1)

            fig.append_trace({
                'x': x_list,
                'y': df[provider_list[i] + '_fare_mean'],
                'type':'scatter',
                'name': provider_list[i]+'Mean Fare | Stdev',
                'marker':{'color': colors[i]},
                'opacity':0.5,
                'error_y':{'type':'data', 'array':df[provider_list[i] + '_fare_std'],'visible':True,},
            } ,3, 1)

        return fig




    if __name__ == '__main__':
            app.run_server(debug=True)

    return app



def getapp(file_path=r''):
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
    app = DjangoDash('dash2')
    df = pd.read_csv(file_path)
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})

    ond = df['market'][0]
    date = df['search_date'][0]
    ap_los = df['ap_los'][0]
    provider_count = dict((df['provider'].value_counts()))
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js","https://codepen.io/bcd/pen/YaXojL.js"]

    for js in external_js:
        app.scripts.append_script({"external_url": js})

    app.layout = html.Div(
        html.Div([
            html.Div([
                html.Div(children=[
                    html.H1(children=ond),
                    html.H3(children=date),
                    html.H4(children=str(provider_count)),
                    html.H5(children=str(ap_los)),
                    #generate_table(df['is_duplicate'].value_counts())


                ],className='row'),
                html.Div([
                    html.Div([
                        html.A(['Print PDF'],className="button no-print print",style={}),
                        html.H3('Choose Provider:'),
                        html.Div([
                        dcc.Checklist(id = 'Provider', values=['sabre', 'competitor','overlap'], labelStyle={'display': 'inline-block'},
                            options=[{'label': 'Sabre', 'value': 'sabre'},{'label': 'Competitor', 'value': 'competitor'},{'label': 'Overlap', 'value': 'overlap'}]
                        )],className='row'),
                    ],className='six columns'),
                    html.Div([dcc.Graph(id='time_vs_fare-graph')], className= 'twelve columns', style={'height':'500px'}),
                    html.Div([dcc.Graph(id='overlap-graph')], className= 'twelve columns'),
                    html.Div([dcc.Graph(id='fare-graph')], className= 'twelve columns'),

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
                        dt.DataTable( rows=df.to_dict('records'), row_selectable=True, filterable=True, sortable=True, selected_row_indices=[],
                        id='datatable-gapminder')
                    ], className="twelve columns"),
            ], style={'width':'100%','font-size':'0.8em'})

        ], className='ten columns offset-by-one')
    )

    @app.callback(
        dash.dependencies.Output('violin-graph', 'figure'),
        [dash.dependencies.Input('Provider', 'values'),Input('datatable-gapminder', 'rows'), Input('datatable-gapminder', 'selected_row_indices')])
    def update_image_src2(selector,rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Fare Distribution by Provider',  ))

        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        df = df[ df['provider'].isin( selector ) ]

        providers = pd.unique(df['provider'])
        for provider in providers:
            fig.append_trace({
                "x": df['provider'][df['provider'] == provider],
                'y': df['fare'][df['provider'] == provider],
                "name": provider,
                'type': 'violin',
                "box": {"visible": True},
                "meanline": {"visible": True},
                #'color': {'competitor':'blue','sabre':'red'}[provider],
            }, 1, 1)
        return fig


    @app.callback(
        dash.dependencies.Output('fare-graph', 'figure'),[dash.dependencies.Input('Provider', 'values'),Input('datatable-gapminder', 'rows'), Input('datatable-gapminder', 'selected_row_indices')])
    def update_image_src(selector,rows, selected_row_indices):

        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Fare Comparison',  ), shared_xaxes=False,shared_yaxes=False)

        sdf = [float(x) for x in list(df[df['provider']=='sabre']['fare'])]
        cdf = [float(x) for x in  list(df[df['provider']=='competitor']['fare']) ]

        fig.append_trace({
            'y': sdf,
            'x': [i for i in range(len(sdf))],
            'type':'scatter','name':'Sabre',
            'marker': {'color':'red'}

        } ,1, 1)
        fig.append_trace({
            'y': cdf,
            'x': [i for i in range(len(cdf))],
            'type':'scatter','name':'Competitor',
            'marker': {'color':'blue'}

        } ,1, 1)
        fig.append_trace({
            'y': [s - c for s, c in zip(sdf,cdf)],
            'x': [i for i in range(min (len(cdf) , len(sdf)) )],
            'type':'bar','name':'Sabre - Competitor',
            'marker': {'color':'green'}

        } ,1, 1)

        return fig

    @app.callback(
        dash.dependencies.Output('time_vs_fare-graph', 'figure'),
        [dash.dependencies.Input('Provider', 'values'),Input('datatable-gapminder', 'rows'), Input('datatable-gapminder', 'selected_row_indices')])
    def update_image_src(selector,rows, selected_row_indices):
        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Time vs Fare',  ), shared_xaxes=False,shared_yaxes=False)

        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]

        df = pd.DataFrame(rows)
        df = df[ df['provider'].isin( selector ) ]

        for provider in selector:
            fig.append_trace({
                'x': df[(df['provider'] == provider ) & (df['is_duplicate']=='N')]['fare'],
                'y': df[(df['provider'] == provider ) & (df['is_duplicate']=='N')]['travel_time'],
                'type': 'scatter', 'mode': 'markers', 'name':provider, 'marker': {'color': {'sabre':'red','competitor':'blue','overlap':'green'}[provider] }
            }, 1, 1)
        fig.append_trace({
            'x': df[(df['is_duplicate']=='Y')]['fare'],
            'y': df[(df['is_duplicate']=='Y')]['travel_time'],
            'type': 'scatter', 'mode': 'markers', 'name':'overlap', 'marker': {'color':'green'},
        }, 1, 1)

        return fig


    @app.callback(dash.dependencies.Output('overlap-graph', 'figure'),
        [dash.dependencies.Input('Provider', 'values'),Input('datatable-gapminder', 'rows'), Input('datatable-gapminder', 'selected_row_indices')])
    def update_image_src(selector, rows, selected_row_indices):

        fig = plotly.tools.make_subplots( rows=1, cols=1, subplot_titles=('Options Distribution by Carrier',  ), shared_xaxes=False,shared_yaxes=False)

        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        df = df[ df['provider'].isin( selector ) ]
        providers = pd.unique(df['provider'])
        aux_count = 0
        for provider in providers:
            aux_df = df[df['provider']=='competitor']
            fig.append_trace({
                'x': aux_df['id'], #'x': [i for i in range(aux_count, len(aux_df) + aux_count)],#'x':df[df['provider']==provider]['id'],
                'y': [1 for i in list(range(aux_df.shape[0]))],
                'type': 'bar',
                'name':provider,
                'marker': {'color': {'competitor':'blue','sabre':'red'}[provider]}
            } ,1, 1)
            aux_count += len(aux_df)

        aux_df = df[df['is_duplicate']=='Y']
        fig.append_trace({
            'x': aux_df['id'],# 'x': [i for i in range(aux_count, len(aux_df) + aux_count)],  #'x':df[df['is_duplicate']=='Y']['id'],
            'y': [1 for i in list(range(aux_df.shape[0]))],
            'type': 'bar',
            'name':'overlap',
            'marker': {'color': 'green'}
        } ,1, 1)

        return fig

    @app.callback(dash.dependencies.Output('overlap_pie-graph', 'figure'),
    [dash.dependencies.Input('time_vs_fare-graph', 'figure'),Input('datatable-gapminder', 'rows'),Input('datatable-gapminder', 'selected_row_indices')])
    def update_image_src2(selector, rows, selected_row_indices):


        fig = plotly.tools.make_subplots( rows=4, cols=1, subplot_titles=('Time vs Fare',  ), shared_xaxes=False,shared_yaxes=False)

        if len(selected_row_indices) != 0: rows = [rows[x] for x in selected_row_indices]
        df = pd.DataFrame(rows)
        duplicate_dict = dict((df['is_duplicate'].value_counts()))

        data = Data([
            go.Pie(values=list(duplicate_dict.values()), labels=list(duplicate_dict.keys()))
         ])
        return go.Figure(data=data)


    def test():
        return 'TEST'

    if __name__ == '__main__':
            app.run_server(debug=True)

    return app
