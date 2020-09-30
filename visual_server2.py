from CovidData import Covid19Italia
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import dash_table.FormatTemplate as FormatTemplate
import plotly.express as px
import locale
import pandas as pd

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
default_height = 800
hovermode = "x"
mapbox_access_token = open(".mapbox_token").read()
colors = px.colors.cyclical.HSV


class VisualServer:
    _data_manager: Covid19Italia = None
    _selected_region: int = 15

    def __init__(self):
        self._selected_region = 15

    @property
    def selected_region(self) -> int:
        return self._selected_region

    @selected_region.setter
    def selected_region(self, value:int):
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
                    {'id': 'formatted_date', 'name': 'Data'},
                    {'id': 'denominazione_regione', 'name': 'Regione'},
                    {'id': 'nuovi_positivi', 'name': 'Nuovi positivi', 'type': 'numeric'},
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
                'formatted_date',
                'ricoverati_con_sintomi',
                'terapia_intensiva',
                'totale_ospedalizzati',
                'isolamento_domiciliare',
                'totale_positivi',
                'variazione_totale_positivi',
                'nuovi_positivi',
                'dimessi_guariti',
                'deceduti',
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
                                       {'if': {'column_id': 'denominazione_regione'},
                                        'width': '80%',
                                        'minWidth': '200px',
                                        'textAlign': 'left',
                                        }
                                   ] + [
                                       {'if': {'column_id': c},
                                        'width': '10%',
                                        'minWidth': '150px',
                                        'textAlign': 'left'} for c in [
                    'formatted_date',
                    'ricoverati_con_sintomi',
                    'terapia_intensiva',
                    'totale_ospedalizzati',
                    'isolamento_domiciliare',
                    'totale_positivi',
                    'variazione_totale_positivi',
                    'nuovi_positivi',
                    'dimessi_guariti',
                    'deceduti',
                    'casi_da_sospetto_diagnostico',
                    'casi_da_screening',
                    'totale_casi',
                    'tamponi',
                    'casi_testati',
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
                ]
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

    def generate_table_from_data_province(self) -> dt.DataTable:
        data = self.data_manager.dati_provinciali_latest.sort_values(by=['codice_regione', 'codice_provincia'])
        data_table = dt.DataTable(
            id='rdtp',
            columns=(
                [
                    {'id': 'formatted_date', 'name': 'Data'},
                    {'id': 'denominazione_regione', 'name': 'Regione'},
                    {'id': 'denominazione_provincia', 'name': 'Provincia'},
                    {'id': 'totale_casi', 'name': 'Casi', 'type': 'numeric'},
                    {'id': 'variazione_totale_casi', 'name': 'Var. Casi', 'type': 'numeric'},
                    {'id': 'percentuale_variazione_totale_casi', 'name': 'Perc. incremento', 'type': 'numeric',
                     'format': FormatTemplate.percentage(2, rounded=False)},
                ]
            ),
            data=data[[
                'formatted_date',
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
                                       {'if': {'column_id': c},
                                        'width': '80%',
                                        'minWidth': '200px',
                                        'textAlign': 'left',
                                        } for c in [
                    'denominazione_provincia',
                    'denominazione_regione'
                ]
                                   ] + [
                                       {'if': {'column_id': c},
                                        'width': '10%',
                                        'minWidth': '150px',
                                        'textAlign': 'left'} for c in [
                    'formatted_date',
                    'totale_casi',
                    'isolamento_domiciliare',
                    'variazione_totale_casi',
                    'percentuale_variazione_totale_casi',
                ]
                                   ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            fixed_columns={'headers': True, 'data': 3},
            fixed_rows={'headers': True, 'data': 0},
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
                    f' ({data.nuovi_positivi.iloc[0]} su {data.variazione_casi_testati.iloc[0]:.0f})'
                ]),
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
            html.Hr(),
            html.H2(children=[
                'Riepilogo dati in regione ',
                self.data_manager.dati_regionali_latest[
                    self.data_manager.dati_regionali_latest.codice_regione == self.selected_region].denominazione_regione.iloc[
                    0]]),
            html.Hr(),
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


if __name__ == '__main__':
    v = VisualServer()
    v.run_server()
