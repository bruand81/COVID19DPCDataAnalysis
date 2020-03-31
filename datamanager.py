import pandas as pd
import numpy as np

class DataManager:
    # @staticmethod
    # def nazionale_data(file_nazionale, use_increments=False):
    #     data_naz = pd.read_csv(file_nazionale)
    #     return DataManager.__parse_data(data_naz, denominazione="Italia", use_increments=use_increments)

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
        #     codici_regione = data_reg[idx].sort_values(by="totale_casi", ascending=False).head(head_region)[
        #         "codice_regione"].to_numpy()
        else:
            codici_regione = idx[head_region:]
        #     codici_regione = data_reg[idx].sort_values(by="totale_casi", ascending=False).tail(abs(head_region))[
        #         "codice_regione"].to_numpy()

        if must_region is not None and len(must_region) > 0:
            must_region_add = [x for x in must_region if x not in codici_regione]
            codici_regione = np.concatenate((codici_regione, must_region_add))
            # codici_regione = np.unique(np.concatenate((codici_regione, must_region)))

        DataManager.__parse_data_as_dataframe(data_reg)

        return data_reg, codici_regione

    # @staticmethod
    # def regioni_data(file_regioni, head_region=0, must_region=None, use_increments=False):
    #     data_reg = pd.read_csv(file_regioni)
    #     # idx = data_reg.groupby(['codice_regione'])['totale_casi'].transform(max) == data_reg['totale_casi']
    #     idx = data_reg.sort_values(by="totale_casi", ascending=False).codice_regione.unique()
    #
    #     if head_region == 0:
    #         head_region = len(idx)
    #
    #     if head_region > 0:
    #         codici_regione = idx[:head_region]
    #     #     codici_regione = data_reg[idx].sort_values(by="totale_casi", ascending=False).head(head_region)[
    #     #         "codice_regione"].to_numpy()
    #     else:
    #         codici_regione = idx[head_region:]
    #     #     codici_regione = data_reg[idx].sort_values(by="totale_casi", ascending=False).tail(abs(head_region))[
    #     #         "codice_regione"].to_numpy()
    #
    #     if must_region is not None and len(must_region) > 0:
    #         must_region_add = [x for x in must_region if x not in codici_regione]
    #         codici_regione = np.concatenate((codici_regione, must_region_add))
    #         # codici_regione = np.unique(np.concatenate((codici_regione, must_region)))
    #     return_data = {}
    #
    #     for reg in codici_regione:
    #         data = data_reg[data_reg["codice_regione"] == reg]
    #         denominazione = ", ".join(data.denominazione_regione.unique())
    #         results = DataManager.__parse_data(data, denominazione=denominazione, use_increments=use_increments)
    #         return_data[reg] = results
    #
    #     return return_data, codici_regione

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
    def __parse_data(data, denominazione, use_increments=False):
        # giorni = pd.Series(np.array(list(xi[:10] for xi in data['data'])))
        giorni = data['data'].str.slice(stop=10)
        contagiati = data['totale_casi']
        deceduti = data['deceduti']
        guariti = data['dimessi_guariti']
        terapia_intensiva = data['terapia_intensiva']
        ricoverati = data['ricoverati_con_sintomi']
        tamponi = data['tamponi']

        template = contagiati.copy()
        template.values[:] = 0
        (increments, increments_percentage, increments_tamponi,
         increments_tamponi_percentage) = DataManager.__compute_increments(contagiati=contagiati, tamponi=tamponi,
                                                                           template=template.astype("int64",
                                                                                                    copy=True)) \
            if use_increments else (
            template.astype("int64", copy=True), template.astype("float64", copy=True),
            template.astype("int64", copy=True),
            template.astype("float64", copy=True))

        return {
            "denominazione": pd.Series(np.repeat(denominazione, len(contagiati))),
            "giorni": giorni,
            "totale_casi": contagiati,
            "deceduti": deceduti,
            "dimessi_guariti": guariti,
            "terapia_intensiva": terapia_intensiva,
            "ricoverati_con_sintomi": ricoverati,
            "tamponi": tamponi,
            "incrementi": increments,
            "incrementi_percentuali": increments_percentage,
            "incrementi_tamponi": increments_tamponi,
            "incrementi_tamponi_percentuali": increments_tamponi_percentage
        }

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
        pd.set_option('mode.chained_assignment', 'raise')

    @staticmethod
    def __increments_calculation(data, source, destination, destination_percentage):
        prev_day = 0
        for i, row in data.iterrows():
            today_increment = row[source] - prev_day
            data[destination].loc[i] = today_increment
            data[destination_percentage].loc[i] = 0 if prev_day == 0 else today_increment / prev_day
            prev_day = row[source]

    @staticmethod
    def __compute_increments(contagiati, template, tamponi=None):
        (increments, increments_percentage) = DataManager.__increments_from_data(contagiati, use_template=template)
        (increments_tamponi, increments_tamponi_percentage) = DataManager.__increments_from_data(
            tamponi, use_template=template)
        return increments, increments_percentage, increments_tamponi, increments_tamponi_percentage

    @staticmethod
    def __increments_from_data(data, use_template):
        template = use_template if data is None else data
        increments = template.astype("int64", copy=True)
        increments_percentage = template.astype("float64", copy=True)
        if data is not None:
            prev_day = 0
            idx = 0
            for idx, cases in data.items():
                today_increment = cases - prev_day
                increments.loc[idx] = today_increment
                increments_percentage.loc[idx] = 0 if prev_day == 0 else today_increment / prev_day
                prev_day = cases
                # idx = idx + 1

        return increments, increments_percentage