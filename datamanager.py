import pandas as pd
import numpy as np


class DataManager:

    @staticmethod
    def nazionale_data(file_nazionale):
        data_naz = pd.read_csv(file_nazionale)
        DataManager.__parse_data_as_dataframe(data_naz)
        return data_naz

    @staticmethod
    def regioni_data(file_regioni, head_region=0, must_region=None):
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

        return data_reg, codici_regione

    @staticmethod
    def province_data2(file_province):
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
                today_increment_contagi = row['totale_casi'] - prev_day_contagi
                data_prov['incrementi'].loc[i] = today_increment_contagi
                data_prov['incrementi_percentuali'].loc[
                    i] = 0 if prev_day_contagi == 0 else today_increment_contagi / prev_day_contagi
                prev_day_contagi = row['totale_casi']
        pd.reset_option('mode.chained_assignment')
        return data_prov

    @staticmethod
    def province_data(file_province, target_region=15, use_increments=False):
        data_prov = pd.read_csv(file_province)
        data_prov_in_reg = data_prov[data_prov.codice_regione.eq(target_region)]

        idx = data_prov_in_reg.groupby(['codice_provincia'])['totale_casi'].transform(max) == data_prov_in_reg[
            'totale_casi']

        codici_province = data_prov_in_reg[idx].sort_values(by="totale_casi", ascending=False)[
            "codice_provincia"].to_numpy()
        return_data = {}

        for prov in codici_province:
            data = data_prov_in_reg[data_prov_in_reg["codice_provincia"] == prov]
            giorni = np.array(list(xi[:10] for xi in data['data']))
            contagiati = data['totale_casi']

            template = contagiati.copy()
            template.values[:] = 0

            (increments, increments_percentage, _, _) = DataManager.__compute_increments(
                contagiati, template=template) if use_increments else (
                template.astype("int64", copy=True), template.astype("float64", copy=True), None, None)

            return_data[prov] = {
                "regione": data.denominazione_regione.unique()[0],
                "denominazione": data.denominazione_provincia.unique()[0],
                "giorni": giorni,
                "totale_casi": contagiati,
                "incrementi": increments,
                "incrementi_percentuali": increments_percentage
            }

        return return_data

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
            for i, row in values.iterrows():
                today_increment_contagi = row['totale_casi'] - prev_day_contagi
                today_increment_tamponi = row['tamponi'] - prev_day_tamponi
                data['incrementi'].loc[i] = today_increment_contagi
                data['incrementi_percentuali'].loc[
                    i] = 0 if prev_day_contagi == 0 else today_increment_contagi / prev_day_contagi
                data['incrementi_tamponi'].loc[i] = today_increment_tamponi
                data['incrementi_tamponi_percentuali'].loc[
                    i] = 0 if prev_day_tamponi == 0 else today_increment_tamponi / prev_day_tamponi
                prev_day_contagi = row['totale_casi']
                prev_day_tamponi = row['tamponi']
        pd.reset_option('mode.chained_assignment')
