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
    __istat_pcm_link_file = '/Users/bruand/PycharmProjects/COVID19DPCDataAnalysis/files/link_pcm_istat.csv'
    __istat_file = '/Users/bruand/PycharmProjects/COVID19DPCDataAnalysis/files/DCIS_POPRES1_08102020132111719.csv'
    __istat = pd.DataFrame()
    __variation_columns = ['tamponi', 'casi_testati', 'terapia_intensiva', 'ricoverati_con_sintomi', 'deceduti',
                           'dimessi_guariti', 'isolamento_domiciliare', 'casi_da_screening',
                           'casi_da_sospetto_diagnostico']
    __variation_columns_province = ['totale_casi']
    __renamed_columns = {x: f'variazione_{x}' for x in __variation_columns}
    __percentage_renamed_columns = {x: f'percentuale_variazione_{x}' for x in __variation_columns}
    __renamed_columns_province = {x: f'variazione_{x}' for x in __variation_columns_province}
    __percentage_renamed_columns_province = {x: f'percentuale_variazione_{x}' for x in __variation_columns_province}
    __full_data: pd.DataFrame = None
    __dati_provinciali = None
    max_days = np.inf

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
        self.__full_data = self.__full_data.merge(self.popolazione_istat[['codice_regione', 'popolazione']],
                                                  how='inner', on='codice_regione')
        self.__full_data['incidenza'] = (self.__full_data['totale_casi'] / (self.__full_data['popolazione'] / 100000)).round(decimals=0).astype('int')

        regions = self.__full_data.codice_regione.unique()

        nuovi_positivi_7dsum = pd.Series([])
        nuovi_positivi_7dma = pd.Series([])
        nuovi_positivi_3dma = pd.Series([])
        increments = pd.Series([])
        increments_percentage = pd.Series([])
        increments_7dma = pd.Series(name='nuovi_positivi_7dma')
        increments_3dma = pd.Series(name='nuovi_positivi_7dma')

        for region in regions:
            selected_rows = self.__full_data.codice_regione == region
            tmp = self.__full_data[selected_rows][self.__variation_columns].diff()
            is_NaN = tmp.isnull()
            row_has_NaN = is_NaN.any(axis=1)
            rows_cleaned = self.__full_data[selected_rows][row_has_NaN]
            tmp[row_has_NaN] = rows_cleaned[self.__variation_columns]
            increments = pd.concat([increments, tmp], axis=0)
            increments_percentage = pd.concat([increments_percentage, tmp.pct_change(fill_method='ffill')], axis=0)
            increments_7dma = pd.concat([increments_7dma, tmp.rolling(window=7).mean()], axis=0)
            increments_3dma = pd.concat([increments_3dma, tmp.rolling(window=3).mean()], axis=0)
            nuovi_positivi_7dma = nuovi_positivi_7dma.append(self.__full_data[selected_rows].nuovi_positivi.
                                                             rolling(window=7).mean())
            nuovi_positivi_3dma = nuovi_positivi_3dma.append(self.__full_data[selected_rows].nuovi_positivi.
                                                             rolling(window=3).mean())
            nuovi_positivi_7dsum = nuovi_positivi_7dsum.append(self.__full_data[selected_rows].nuovi_positivi.
                                                               rolling(window=7).sum())

        increments.columns = ['variazione_' + str(col) for col in increments.columns]
        increments_percentage.columns = ['percentuale_variazione_' + str(col) for col in increments_percentage.columns]
        increments_3dma.columns = ['variazione_' + str(col) + '_3dma' for col in increments_3dma.columns]
        increments_7dma.columns = ['variazione_' + str(col) + '_7dma' for col in increments_7dma.columns]
        nuovi_positivi_7dma.fillna(0, inplace=True)
        nuovi_positivi_3dma.fillna(0, inplace=True)
        nuovi_positivi_7dsum.fillna(0, inplace=True)
        full_data = pd.concat([self.__full_data, increments, increments_percentage, increments_3dma, increments_7dma],
                              axis=1)

        self.__full_data = full_data
        self.__full_data['incidenza_7d'] = (nuovi_positivi_7dsum / (self.__full_data['popolazione'] / 100000)).round(
            decimals=2)
        self.__full_data['nuovi_positivi_7dma'] = nuovi_positivi_7dma.astype('int')
        self.__full_data['nuovi_positivi_3dma'] = nuovi_positivi_3dma.astype('int')

        self.__full_data['percentuale_positivi_tamponi'] = self.__full_data['totale_positivi'].divide(
            self.__full_data['tamponi'])
        self.__full_data['percentuale_positivi_tamponi_giornaliera'] = self.__full_data['nuovi_positivi'].divide(
            self.__full_data['variazione_tamponi'])
        self.__full_data['percentuale_positivi_casi'] = self.__full_data['totale_positivi'].divide(
            self.__full_data['casi_testati'])
        self.__full_data['percentuale_positivi_casi_giornaliera'] = self.__full_data['nuovi_positivi'].divide(
            self.__full_data['variazione_casi_testati'])
        self.__full_data['CFR'] = self.__full_data['deceduti'].divide(
            self.__full_data['totale_casi'])

        self.__full_data.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.__full_data.fillna(0, inplace=True)

        self.__full_data['date'] = pd.to_datetime(self.__full_data['data'])
        self.__full_data['formatted_date'] = self.__full_data.date.dt.strftime('%d/%m/%Y')
        self.__full_data['CFR_str'] = self.__full_data['CFR'].apply(lambda x: f'{x:.2%}')

    def __init_province(self):
        print('Processamento dati riepilogativi provinciali')
        self.__dati_provinciali = pd.read_csv(self.__province)
        self.__dati_provinciali.fillna(0, inplace=True)
        self.__dati_provinciali = self.__dati_provinciali.merge(
            self.popolazione_istat[['codice_provincia', 'popolazione']], how='inner', on='codice_provincia')
        self.__dati_provinciali['incidenza'] = (self.__dati_provinciali['totale_casi'] / (
                    self.__dati_provinciali['popolazione'] / 100000)).round(decimals=0).astype('int')

        counties = self.__dati_provinciali.codice_provincia.unique()

        increments = pd.Series([])
        increments_percentage = pd.Series([])
        increments_7dma = pd.Series([])
        increments_3dma = pd.Series([])
        nuovi_positivi_7dsum = pd.Series([])

        for county in counties:
            selected_rows = self.__dati_provinciali.codice_provincia == county
            tmp = self.__dati_provinciali[selected_rows][self.__variation_columns_province].diff()
            is_NaN = tmp.isnull()
            row_has_NaN = is_NaN.any(axis=1)
            rows_cleaned = self.__dati_provinciali[selected_rows][row_has_NaN]
            tmp[row_has_NaN] = rows_cleaned[self.__variation_columns_province]
            increments = pd.concat([increments, tmp], axis=0)
            increments_percentage = pd.concat([increments_percentage, tmp.pct_change(fill_method='ffill')], axis=0)
            increments_7dma = pd.concat([increments_7dma, tmp.rolling(window=7).mean()], axis=0)
            increments_3dma = pd.concat([increments_3dma, tmp.rolling(window=3).mean()], axis=0)
            nuovi_positivi_7dsum = nuovi_positivi_7dsum.append(tmp.totale_casi.rolling(window=7).sum())

        # increments = increments.drop(columns=increments.columns[0])
        # increments_percentage = increments.drop(columns=increments.columns[0])
        # increments_3dma = increments.drop(columns=increments.columns[0])
        # increments_7dma = increments.drop(columns=increments.columns[0])
        increments.columns = ['variazione_' + str(col) for col in increments.columns]
        increments_percentage.columns = ['percentuale_variazione_' + str(col) for col in increments_percentage.columns]
        increments_3dma.columns = ['variazione_' + str(col) + '_3dma' for col in increments_3dma.columns]
        increments_7dma.columns = ['variazione_' + str(col) + '_7dma' for col in increments_7dma.columns]

        self.__dati_provinciali = pd.concat(
            [self.__dati_provinciali, increments, increments_percentage, increments_3dma, increments_7dma], axis=1)
        incidenza_7d = nuovi_positivi_7dsum.div((self.__dati_provinciali['popolazione'] / 100000))
        incidenza_7d.replace([np.inf, -np.inf], np.nan, inplace=True)
        incidenza_7d.fillna(0, inplace=True)
        incidenza_7d = incidenza_7d.round(decimals=2)
        self.__dati_provinciali['incidenza_7d'] = incidenza_7d
        self.__dati_provinciali.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.__dati_provinciali.fillna(0, inplace=True)
        self.__dati_provinciali['date'] = pd.to_datetime(self.__dati_provinciali['data'])
        self.__dati_provinciali['formatted_date'] = self.__dati_provinciali.date.dt.strftime('%d/%m/%Y')

    @property
    def popolazione_istat(self) -> pd.DataFrame:
        if self.__istat.empty:
            istat = pd.read_csv(self.__istat_file)
            istat_pcm_link = pd.read_csv(self.__istat_pcm_link_file)
            istat = istat.merge(istat_pcm_link, how='inner', on='ITTER107')
            istat = istat[["codice_regione", "codice_provincia", "Value"]]
            self.__istat = istat.rename(columns={"Value": "popolazione"})
        return self.__istat

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

    def get_last_days_of_data(self, max_days: int, data: pd.DataFrame) -> pd.DataFrame:
        d = datetime.today() - timedelta(days=max_days)
        return data[data['date'] > d]

    @property
    def latest_update_date(self) -> datetime:
        data_naz = pd.read_csv(self.__nazionale_latest)
        return pd.to_datetime(data_naz.data).max()

    def dati_province_in_regione(self, codice_regione: int) -> pd.DataFrame:
        return self.dati_provinciali[self.dati_provinciali.codice_regione == codice_regione]

    def dati_province_in_regione_latest(self, codice_regione: int) -> pd.DataFrame:
        return self.dati_provinciali_latest[self.dati_provinciali_latest.codice_regione == codice_regione]
