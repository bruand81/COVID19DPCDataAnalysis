from CovidModels.Covid19Italia import Covid19Italia
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_table as dt
import dash_table.FormatTemplate as FormatTemplate
import plotly.express as px
import locale
import pandas as pd
from urllib.request import urlopen
import orjson

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')


class VisualServer:
    _data_manager: Covid19Italia = None
    _selected_region: int = 15
    _default_height = 800
    _hovermode = "x"
    _mapbox_access_token = open(".mapbox_token").read()
    _colors = px.colors.cyclical.HSV
    _geojson: orjson = None
    _report_axis = {'nuovi_positivi': {'title': 'Nuovi positivi', 'scale': 1},
                    'variazione_deceduti': {'title': 'Decessi', 'scale': 1},
                    'variazione_dimessi_guariti': {'title': 'Guariti', 'scale': 1},
                    'variazione_terapia_intensiva': {'title': 'Terapia intensiva', 'scale': 1},
                    'variazione_ricoverati_con_sintomi': {'title': 'Ricoverati', 'scale': 1},
                    'variazione_tamponi': {'title': 'Tamponi', 'scale': 100},
                    'nuovi_positivi_7dma': {'title': 'Nuovi positivi (7DMA)', 'scale': 1},
                    'nuovi_positivi_3dma': {'title': 'Nuovi positivi (3DMA)', 'scale': 1},
                    }

    def __init__(self):
        self._selected_region = 15

    @property
    def selected_region(self) -> int:
        return self._selected_region

    @selected_region.setter
    def selected_region(self, value: int):
        self._selected_region = value

    @property
    def data_manager(self) -> Covid19Italia:
        if self._data_manager is None:
            self._data_manager = Covid19Italia()
        return self._data_manager

    def generate_table_from_data(self) -> dt.DataTable:
        data = self.data_manager.dati_completi_latest
        data_table = dt.DataTable(
            id='rdt',
            columns=(
                [
                    # {'id': 'formatted_date', 'name': 'Data'},
                    {'id': 'denominazione_regione', 'name': 'Regione'},
                    {'id': 'nuovi_positivi', 'name': 'Nuovi positivi', 'type': 'numeric'},
                    {'id': 'nuovi_positivi_7dma', 'name': 'Nuovi positivi (7DMA)', 'type': 'numeric'},
                    {'id': 'nuovi_positivi_3dma', 'name': 'Nuovi positivi (3DMA)', 'type': 'numeric'},
                    {'id': 'variazione_tamponi', 'name': 'Var. Tamponi', 'type': 'numeric'},
                    {'id': 'variazione_casi_testati', 'name': 'Var. Persone', 'type': 'numeric'},
                    {'id': 'variazione_terapia_intensiva', 'name': 'Var. T.I.', 'type': 'numeric'},
                    {'id': 'variazione_ricoverati_con_sintomi', 'name': 'Var Sintomi', 'type': 'numeric'},
                    {'id': 'variazione_deceduti', 'name': 'Var. Decessi', 'type': 'numeric'},
                    {'id': 'variazione_dimessi_guariti', 'name': 'Var. Guariti', 'type': 'numeric'},
                    {'id': 'percentuale_positivi_tamponi_giornaliera', 'name': 'Positivi/Tamponi oggi',
                     'type': 'numeric', 'format': FormatTemplate.percentage(2, rounded=False)},
                    {'id': 'percentuale_positivi_casi_giornaliera', 'name': 'Positivi/Persone oggi', 'type': 'numeric',
                     'format': FormatTemplate.percentage(2, rounded=False)},
                    {'id': 'ricoverati_con_sintomi', 'name': 'Ricoverati con sintomi', 'type': 'numeric'},
                    {'id': 'terapia_intensiva', 'name': 'Terapia Intensiva', 'type': 'numeric'},
                    {'id': 'totale_ospedalizzati', 'name': 'Ospedalizzati', 'type': 'numeric'},
                    {'id': 'isolamento_domiciliare', 'name': 'Isolamento', 'type': 'numeric'},
                    {'id': 'totale_positivi', 'name': 'Positivi', 'type': 'numeric'},
                    {'id': 'variazione_totale_positivi', 'name': 'Var. Positivi', 'type': 'numeric'},
                    {'id': 'dimessi_guariti', 'name': 'Guariti', 'type': 'numeric'},
                    {'id': 'deceduti', 'name': 'Decessi', 'type': 'numeric'},
                    {'id': 'CFR', 'name': 'Case Fatality Rate', 'type': 'numeric',
                     'format': FormatTemplate.percentage(2, rounded=False)},
                    {'id': 'casi_da_sospetto_diagnostico', 'name': 'Sospetto diagnostico', 'type': 'numeric'},
                    {'id': 'casi_da_screening', 'name': 'Screening', 'type': 'numeric'},
                    {'id': 'totale_casi', 'name': 'Casi', 'type': 'numeric'},
                    {'id': 'tamponi', 'name': 'Tamponi', 'type': 'numeric'},
                    {'id': 'casi_testati', 'name': 'Persone', 'type': 'numeric'},
                    {'id': 'variazione_isolamento_domiciliare', 'name': 'Var. Isolamento', 'type': 'numeric'},
                    {'id': 'variazione_casi_da_screening', 'name': 'Var. Screening', 'type': 'numeric'},
                    {'id': 'variazione_casi_da_sospetto_diagnostico', 'name': 'Var. Sospetto diagnostico',
                     'type': 'numeric'},
                    {'id': 'percentuale_positivi_tamponi', 'name': 'Positivi/Tamponi', 'type': 'numeric',
                     'format': FormatTemplate.percentage(2, rounded=False)},
                    {'id': 'percentuale_positivi_casi', 'name': 'Positivi/Persone', 'type': 'numeric',
                     'format': FormatTemplate.percentage(2, rounded=False)},
                ]
            ),
            data=data[[
                # 'formatted_date',
                'ricoverati_con_sintomi',
                'terapia_intensiva',
                'totale_ospedalizzati',
                'isolamento_domiciliare',
                'totale_positivi',
                'variazione_totale_positivi',
                'nuovi_positivi',
                'nuovi_positivi_7dma',
                'nuovi_positivi_3dma',
                'dimessi_guariti',
                'deceduti',
                'CFR',
                'casi_da_sospetto_diagnostico',
                'casi_da_screening',
                'totale_casi',
                'tamponi',
                'casi_testati',
                'denominazione_regione',
                'variazione_tamponi',
                'variazione_casi_testati',
                'variazione_terapia_intensiva',
                'variazione_ricoverati_con_sintomi',
                'variazione_deceduti',
                'variazione_dimessi_guariti',
                'variazione_isolamento_domiciliare',
                'variazione_casi_da_screening',
                'variazione_casi_da_sospetto_diagnostico',
                'percentuale_positivi_tamponi',
                'percentuale_positivi_tamponi_giornaliera',
                'percentuale_positivi_casi',
                'percentuale_positivi_casi_giornaliera',
            ]].to_dict(orient='records'),
            editable=False,
            style_table={
                'height': 'auto',
                'minWidth': '500px', 'maxWidth': '90%',
                'whiteSpace': 'normal',
                'overflowX': 'scroll',
                'maxHeight': self._default_height,
                'overflowY': 'scroll',
                'textAlign': 'left'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            # style_cell_conditional=[
            #                            {'if': {'column_id': 'denominazione_regione'},
            #                             'width': '60%',
            #                             'minWidth': '100px',
            #                             'textAlign': 'left',
            #                             }
            #                        ] + [
            #                            {'if': {'column_id': c},
            #                             'width': '10%',
            #                             'minWidth': '50px',
            #                             'textAlign': 'left'} for c in [
            #                                 # 'formatted_date',
            #                                 'ricoverati_con_sintomi',
            #                                 'terapia_intensiva',
            #                                 'totale_ospedalizzati',
            #                                 'isolamento_domiciliare',
            #                                 'totale_positivi',
            #                                 'variazione_totale_positivi',
            #                                 'nuovi_positivi',
            #                                 'nuovi_positivi_7dma',
            #                                 'nuovi_positivi_3dma',
            #                                 'dimessi_guariti',
            #                                 'deceduti',
            #                                 'CFR',
            #                                 'casi_da_sospetto_diagnostico',
            #                                 'casi_da_screening',
            #                                 'totale_casi',
            #                                 'tamponi',
            #                                 'casi_testati',
            #                                 'variazione_tamponi',
            #                                 'variazione_casi_testati',
            #                                 'variazione_terapia_intensiva',
            #                                 'variazione_ricoverati_con_sintomi',
            #                                 'variazione_deceduti',
            #                                 'variazione_dimessi_guariti',
            #                                 'variazione_isolamento_domiciliare',
            #                                 'variazione_casi_da_screening',
            #                                 'variazione_casi_da_sospetto_diagnostico',
            #                                 'percentuale_positivi_tamponi',
            #                                 'percentuale_positivi_tamponi_giornaliera',
            #                                 'percentuale_positivi_casi',
            #                                 'percentuale_positivi_casi_giornaliera',
            #                             ]
            #                        ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            fixed_columns={'headers': True, 'data': 1},
            # fixed_rows={'headers': True, 'data': 0},
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
        )

        return data_table

    def generate_table_from_data_province(self) -> dt.DataTable:
        data = self.data_manager.dati_provinciali_latest.sort_values(by=['codice_regione', 'codice_provincia'])
        data_table = dt.DataTable(
            id='rdtp',
            columns=(
                [
                    # {'id': 'formatted_date', 'name': 'Data'},
                    {'id': 'denominazione_provincia', 'name': 'Provincia'},
                    {'id': 'denominazione_regione', 'name': 'Regione'},
                    {'id': 'totale_casi', 'name': 'Casi', 'type': 'numeric'},
                    {'id': 'variazione_totale_casi', 'name': 'Var. Casi', 'type': 'numeric'},
                    {'id': 'percentuale_variazione_totale_casi', 'name': 'Perc. incremento', 'type': 'numeric',
                     'format': FormatTemplate.percentage(2, rounded=False)},
                ]
            ),
            data=data[[
                # 'formatted_date',
                'denominazione_regione',
                'denominazione_provincia',
                'totale_casi',
                'variazione_totale_casi',
                'percentuale_variazione_totale_casi',
            ]].to_dict(orient='records'),
            editable=False,
            style_table={
                'height': 'auto',
                'minWidth': '500px', 'maxWidth': '90%',
                'whiteSpace': 'normal',
                'overflowX': 'scroll',
                'maxHeight': self._default_height,
                'overflowY': 'scroll',
                'textAlign': 'left'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            # style_cell_conditional=[
            #     {'if': {'column_id': c},
            #      'width': '10%',
            #      'minWidth': '50px',
            #      'textAlign': 'left'} for c in [
            #         'denominazione_provincia'
            #         'denominazione_regione',
            #         # 'formatted_date',
            #         'totale_casi',
            #         'isolamento_domiciliare',
            #         'variazione_totale_casi',
            #         'percentuale_variazione_totale_casi',
            #     ]
            # ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            # fixed_columns={'headers': True, 'data': 2},
            # fixed_rows={'headers': True, 'data': 0},
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
        )

        return data_table

    def dati_essenziali(self, data: pd.DataFrame, id: str) -> html.Div:
        return html.Div(id=id, children=[
            html.H3(children=[
                'Percentuale positivi/tamponi: ',
                html.Span(style={'color': 'red' if (
                        data.percentuale_positivi_tamponi_giornaliera.iloc[
                            0] >= 0.03) else 'green'},
                          children=f'{data.percentuale_positivi_tamponi_giornaliera.iloc[0]:.2%}'),
                f' ({data.nuovi_positivi.iloc[0]} su {data.variazione_tamponi.iloc[0]:.0f})',
                ' - Percentuale positivi/persone testate: ',
                html.Span(style={'color': 'red' if (
                        data.percentuale_positivi_casi_giornaliera.iloc[
                            0] >= 0.03) else 'green'},
                          children=f'{data.percentuale_positivi_casi_giornaliera.iloc[0]:.2%}'),
                f' ({data.nuovi_positivi.iloc[0]} su {data.variazione_casi_testati.iloc[0]:.0f})',
                ' - CFR: ',
                f'{data.CFR.iloc[0]:.2%}'
            ]),
        ])

    def generate_map(self) -> html.Div:
        df = self.data_manager.dati_regionali_latest.sort_values(by="totale_casi", ascending=False)
        mappa_nazionale = px.scatter_mapbox(df, lat="lat", lon="long", color="denominazione_regione",
                                            size="totale_casi",
                                            color_discrete_sequence=px.colors.qualitative.Light24,
                                            hover_data=['totale_casi', 'casi_da_sospetto_diagnostico',
                                                        'casi_da_screening', 'deceduti', 'terapia_intensiva'],
                                            # color_discrete_sequence=['red'],
                                            labels={
                                                'denominazione_regione': 'Denominazione regione',
                                                'totale_casi': 'Totale casi',
                                                'casi_da_sospetto_diagnostico': 'Nuove diagnosi',
                                                'casi_da_screening': 'Screening',
                                                'deceduti': 'Deceduti',
                                                'terapia_intensiva': 'Terapia intensiva'
                                            })

        mappa_nazionale.update_layout(
            title='Situazione nelle regioni',
            autosize=True,
            hovermode='closest',
            showlegend=True,
            mapbox=dict(
                accesstoken=self._mapbox_access_token,
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
                        type='fill',
                        below='traces',
                        color='rgba(112,161,215,0.8)'
                        # color=px.colors.qualitative.Light24
                    ),
                    dict(
                        sourcetype='geojson',
                        source='https://gist.githubusercontent.com/datajournalism-it/f1abb68e718b54f6a0fe/raw/23636ff76534439b52b87a67e766b11fa7373aa9/regioni-con-trento-bolzano.geojson',
                        type='line',
                        below='traces',
                        color='white'
                    )
                ],
            ),
            height=800,
            width=1500
        )

        return html.Div(id="mappa_italia", children=[
            html.H2(children='Mappa del contagio in Italia'),
            html.Hr(),
            dcc.Graph(figure=mappa_nazionale)
        ])

    @property
    def geojson(self) -> orjson:
        if self._geojson is None:
            print('Elaborazione dati geojson')
            with open(
                    'files/regioni-con-trento-bolzano.geojson') as response:
                geojson = orjson.loads(response.read())
                correspondance_dict = {"Piemonte": "Piemonte",
                                       "Valle d'Aosta": "Valle d'Aosta",
                                       "Lombardia": "Lombardia",
                                       "Veneto": "Veneto",
                                       "Friuli Venezia Giulia": "Friuli Venezia Giulia",
                                       "Liguria": "Liguria",
                                       "Emilia Romagna": "Emilia-Romagna",
                                       "Toscana": "Toscana",
                                       "Umbria": "Umbria",
                                       "Marche": "Marche",
                                       "Lazio": "Lazio",
                                       "Abruzzo": "Abruzzo",
                                       "Molise": "Molise",
                                       "Campania": "Campania",
                                       "Puglia": "Puglia",
                                       "Basilicata": "Basilicata",
                                       "Calabria": "Calabria",
                                       "Sicilia": "Sicilia",
                                       "Sardegna": "Sardegna",
                                       "Bolzano": "P.A. Bolzano",
                                       "Trento": "P.A. Trento", }
                for i in range(len(geojson['features'])):
                    key = geojson["features"][i]["properties"]["Regione"]
                    value = correspondance_dict[key]
                    geojson["features"][i]["properties"]["denominazione_regione"] = value
                self._geojson = geojson
        return self._geojson

    def generate_choropleth_map(self) -> html.Div:
        df = self.data_manager.dati_regionali_latest
        df.reset_index(inplace=True)

        fig = px.choropleth_mapbox(df, geojson=self.geojson,
                                   color="denominazione_regione",
                                   locations="denominazione_regione",
                                   featureidkey="properties.denominazione_regione",
                                   color_discrete_sequence=px.colors.qualitative.Light24,
                                   # color_continuous_scale="Viridis",
                                   # range_color=(0, 12),
                                   center={"lat": 42, "lon": 12},
                                   mapbox_style="white-bg",
                                   zoom=5,
                                   opacity=0.5,
                                   hover_data=['totale_casi',
                                               'casi_da_sospetto_diagnostico',
                                               'casi_da_screening',
                                               'deceduti',
                                               'terapia_intensiva',
                                               'CFR_str',
                                               'nuovi_positivi_7dma',
                                               'nuovi_positivi_3dma'],
                                   labels={
                                       'denominazione_regione': 'Denominazione regione',
                                       'totale_casi': 'Totale casi',
                                       'casi_da_sospetto_diagnostico': 'Nuove diagnosi',
                                       'casi_da_screening': 'Screening',
                                       'deceduti': 'Deceduti',
                                       'terapia_intensiva': 'Terapia intensiva',
                                       'CFR_str': 'Case Fatality Rate',
                                       'nuovi_positivi_7dma': 'Nuovi positivi (7DMA)',
                                       'nuovi_positivi_3dma': 'Nuovi positivi (3DMA)',
                                   })
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          title='Situazione nelle regioni',
                          autosize=True,
                          hovermode='closest',
                          showlegend=True,
                          # mapbox=dict(
                          #     accesstoken=self._mapbox_access_token,
                          #     bearing=0,
                          #     center=dict(
                          #         lat=42,
                          #         lon=12
                          #     ),
                          #     pitch=0,
                          #     zoom=5,
                          #     style='dark',
                          # ),
                          height=800,
                          width=1500
                          )

        return html.Div(id="mappa_italia", children=[
            html.H2(children='Mappa del contagio in Italia'),
            html.Hr(),
            dcc.Graph(figure=fig,
                      style={'height': self._default_height})
        ])

    def immagine_riepilogo(self, data: pd.DataFrame) -> html.Div:
        nome = data.denominazione_regione.iloc[0]
        codice = data.codice_regione.iloc[0]

        riepilogo = go.Figure()

        i = 0
        for key in self._report_axis.keys():
            riepilogo.add_trace(go.Scatter(x=data.date, y=data[key] / self._report_axis[key]['scale'],
                                           text=data[key],
                                           name=self._report_axis[key]['title'],
                                           line_color=self._colors[i]))
            i += 1

        riepilogo.update_layout(
            hovermode=self._hovermode,
            height=self._default_height
        )
        riepilogo.update_traces(
            mode='lines+markers',
            textposition="bottom center",
            hovertemplate="%{y:n}"
        )

        return html.Div(id=f'riepilogo_{codice}', children=[
            html.H3(children=f'Andamento {nome}'),
            html.Hr(),
            dcc.Graph(figure=riepilogo)
        ])

    def serve_layout(self) -> html.Div:
        return html.Div(children=[
            html.H1(children=self.data_manager.latest_update_date.strftime(
                "Aggiornamenti situazione COVID19 Italia a %A %d %B %Y")),
            html.Hr(),
            html.H2(children='Italia'),
            self.dati_essenziali(self.data_manager.dati_nazionali_latest, 'valori_essenziali'),
            html.Hr(),
            html.Div(id="riepilogo_table", children=[
                html.H3(children='Tabella riepilogativa'),
                html.Hr(),
                self.generate_table_from_data()
            ]),
            self.generate_choropleth_map(),
            self.immagine_riepilogo(self.data_manager.dati_nazionali),
            html.Hr(),
            html.H2(children=[
                'Riepilogo dati in regione ',
                self.data_manager.dati_regionali_latest[
                    self.data_manager.dati_regionali_latest.codice_regione == self.selected_region].denominazione_regione.iloc[
                    0]]),
            html.Hr(),
            self.immagine_riepilogo(self.data_manager.dati_regionali[
                                        self.data_manager.dati_regionali.codice_regione == self.selected_region]),
            self.dati_essenziali(self.data_manager.dati_regionali_latest[
                                     self.data_manager.dati_regionali_latest.codice_regione == self.selected_region],
                                 'valori_essenziali_regione'),
            html.Hr(),
            html.H2(children='Situazione province'),
            html.Hr(),
            html.Div(id="riepilogo_table_province", children=[
                html.H3(children='Tabella riepilogativa delle province'),
                html.Hr(),
                self.generate_table_from_data_province()
            ]),
        ]
        )

    def run_server(self):
        self.data_manager.max_days = 30
        self.selected_region = 15

        print(self.data_manager.latest_update_date.strftime("Aggiornamenti situazione COVID19 Italia a %A %d %B %Y"))

        app = dash.Dash()
        app.layout = self.serve_layout()

        app.run_server(debug=True)
