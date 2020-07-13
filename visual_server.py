from dataanalysis import AnalisiDati
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import locale
from urllib.request import urlopen
import pandas as pd
import json
import dateutil.parser
# import shapefile

with urlopen(
        'https://gist.githubusercontent.com/datajournalism-it/f1abb68e718b54f6a0fe/raw/23636ff76534439b52b87a67e766b11fa7373aa9/regioni-con-trento-bolzano.geojson') as response:
    counties = json.load(response)

#geojson_file = '/Users/bruand/Documents Local/analisi/Limiti01012020_g/Reg01012020_g/Reg01012020_g_WGS84.json'
#with open(geojson_file) as json_file:
#    dati_json = json.load(json_file)

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

hovermode = "x"
mapbox_access_token = open(".mapbox_token").read()
colors = px.colors.cyclical.HSV
default_height = 800


def generate_riepilogo_mappa(data: AnalisiDati):
    df = data.data_regionale_latest.sort_values(by="totale_casi", ascending=False)

    mappa_nazionale = px.scatter_mapbox(df, lat="lat", lon="long", color="denominazione", size="totale_casi",
                                        # color_discrete_sequence=px.colors.qualitative.Dark24,
                                        hover_data=['totale_casi', 'casi_da_sospetto_diagnostico', 'casi_da_screening', 'deceduti', 'terapia_intensiva'],
                                        color_discrete_sequence=['red'],
                                        labels={
                                            'totale_casi': 'Totale casi',
                                            'casi_da_sospetto_diagnostico': 'Nuove diagnosi',
                                            'casi_da_screening': 'Screening',
                                            'deceduti': 'Deceduti',
                                            'terapia_intensiva': 'Terapia intensiva'
                                        })
    # mappa_nazionale = px.scatter_mapbox(df, lat="lat", lon="long", color="denominazione", size=['totale_casi', 'casi_da_sospetto_diagnostico', 'casi_da_screening', 'deceduti', 'terapia-intensiva'],
    #                                     # color_discrete_sequence=px.colors.qualitative.Dark24,
    #                                     color_discrete_sequence=['red'],
    #                                     labels={
    #                                         'totale_casi': 'Totale casi',
    #                                         'casi_da_sospetto_diagnostico': 'Nuove diagnosi',
    #                                         'casi_da_screening': 'Screening',
    #                                         'deceduti': 'Deceduti',
    #                                         'terapia-intensiva': 'Terapia intensiva'
    #                                     })

    # file_regioni_json = 'https://gist.githubusercontent.com/datajournalism-it/f1abb68e718b54f6a0fe/raw/23636ff76534439b52b87a67e766b11fa7373aa9/regioni-con-trento-bolzano.geojson'
    # file_regioni_json = geojson_file

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
            style='dark',
            layers=[
                dict(
                    sourcetype='geojson',
                    source='https://gist.githubusercontent.com/datajournalism-it/f1abb68e718b54f6a0fe/raw/23636ff76534439b52b87a67e766b11fa7373aa9/regioni-con-trento-bolzano.geojson',
                    # source='file://Users/bruand/Documents Local/analisi/Limiti01012020_g/Reg01012020_g/Reg01012020_g_WGS84.json',
                    type='fill',
                    below='traces',
                    color='rgba(112,161,215,0.8)'
                ),
                dict(
                    sourcetype='geojson',
                    source='https://gist.githubusercontent.com/datajournalism-it/f1abb68e718b54f6a0fe/raw/23636ff76534439b52b87a67e766b11fa7373aa9/regioni-con-trento-bolzano.geojson',
                    # source='file://Users/bruand/Documents Local/analisi/Limiti01012020_g/Reg01012020_g/Reg01012020_g_WGS84.json',
                    type='line',
                    below='traces',
                    color='white'
                )
            ],
        ),
        height=800,
        width=1500
    )

    return mappa_nazionale


def generate_riepilogo_mappa2(data: AnalisiDati):
    df = data.data_regionale_latest.sort_values(by="totale_casi", ascending=False)
    # print(df["codice_regione"][1251])
    # print(dati_json["features"][0]["properties"])

    # fig = px.choropleth_mapbox(df, geojson=dati_json,  color='totale_casi',
    #                            locations='codice_regione',
    #                            featureidkey="properties.codice_regione",
    #                            center={"lat": 42, "lon": 12},
    #                            mapbox_style="carto-positron", zoom=9)
    #                            mapbox_style="carto-positron",
    #                            zoom=3, center={"lat": 42, "lon": 12},
    #                            opacity=0.5,
    #                            labels={'totale_casi': 'Totale casi'}
    #                            )
    fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=df.denominazione, z=df.totale_casi,
                                        featureidkey="properties.Regione",
                                        colorscale="Viridis", zmin=0, zmax=df.totale_casi.max(),
                                        marker_opacity=0.5, marker_line_width=0))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=3, mapbox_center={"lat": 42, "lon": 12})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # fig.update_layout(
    #     title='Situazione nelle regioni',
    #     autosize=True,
    #     hovermode='closest',
    #     showlegend=True,
    #     mapbox=dict(
    #         accesstoken=mapbox_access_token,
    #         bearing=0,
    #         center=dict(
    #             lat=42,
    #             lon=12
    #         ),
    #         pitch=0,
    #         zoom=5,
    #         style='dark',
    #     ),
    #     height=800,
    #     width=1500
    # )
    return fig


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
                                line_shape="linear", color_discrete_sequence=px.colors.qualitative.Dark24)

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


def generate_riepilogo_bar_regione(data: AnalisiDati, regione: int, use_percentage: bool):
    df = data.data_regionale[data.data_regionale.codice_regione == regione]
    return generate_riepilogo_bar(data=df, use_percentage=use_percentage)


def generate_riepilogo_pressione_ospedali_bar_regione(data: AnalisiDati, regione: int, use_percentage: bool):
    df = data.data_regionale[data.data_regionale.codice_regione == regione]
    return generate_riepilogo_pressione_ospedali_bar(data=df, use_percentage=use_percentage)


def generate_riepilogo_bar(data: pd.DataFrame, use_percentage):
    y_contagi = data.incrementi_percentuali if use_percentage else data.incrementi
    y_tamponi = data.incrementi_tamponi_percentuali if use_percentage else data.incrementi_tamponi
    contagi_avg = y_contagi.mean()
    tamponi_avg = y_tamponi.mean()

    fig = go.Figure(data=[
        go.Bar(name='Nuovi contagi', x=data.giorni, y=[x if x < 4 * contagi_avg else 1 for x in y_contagi],
               marker_color='blue'),
        go.Bar(name='Nuovi tamponi', x=data.giorni, y=[x if x < 4 * tamponi_avg else 1 for x in y_tamponi],
               marker_color='green')
    ])
    # Change the bar mode
    fig.update_layout(
        barmode='group',
        hovermode=hovermode,
        height=default_height
    )
    fig.update_traces(
        opacity=1,
        textposition='outside',
        hovertemplate="%{y:.1%}" if use_percentage else "%{y:n}"
    )
    return fig


def generate_riepilogo_pressione_ospedali_bar(data: pd.DataFrame, use_percentage):
    y_ti= data.incrementi_ti_percentuali if use_percentage else data.incrementi_ti
    y_ricoverati = data.incrementi_ricoverati_percentuali if use_percentage else data.incrementi_ricoverati
    y_deceduti = data.incrementi_deceduti_percentuali if use_percentage else data.incrementi_deceduti
    ti_avg = y_ti.mean()
    ricoverati_avg = y_ricoverati.mean()
    deceduti_avg = y_deceduti.mean()

    fig = go.Figure(data=[
        # go.Bar(name='Terapie Intensive', x=data.giorni, y=[x if x < 4 * ti_avg else 1 for x in y_ti],
        #        marker_color='blue'),
        # go.Bar(name='Ospedalizzati', x=data.giorni, y=[x if x < 4 * ricoverati_avg else 1 for x in y_ricoverati],
        #        marker_color='green'),
        # go.Bar(name='Deceduti', x=data.giorni, y=[x if x < 4 * deceduti_avg else 1 for x in y_deceduti],
        #        marker_color='red')
        go.Bar(name='Terapie Intensive', x=data.giorni, y=y_ti, marker_color='blue', textposition='outside',
               marker_opacity=0.6),
        go.Bar(name='Ospedalizzati', x=data.giorni, y=y_ricoverati, marker_color='green', textposition='outside',
               marker_opacity=0.6),
        go.Bar(name='Deceduti', x=data.giorni, y=y_deceduti, marker_color='red', textposition='outside',
               marker_opacity=0.6)
    ])

    if not use_percentage:
        fig.add_trace(go.Scatter(name='Terapie Intensive', x=data.giorni, y=y_ti, marker_color='blue', mode='lines+markers'))
        fig.add_trace(go.Scatter(name='Ospedalizzati', x=data.giorni, y=y_ricoverati, marker_color='green', mode='lines+markers'))
        fig.add_trace(go.Scatter(name='Deceduti', x=data.giorni, y=y_deceduti, marker_color='red', mode='lines+markers'))
    # Change the bar mode
    fig.update_layout(
        barmode='group',
        hovermode=hovermode,
        height=default_height
    )
    fig.update_traces(
        opacity=1,
        hovertemplate="%{y:.1%}" if use_percentage else "%{y:n}"
    )
    return fig


def generate_table_from_data(data: AnalisiDati) -> dt.DataTable:
    #df = data.data_regionale[data.data_regionale.codice_regione == regione]
    df = pd.merge(data.data_nazionale_latest, data.data_regionale_latest, how='outer')
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
                {'id': 'casi_testati', 'name': 'Casi t.'},
                {'id': 'incrementi_tamponi', 'name': 'Incr. tamponi'},
                {'id': 'incrementi_ti', 'name': 'Incr. t.intensiva'},
                {'id': 'incrementi_ricoverati', 'name': 'Incr. ricoverati'},
                {'id': 'incrementi_deceduti', 'name': 'Incr. deceduti'},
                {'id': 'incrementi_casi_testati', 'name': 'Incr. casi testati'},
                {'id': 'incrementi_casi_da_sospetto_diagnostico', 'name': 'Incr. casi diagnostici'},
                {'id': 'incrementi_casi_da_screening', 'name': 'Incr. casi screening'}
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
            'casi_testati',
            'incrementi_tamponi',
            'incrementi_ti',
            'incrementi_ricoverati',
            'incrementi_deceduti',
            'incrementi_casi_testati',
            'incrementi_casi_da_sospetto_diagnostico',
            'incrementi_casi_da_screening'
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
                               ] + [
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
                                     'tamponi'
                                     'casi_testati',
                                     'incrementi_tamponi',
                                     'incrementi_ti',
                                     'incrementi_ricoverati',
                                     'incrementi_deceduti',
                                     'incrementi_casi_testati',
                                     'incrementi_casi_da_sospetto_diagnostico',
                                     'incrementi_casi_da_screening']
                               ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        fixed_columns={'headers': True, 'data': 2},
        fixed_rows={'headers': True, 'data': 0},
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
    )

    return data_table


def generate_riepilogo_regionale_bar_plain(data: AnalisiDati, regione: int):
    return generate_riepilogo_bar_regione(data, regione, False)


def generate_riepilogo_regionale_bar_percentuale(data: AnalisiDati, regione: int):
    return generate_riepilogo_bar_regione(data, regione, True)


def generate_riepilogo_pressione_ospedali_regionale_bar_plain(data: AnalisiDati, regione: int):
    return generate_riepilogo_pressione_ospedali_bar_regione(data, regione, False)


def generate_riepilogo_pressione_ospedali_regionale_bar_percentuale(data: AnalisiDati, regione: int):
    return generate_riepilogo_pressione_ospedali_bar_regione(data, regione, True)


def generate_riepilogo_nazionale_bar_plain(data: AnalisiDati):
    df = data.data_nazionale
    return generate_riepilogo_bar(df, False)


def generate_riepilogo_nazionale_bar_percentuale(data: AnalisiDati):
    df = data.data_nazionale
    return generate_riepilogo_bar(df, True)


def generate_riepilogo_pressione_ospedali_nazionale_bar_plain(data: AnalisiDati):
    df = data.data_nazionale
    return generate_riepilogo_pressione_ospedali_bar(df, False)


def generate_riepilogo_pressione_ospedali_nazionale_bar_percentuale(data: AnalisiDati):
    df = data.data_nazionale
    return generate_riepilogo_pressione_ospedali_bar(df, True)


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
    # shape_path = "/Users/bruand/Documents Local/analisi/Limiti01012020_g/Reg01012020_g/Reg01012020_g_WGS84"
    # sf = shapefile.Reader(shape_path)
    # print(sf)
    repo_path = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master"
    nazionale = f'{repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
    regioni = f'{repo_path}/dati-regioni/dpc-covid19-ita-regioni.csv'
    province = f'{repo_path}/dati-province/dpc-covid19-ita-province.csv'

    analysis = AnalisiDati(file_nazionale=nazionale, file_regioni=regioni,
                           file_province=province, show=False, store=True, color_map="brg", max_days=30)

    last_update_date = dateutil.parser.parse(analysis.last_update)

    selected_region = 15

    riepilogo_nazionale = generate_riepilogo_nazionale(analysis)

    mappa_nazionale = generate_riepilogo_mappa(analysis)

    riepilogo_regioni = generate_riepilogo_regionale(analysis)

    riepilogo_province = generate_riepilogo_province(analysis, selected_region)

    bar_chart = generate_riepilogo_nazionale_bar_plain(analysis)

    bar_chart_percentuale = generate_riepilogo_nazionale_bar_percentuale(analysis)

    bar_chart_regione = generate_riepilogo_regionale_bar_plain(analysis, selected_region)

    bar_chart_regione_percentuale = generate_riepilogo_regionale_bar_percentuale(analysis, selected_region)

    bar_chart_po = generate_riepilogo_pressione_ospedali_nazionale_bar_plain(analysis)

    bar_chart_percentuale_po = generate_riepilogo_pressione_ospedali_nazionale_bar_percentuale(analysis)

    bar_chart_regione_po = generate_riepilogo_pressione_ospedali_regionale_bar_plain(analysis, selected_region)

    bar_chart_regione_percentuale_po = generate_riepilogo_pressione_ospedali_regionale_bar_percentuale(analysis, selected_region)

    full_dt = generate_table_from_data(analysis)
    print(f'Analisi covid 19 in Italia a {last_update_date.strftime("%A %d %B %Y")}')

    app = dash.Dash()
    app.layout = html.Div(children=[
        html.H1(children=f'Analisi covid 19 in Italia a {last_update_date.strftime("%A %d %B %Y")}'),
        html.Hr(),
        html.Div(id="mappa_italia", children=[
            html.H2(children='Mappa del contagio in Italia'),
            html.Hr(),
            dcc.Graph(figure=mappa_nazionale)
        ]),
        html.Hr(),
        html.Div(id="riepilogo_table", children=[
            html.H3(children='Tabella riepilogativa'),
            html.Hr(),
            full_dt
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
        html.Div(id="riepilogo_bar", children=[
            html.H3(children='Grafico a barre riepilogativo '),
            html.Hr(),
            dcc.Graph(figure=bar_chart)
        ]),
        html.Hr(),
        html.Div(id="riepilogo_bar_perc", children=[
            html.H3(children='Grafico a barre riepilogativo in percentuale'),
            html.Hr(),
            dcc.Graph(figure=bar_chart_percentuale)
        ]),
        html.Hr(),
        html.Div(id="riepilogo_bar_po", children=[
            html.H3(children='Grafico a barre riepilogativo pressione ospedali'),
            html.Hr(),
            dcc.Graph(figure=bar_chart_po)
        ]),
        html.Hr(),
        html.Div(id="riepilogo_bar_perc_po", children=[
            html.H3(children='Grafico a barre riepilogativo pressione ospedali in percentuale'),
            html.Hr(),
            dcc.Graph(figure=bar_chart_percentuale_po)
        ]),
        html.Hr(),
        html.H2(children='Analisi covid 19 in Campania'),
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
        html.Div(id="riepilogo_regione_bar_po", children=[
            html.H3(children='Grafico a barre riepilogativo pressione ospedali della Campania'),
            html.Hr(),
            dcc.Graph(figure=bar_chart_regione_po)
        ]),
        html.Hr(),
        html.Div(id="riepilogo_regione_bar_perc_po", children=[
            html.H3(children='Grafico a barre riepilogativo pressione ospedali della Campania in percentuale'),
            html.Hr(),
            dcc.Graph(figure=bar_chart_regione_percentuale_po)
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
