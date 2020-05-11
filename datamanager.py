import pandas as pd
import numpy as np


class DataManager:
    @staticmethod
    def get_last_n_days_of_data(data, max_days=0):
        valid_days = data.giorni.unique()[-1 * max_days:]
        return data[data.giorni.isin(valid_days)]

    @staticmethod
    def nazionale_data(file_nazionale, max_days=0):
        data_naz = pd.read_csv(file_nazionale)
        DataManager.__parse_data_as_dataframe(data_naz)
        return DataManager.get_last_n_days_of_data(data=data_naz, max_days=max_days)

    @staticmethod
    def regioni_data(file_regioni, head_region=0, must_region=None, max_days=0):
        data_reg = pd.read_csv(file_regioni)
        idx = data_reg.sort_values(by="totale_casi", ascending=False).codice_regione.unique()

        if head_region == 0:
            head_region = len(idx)

        if head_region > 0:
            codici_regione = idx[:head_region]
        else:
            codici_regione = idx[head_region:]

        if must_region is not None and len(must_region) > 0:
            must_region_add = [x for x in must_region if x not in codici_regione]
            codici_regione = np.concatenate((codici_regione, must_region_add))

        DataManager.__parse_data_as_dataframe(data_reg)

        return DataManager.get_last_n_days_of_data(data=data_reg, max_days=max_days), codici_regione

    @staticmethod
    def province_data(file_province, max_days=0):
        data_prov = pd.read_csv(file_province)
        data_prov['denominazione'] = data_prov['denominazione_provincia']
        data_prov['giorni'] = data_prov['data'].str.slice(stop=10)
        data_prov['incrementi'] = 0
        data_prov['incrementi_percentuali'] = 0.0

        idx = data_prov.sort_values(by="totale_casi", ascending=False).codice_provincia.unique()
        pd.set_option('mode.chained_assignment', None)
        for prov in idx:
            values = data_prov[data_prov["codice_provincia"] == prov]
            prev_day_contagi = 0
            for i, row in values.iterrows():
                try:
                    today_increment_contagi = row['totale_casi'] - prev_day_contagi
                    data_prov['incrementi'].loc[i] = today_increment_contagi
                    data_prov['incrementi_percentuali'].loc[
                        i] = 0 if prev_day_contagi == 0 else today_increment_contagi / prev_day_contagi
                    prev_day_contagi = row['totale_casi']
                except:
                    data_prov.drop([i])
                    continue
        pd.reset_option('mode.chained_assignment')
        return DataManager.get_last_n_days_of_data(data=data_prov, max_days=max_days)

    @staticmethod
    def get_all_region(file_regioni):
        data_reg = pd.read_csv(file_regioni)

        codici_regione = np.unique(data_reg.codice_regione.to_numpy())

        return [codici_regione, data_reg]

    @staticmethod
    def get_last_update(file_latest):
        data = pd.read_csv(file_latest)
        return data.data[0][:10].replace("-", "")

    @staticmethod
    def __parse_data_as_dataframe(data):
        data['giorni'] = data['data'].str.slice(stop=10)
        data['incrementi'] = 0
        data['incrementi_percentuali'] = 0.0
        data['incrementi_tamponi'] = 0
        data['incrementi_tamponi_percentuali'] = 0.0
        data['incrementi_ti'] = 0
        data['incrementi_ti_percentuali'] = 0.0
        data['incrementi_ricoverati'] = 0
        data['incrementi_ricoverati_percentuali'] = 0.0
        data['incrementi_deceduti'] = 0
        data['incrementi_deceduti_percentuali'] = 0.0
        data['denominazione'] = ''

        if 'codice_regione' in data.columns:
            # print('parsing regione')
            data['denominazione'] = data['denominazione_regione']
            # DataManager.__parse_sub_dataframe(values)
        else:
            data['denominazione'] = "Italia"
            data['codice_regione'] = 0
            # DataManager.__parse_sub_dataframe(data)

        idx = data.sort_values(by="totale_casi", ascending=False).codice_regione.unique()
        pd.set_option('mode.chained_assignment', None)
        for reg in idx:
            values = data[data['codice_regione'] == reg]
            prev_day_contagi = 0
            prev_day_tamponi = 0
            prev_day_ti = 0
            prev_day_ricoverati = 0
            prev_day_deceduti = 0
            for i, row in values.iterrows():
                today_increment_contagi = row['totale_casi'] - prev_day_contagi
                today_increment_tamponi = row['tamponi'] - prev_day_tamponi
                today_increment_ti = row['terapia_intensiva'] - prev_day_ti
                today_increment_ricoverati = row['ricoverati_con_sintomi'] - prev_day_ricoverati
                today_increment_deceduti = row['deceduti'] - prev_day_deceduti
                data['incrementi'].loc[i] = today_increment_contagi
                data['incrementi_percentuali'].loc[
                    i] = 0 if prev_day_contagi == 0 else today_increment_contagi / prev_day_contagi
                data['incrementi_tamponi'].loc[i] = today_increment_tamponi
                data['incrementi_tamponi_percentuali'].loc[
                    i] = 0 if prev_day_tamponi == 0 else today_increment_tamponi / prev_day_tamponi
                data['incrementi_ti'].loc[i] = today_increment_ti
                data['incrementi_ti_percentuali'].loc[
                    i] = 0 if prev_day_ti == 0 else today_increment_ti / prev_day_ti
                data['incrementi_ricoverati'].loc[i] = today_increment_ricoverati
                data['incrementi_ricoverati_percentuali'].loc[
                    i] = 0 if prev_day_ricoverati == 0 else today_increment_ricoverati / prev_day_ricoverati
                data['incrementi_deceduti'].loc[i] = today_increment_deceduti
                data['incrementi_deceduti_percentuali'].loc[
                    i] = 0 if prev_day_deceduti == 0 else today_increment_deceduti / prev_day_deceduti
                prev_day_contagi = row['totale_casi']
                prev_day_tamponi = row['tamponi']
                prev_day_ti = row['terapia_intensiva']
                prev_day_ricoverati = row['ricoverati_con_sintomi']
                prev_day_deceduti = row['deceduti']
        pd.reset_option('mode.chained_assignment')
