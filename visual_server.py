from repomanager import RepoManager
from dataanalysis import AnalisiDati
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import locale
import pandas as pd
locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

hovermode = "x"
mapbox_access_token = open(".mapbox_token").read()
colors = px.colors.cyclical.HSV
default_height = 800


def generate_riepilogo_mappa(data: AnalisiDati):
    df = data.data_regionale_latest
    # mappa_nazionale = px.scatter_mapbox(df, lat="lat", lon="long", color="denominazione", size="totale_casi",
    #                                     color_continuous_scale=px.colors.cyclical.IceFire)

    mappa_nazionale = px.scatter_mapbox(df, lat="lat", lon="long", color="denominazione", size="totale_casi",
                                        color_discrete_sequence=px.colors.qualitative.Dark24)

    mappa_nazionale.update_layout(
        title='Situazione nelle regioni',
        autosize=True,
        hovermode='closest',
        showlegend=True,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=42,
                lon=12
            ),
            pitch=0,
            zoom=5,
            style='dark'
        ),
        height=800,
        width=1500
    )

    # mappa_nazionale.update_traces(
    #     hovertemplate=None,
    #     hoverinfo="all",
    #     hovertext=df["totale_casi"]
    # )
    return mappa_nazionale


def generate_riepilogo_nazionale(data: AnalisiDati):
    data_nazionale = data.data_nazionale

    riepilogo_nazionale = go.Figure()

    riepilogo_nazionale.add_trace(go.Scatter(x=data_nazionale.giorni, y=data_nazionale.totale_casi,
                                             text=data_nazionale.totale_casi,
                                             name='Totale casi',
                                             line_color=colors[0]))
    riepilogo_nazionale.add_trace(go.Scatter(x=data_nazionale.giorni, y=data_nazionale.deceduti,
                                             text=data_nazionale.deceduti,
                                             name='Deceduti',
                                             line_color=colors[1]))
    riepilogo_nazionale.add_trace(go.Scatter(x=data_nazionale.giorni, y=data_nazionale.dimessi_guariti,
                                             text=data_nazionale.dimessi_guariti,
                                             name='Guariti',
                                             line_color=colors[2]))
    riepilogo_nazionale.add_trace(go.Scatter(x=data_nazionale.giorni, y=data_nazionale.terapia_intensiva,
                                             text=data_nazionale.terapia_intensiva,
                                             name='Terapia intensiva',
                                             line_color=colors[3]))
    riepilogo_nazionale.add_trace(go.Scatter(x=data_nazionale.giorni, y=data_nazionale.ricoverati_con_sintomi,
                                             text=data_nazionale.ricoverati_con_sintomi,
                                             name='Ospedalizzati',
                                             line_color=colors[5]))
    riepilogo_nazionale.add_trace(go.Scatter(x=data_nazionale.giorni, y=data_nazionale.tamponi,
                                             text=data_nazionale.tamponi,
                                             name='Tamponi',
                                             line_color=colors[6]))
    riepilogo_nazionale.add_trace(go.Scatter(x=data_nazionale.giorni, y=data_nazionale.totale_positivi,
                                             text=data_nazionale.totale_positivi,
                                             name='Attualmente positivi',
                                             line_color=colors[7]))
    # riepilogo_nazionale.add_trace(go.Scatter(x=data_nazionale.giorni, y=data_nazionale.variazione_totale_positivi,
    #                                          text=data_nazionale.variazione_totale_positivi,
    #                                          name='Variazione attualmente positivi',
    #                                          line_color=colors[7]))
    riepilogo_nazionale.update_layout(
        yaxis_type="log",
        hovermode=hovermode,
        height=default_height
    )
    riepilogo_nazionale.update_traces(
        mode='lines+markers',
        textposition="bottom center",
        hovertemplate="%{y:n}"
    )

    return riepilogo_nazionale


def generate_riepilogo_regionale(data: AnalisiDati):
    riepilogo_regioni = px.line(data.data_regionale, x="giorni", y="totale_casi", color="denominazione",
                                line_shape="spline", color_discrete_sequence=px.colors.qualitative.Dark24)

    riepilogo_regioni.update_layout(
        yaxis_type="log",
        hovermode=hovermode,
        height=default_height

    )
    riepilogo_regioni.update_traces(
        mode='lines+markers',
        hovertemplate=None,
        textposition="bottom center"
    )

    return riepilogo_regioni


def generate_riepilogo_bar(data: AnalisiDati, regione: int, use_percentage: bool):
    df = data.data_regionale[data.data_regionale.codice_regione == regione]
    y_contagi = df.incrementi_percentuali if use_percentage else df.incrementi
    y_tamponi = df.incrementi_tamponi_percentuali if use_percentage else df.incrementi_tamponi
    contagi_avg = y_contagi.mean()
    tamponi_avg = y_tamponi.mean()

    fig = go.Figure(data=[
        go.Bar(name='Nuovi contagi', x=df.giorni, y=[x if x < 4*contagi_avg else 1 for x in y_contagi]),
        go.Bar(name='Nuovi tamponi', x=df.giorni, y=[x if x < 4*tamponi_avg else 1 for x in y_tamponi])
    ])
    # Change the bar mode
    fig.update_layout(
        barmode='overlay',
        hovermode=hovermode,
        height=default_height
    )
    fig.update_traces(
        opacity=0.4,
        textposition='outside',
        hovertemplate="%{y:.1%}" if use_percentage else "%{y:n}"
    )
    return fig


def generate_table_from_data(data: AnalisiDati, regione: int,) -> dt.DataTable:
    df = data.data_regionale[data.data_regionale.codice_regione == regione]
    data_table = dt.DataTable(
        id='rdt',
        columns=(
                [
                    {'id': 'denominazione', 'name': 'Denominazione'},
                    {'id': 'giorni', 'name': 'Giorno'},
                    {'id': 'totale_casi', 'name': 'Contagiati'},
                    {'id': 'incrementi', 'name': 'Incremento contagi'},
                    {'id': 'ricoverati_con_sintomi', 'name': 'Ricoverati'},
                    {'id': 'terapia_intensiva', 'name': 'Terapia intensiva'},
                    {'id': 'totale_ospedalizzati', 'name': 'Ospedalizzati'},
                    {'id': 'isolamento_domiciliare', 'name': 'Isolamento'},
                    {'id': 'nuovi_positivi', 'name': 'Nuovi positivi'},
                    {'id': 'dimessi_guariti', 'name': 'Guariti'},
                    {'id': 'deceduti', 'name': 'Deceduti'},
                    {'id': 'tamponi', 'name': 'Tamponi'},
                    {'id': 'incrementi_tamponi', 'name': 'Incremento tamponi'}
                ]
        ),
        data=df[[
            'denominazione',
            'giorni',
            'totale_casi',
            'incrementi',
            'ricoverati_con_sintomi',
            'terapia_intensiva',
            'totale_ospedalizzati',
            'isolamento_domiciliare',
            'nuovi_positivi',
            'dimessi_guariti',
            'deceduti',
            'tamponi',
            'incrementi_tamponi'
        ]].to_dict(orient='records'),
        editable=False,
        style_table={
            'height': 'auto',
            'minWidth': '500px', 'maxWidth': '90%',
            'whiteSpace': 'normal',
            'overflowX': 'scroll',
            'maxHeight': default_height,
            'overflowY': 'scroll',
            'textAlign': 'left'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_cell_conditional=[
           {'if': {'column_id': 'denominazione'},
            'width': '80%',
            'minWidth': '200px',
            'textAlign': 'left',
            }
                               ] +
        [
            {'if': {'column_id': c},
             'width': '10%',
             'minWidth': '150px',
             'textAlign': 'left'} for c in [
                        'giorni',
                        'totale_casi',
                        'incrementi',
                        'ricoverati_con_sintomi',
                        'terapia_intensiva',
                        'totale_ospedalizzati',
                        'isolamento_domiciliare',
                        'nuovi_positivi',
                        'dimessi_guariti',
                        'deceduti',
                        'tamponi',
                        'incrementi_tamponi'
                    ]
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        fixed_columns={'headers': True, 'data': 2},
        fixed_rows={'headers': True, 'data': 0},
    )
    # data_table = dt.DataTable(
    #     # Initialise the rows
    #     rows=df.to_dict('records'),
    #     columns=(
    #             [
    #                 {'id': 'denominazione', 'name': 'Denominazione'},
    #                 {'id': 'giorni', 'name': 'Giorno'},
    #                 {'id': 'totale_casi', 'name': 'Totale casi'}
    #             ]
    #     ),
    #     row_selectable=True,
    #     filterable=False,
    #     # sortable=True,
    #     selected_row_indices=['denominazione', 'giorni', 'totale_casi'],
    #     id='dt-regionale'
    # )

    return data_table


def generate_riepilogo_regionale_bar_plain(data: AnalisiDati, regione: int):
    # df = data.data_regionale[data.data_regionale.codice_regione == regione]
    # fig = go.Figure(data=[
    #     go.Bar(name='Nuovi contagi', x=df.giorni, y=df.incrementi),
    #     go.Bar(name='Nuovi tamponi', x=df.giorni, y=df.incrementi_tamponi)
    # ])
    # # Change the bar mode
    # fig.update_layout(
    #     barmode='overlay',
    #     hovermode=hovermode,
    # )
    # fig.update_traces(
    #     opacity=0.6,
    #     textposition='outside'
    # )
    # return fig
    return generate_riepilogo_bar(data, regione, False)


def generate_riepilogo_regionale_bar_percentuale(data: AnalisiDati, regione: int):
    # df = data.data_regionale[data.data_regionale.codice_regione == regione]
    # fig = go.Figure(data=[
    #     go.Bar(name='Nuovi contagi', x=df.giorni, y=df.incrementi_percentuali),
    #     go.Bar(name='Nuovi tamponi', x=df.giorni, y=df.incrementi_tamponi_percentuali)
    # ])
    # # Change the bar mode
    # fig.update_layout(
    #     barmode='overlay',
    #     hovermode=hovermode,
    # )
    # fig.update_traces(
    #     opacity=0.6,
    #     textposition='outside',
    #     hovertemplate="%{y:.1%}"
    # )
    # return fig
    return generate_riepilogo_bar(data, regione, True)

def generate_riepilogo_province(data: AnalisiDati, regione: int):
    df = data.data_provinciale[data.data_provinciale.codice_regione == regione]
    riepilogo_province = px.line(df, x="giorni", y="totale_casi", color="denominazione", line_shape="spline",
                                 color_discrete_sequence=colors)

    riepilogo_province.update_layout(
        yaxis_type="log",
        hovermode=hovermode,
        height=default_height
    )
    riepilogo_province.update_traces(
        mode='lines+markers',
        textposition="bottom center",
        hovertemplate=None
    )

    return riepilogo_province


def main_func():
    repo_path = '/Users/bruand/Documents Local/analisi/COVID-19'
    #_ = RepoManager.update_repo(repo_path)
    #repo_path = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master"
    nazionale = f'{repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
    regioni = f'{repo_path}/dati-regioni/dpc-covid19-ita-regioni.csv'
    province = f'{repo_path}/dati-province/dpc-covid19-ita-province.csv'

    analysis = AnalisiDati(file_nazionale=nazionale, file_regioni=regioni,
                           file_province=province, show=False, store=True, color_map="brg")

    last_update_date = analysis.last_update

    selected_region = 15

    riepilogo_nazionale = generate_riepilogo_nazionale(analysis)

    mappa_nazionale = generate_riepilogo_mappa(analysis)

    riepilogo_regioni = generate_riepilogo_regionale(analysis)

    riepilogo_province = generate_riepilogo_province(analysis, selected_region)

    bar_chart_regione = generate_riepilogo_regionale_bar_plain(analysis, selected_region)

    bar_chart_regione_percentuale = generate_riepilogo_regionale_bar_percentuale(analysis, selected_region)

    regione_dt = generate_table_from_data(analysis, selected_region)

    app = dash.Dash()
    app.layout = html.Div(children=[
        html.H1(children=f'Analisi covid 19 in Italia al {last_update_date}'),
        html.Hr(),
        html.Div(id="mappa_italia", children=[
            html.H2(children='Mappa del contagio in Italia'),
            html.Hr(),
            dcc.Graph(figure=mappa_nazionale)
        ]),
        html.Hr(),
        html.Div(id="riepilogo_italia", children=[
            html.H2(children='Andamento logaritmico nazionale'),
            html.Hr(),
            dcc.Graph(figure=riepilogo_nazionale)
        ]),
        html.Hr(),
        html.Div(id="riepilogo_regioni", children=[
            html.H2(children='Andamento logaritmico regioni'),
            html.Hr(),
            dcc.Graph(figure=riepilogo_regioni)
        ]),
        html.Hr(),
        html.H2(children='Analisi covid 19 in Campania'),
        html.Hr(),
        html.Div(id="riepilogo_regione_table", children=[
            html.H3(children='Tabella riepilogativa'),
            html.Hr(),
            regione_dt
        ]),
        html.Hr(),
        html.Div(id="riepilogo_regione_bar", children=[
            html.H3(children='Grafico a barre riepilogativo della Campania'),
            html.Hr(),
            dcc.Graph(figure=bar_chart_regione)
        ]),
        html.Hr(),
        html.Div(id="riepilogo_regione_bar_perc", children=[
            html.H3(children='Grafico a barre riepilogativo della Campania in percentuale'),
            html.Hr(),
            dcc.Graph(figure=bar_chart_regione_percentuale)
        ]),
        html.Hr(),
        html.Div(id="riepilogo province", children=[
            html.H3(children='Andamento logaritmico province regione Campania'),
            html.Hr(),
            dcc.Graph(figure=riepilogo_province)
        ]),
    ])

    app.run_server(debug=True)


if __name__ == '__main__':
    main_func()
