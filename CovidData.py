import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta

class Covid19Italia:
    __repo_path = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master"
    __nazionale = f'{__repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
    __nazionale_latest = f'{__repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale-latest.csv'
    __regioni = f'{__repo_path}/dati-regioni/dpc-covid19-ita-regioni.csv'
    __province = f'{__repo_path}/dati-province/dpc-covid19-ita-province.csv'
    __variation_columns = ['tamponi','casi_testati','terapia_intensiva','ricoverati_con_sintomi', 'deceduti', 'dimessi_guariti', 'isolamento_domiciliare', 'casi_da_screening', 'casi_da_sospetto_diagnostico']
    __variation_columns_province = ['totale_casi']
    __renamed_columns = {x: f'variazione_{x}' for x in __variation_columns}
    __percentage_renamed_columns = {x: f'percentuale_variazione_{x}' for x in __variation_columns}
    __renamed_columns_province = {x: f'variazione_{x}' for x in __variation_columns_province}
    __percentage_renamed_columns_province = {x: f'percentuale_variazione_{x}' for x in __variation_columns_province}
    __full_data: pd.DataFrame = None
    __dati_provinciali = None
    max_days=np.inf

    def __init_full_data(self):
        print('Processamento dati riepilogativi nazionali e regionali')
        data_naz = pd.read_csv(self.__nazionale)
        data_reg = pd.read_csv(self.__regioni)
        data_naz.sort_values(by='data', inplace=True)
        data_naz.fillna(0, inplace=True)
        data_naz['codice_regione'] = 0
        data_naz['denominazione_regione'] = 'Italia'
        data_naz['lat'] = 41.89277044
        data_naz['long'] = 12.48366722
        data_reg.fillna(0, inplace=True)
        self.__full_data = pd.merge(data_naz, data_reg, how='outer')
        regions = self.__full_data.codice_regione.unique()
        self.__full_data[list(self.__renamed_columns.values())] = 0
        self.__full_data[list(self.__percentage_renamed_columns.values())] = 0.0
        for region in regions:
            selected_rows = self.__full_data.codice_regione == region
            increments = self.__full_data[selected_rows][self.__variation_columns].diff()
            is_NaN = increments.isnull()
            row_has_NaN = is_NaN.any(axis=1)
            rows_cleaned = self.__full_data[selected_rows][row_has_NaN]
            increments[row_has_NaN] = rows_cleaned[self.__variation_columns]
            increments.rename(columns=self.__renamed_columns, inplace=True)
            increments_percentage = increments.pct_change(fill_method='ffill')
            # self.__full_data[selected_rows] =
            for key in self.__renamed_columns:
                column_indexer = self.__renamed_columns[key]
                percentage_column_indexer = self.__percentage_renamed_columns[key]
                self.__full_data.loc[selected_rows, column_indexer] = increments[column_indexer]
                self.__full_data.loc[selected_rows, percentage_column_indexer] = increments_percentage[column_indexer]

        # for key in self.__renamed_columns:
        #     variation_key = self.__renamed_columns[key]
        #     new_column_names = f'percentuale_{variation_key}'
        #     self.__full_data[new_column_names] = self.__full_data[key].divide(self.__full_data[variation_key])

        self.__full_data['percentuale_positivi_tamponi'] = self.__full_data['totale_positivi'].divide(
            self.__full_data['tamponi'])
        self.__full_data['percentuale_positivi_tamponi_giornaliera'] = self.__full_data['nuovi_positivi'].divide(
            self.__full_data['variazione_tamponi'])
        self.__full_data['percentuale_positivi_casi'] = self.__full_data['totale_positivi'].divide(
            self.__full_data['casi_testati'])
        self.__full_data['percentuale_positivi_casi_giornaliera'] = self.__full_data['nuovi_positivi'].divide(
            self.__full_data['variazione_casi_testati'])
        self.__full_data.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.__full_data.fillna(0, inplace=True)
        self.__full_data['date'] = pd.to_datetime(self.__full_data['data'])
        self.__full_data['formatted_date'] = self.__full_data.date.dt.strftime('%d/%m/%Y')

    def __init_province(self):
        print('Processamento dati riepilogativi provinciali')
        self.__dati_provinciali = pd.read_csv(self.__province)
        self.__dati_provinciali.fillna(0, inplace=True)
        counties = self.__dati_provinciali.codice_provincia.unique()
        self.__dati_provinciali[list(self.__renamed_columns_province.values())] = 0.0
        for county in counties:
            selected_rows = self.__dati_provinciali.codice_provincia == county
            increments = self.__dati_provinciali[selected_rows][self.__variation_columns_province].diff()
            is_NaN = increments.isnull()
            row_has_NaN = is_NaN.any(axis=1)
            rows_cleaned = self.__dati_provinciali[selected_rows][row_has_NaN]
            increments[row_has_NaN] = rows_cleaned[self.__variation_columns_province]
            increments.rename(columns=self.__renamed_columns_province, inplace=True)
            increments_percentage = increments.pct_change(fill_method='ffill')
            # self.__full_data[selected_rows] =
            for key in self.__renamed_columns_province:
                column_indexer = self.__renamed_columns_province[key]
                percentage_column_indexer = self.__percentage_renamed_columns_province[key]
                self.__dati_provinciali.loc[selected_rows, column_indexer] = increments[column_indexer]
                self.__dati_provinciali.loc[selected_rows, percentage_column_indexer] = increments_percentage[column_indexer]

            # for key in self.__renamed_columns_province:
            #     variation_key = self.__renamed_columns_province[key]
            #     new_column_names = f'percentuale_{variation_key}'
            #     self.__dati_provinciali[new_column_names] = self.__dati_provinciali[key].divide(self.__dati_provinciali[variation_key])

            self.__dati_provinciali.replace([np.inf, -np.inf], np.nan, inplace=True)
            self.__dati_provinciali.fillna(0, inplace=True)
            self.__dati_provinciali['date'] = pd.to_datetime(self.__dati_provinciali['data'])
            self.__dati_provinciali['formatted_date'] = self.__dati_provinciali.date.dt.strftime('%d/%m/%Y')

    @property
    def dati_nazionali(self) -> pd.DataFrame:
        if self.__full_data is None:
            self.__init_full_data()
        if math.isinf(self.max_days):
            return self.__full_data[self.__full_data.codice_regione == 0]
        else:
            return self.get_last_days_of_data(self.max_days, self.__full_data[self.__full_data.codice_regione == 0])

    @property
    def dati_regionali(self) -> pd.DataFrame:
        if self.__full_data is None:
            self.__init_full_data()
        if math.isinf(self.max_days):
            return self.__full_data[self.__full_data.codice_regione != 0]
        else:
            return self.get_last_days_of_data(self.max_days, self.__full_data[self.__full_data.codice_regione != 0])

    @property
    def dati_completi(self) -> pd.DataFrame:
        if self.__full_data is None:
            self.__init_full_data()
        if math.isinf(self.max_days):
            return self.__full_data
        else:
            return self.get_last_days_of_data(self.max_days, self.__full_data)

    @property
    def dati_provinciali(self) -> pd.DataFrame:
        if self.__dati_provinciali is None:
            self.__init_province()
        if math.isinf(self.max_days):
            return self.__dati_provinciali
        else:
            return self.get_last_days_of_data(self.max_days, self.__dati_provinciali)

    @property
    def dati_nazionali_latest(self) -> pd.DataFrame:
        old_max_days = self.max_days
        self.max_days = 1
        data = self.dati_nazionali
        self.max_days = old_max_days
        return data

    @property
    def dati_regionali_latest(self) -> pd.DataFrame:
        old_max_days = self.max_days
        self.max_days = 1
        data = self.dati_regionali
        self.max_days = old_max_days
        return data

    @property
    def dati_completi_latest(self) -> pd.DataFrame:
        old_max_days = self.max_days
        self.max_days = 1
        data = self.dati_completi
        self.max_days = old_max_days
        return data

    @property
    def dati_provinciali_latest(self) -> pd.DataFrame:
        old_max_days = self.max_days
        self.max_days = 1
        data = self.dati_provinciali
        self.max_days = old_max_days
        return data

    def get_last_days_of_data(self, max_days:int, data:pd.DataFrame) -> pd.DataFrame:
        d = datetime.today() - timedelta(days=max_days)
        return data[data['date'] > d]

    @property
    def latest_update_date(self) -> datetime:
        data_naz = pd.read_csv(self.__nazionale_latest)
        return pd.to_datetime(data_naz.data).max()
