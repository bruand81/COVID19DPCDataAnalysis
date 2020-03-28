import pandas
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import unicodedata
import string
from git import Repo
from git import RemoteProgress
storeGraph = False
showGraph = False
timestr = ''
current_ref = ''
force_graph_generation = True


class DataManager:
    @staticmethod
    def nazionale_data(file_nazionale, use_increments=False):
        data_naz = pandas.read_csv(file_nazionale)
        return DataManager.__parse_data(data_naz, use_increments=use_increments)

    @staticmethod
    def regioni_data(file_regioni, head_region, must_region, use_increments=False):
        data_reg = pandas.read_csv(file_regioni)
        idx = data_reg.groupby(['codice_regione'])['totale_casi'].transform(max) == data_reg['totale_casi']

        if head_region == 0:
            head_region = len(data_reg.groupby(['codice_regione'])['codice_regione'])

        if head_region > 0:
            codici_regione = data_reg[idx].sort_values(by="totale_casi", ascending=False).head(head_region)[
                "codice_regione"].to_numpy()
        else:
            codici_regione = data_reg[idx].sort_values(by="totale_casi", ascending=False).tail(abs(head_region))[
                "codice_regione"].to_numpy()

        if must_region is not None and len(must_region) > 0:
            codici_regione = np.unique(np.concatenate((codici_regione, must_region)))
        return_data = {}

        for reg in codici_regione:
            data = data_reg[data_reg["codice_regione"] == reg]
            denominazione = ",".join(data.denominazione_regione.unique())
            results = DataManager.__parse_data(data, use_increments=use_increments)
            results["denominazione"] = denominazione
            return_data[reg] = results

        return return_data

    @staticmethod
    def province_data(file_province, target_region=15, use_increments=False):
        data_prov = pandas.read_csv(file_province)
        data_prov_in_reg = data_prov[data_prov.codice_regione.eq(target_region)]

        idx = data_prov_in_reg.groupby(['codice_provincia'])['totale_casi'].transform(max) == data_prov_in_reg[
            'totale_casi']

        codici_province = data_prov_in_reg[idx].sort_values(by="totale_casi", ascending=False)[
            "codice_provincia"].to_numpy()
        return_data = {}

        for prov in codici_province:
            data = data_prov_in_reg[data_prov_in_reg["codice_provincia"] == prov]
            X = np.array(list(xi[:10] for xi in data['data']))
            Contagiati = data['totale_casi']

            (increments, increments_percentage, _, _) = DataManager.__compute_increments(
                Contagiati) if use_increments else (
                None, None, None, None)

            return_data[prov] = {
                "regione": data.denominazione_regione.unique()[0],
                "denominazione": data.denominazione_provincia.unique()[0],
                "giorni": X,
                "totale_casi": Contagiati,
                "incrementi": increments,
                "incrementi_percentuali": increments_percentage
            }

        return return_data

    @staticmethod
    def get_all_region(file_regioni):
        data_reg = pandas.read_csv(file_regioni)

        codici_regione = np.unique(data_reg.codice_regione.to_numpy())

        return [codici_regione, data_reg]

    @staticmethod
    def get_last_update(file_latest):
        data = pandas.read_csv(file_latest)
        return data.data[0][:10].replace("-", "")

    @staticmethod
    def __parse_data(data, use_increments=False):
        giorni = np.array(list(xi[:10] for xi in data['data']))
        contagiati = data['totale_casi']
        deceduti = data['deceduti']
        guariti = data['dimessi_guariti']
        terapia_intensiva = data['terapia_intensiva']
        ricoverati = data['ricoverati_con_sintomi']
        tamponi = data['tamponi']

        (increments, increments_percentage, increments_tamponi,
         increments_tamponi_percentage) = DataManager.__compute_increments(contagiati=contagiati,
                                                                           tamponi=tamponi) if use_increments else (
            None, None, None, None)

        return {
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
    def __compute_increments(contagiati, tamponi=None):
        (increments, increments_percentage) = DataManager.__increments_from_data(contagiati)
        (increments_tamponi, increments_tamponi_percentage) = DataManager.__increments_from_data(
            tamponi) if tamponi is not None else (None, None)
        return increments, increments_percentage, increments_tamponi, increments_tamponi_percentage

    @staticmethod
    def __increments_from_data(data):
        increments = pandas.Series(np.zeros(len(data), dtype=int))
        increments_percentage = pandas.Series(np.zeros(len(data)))
        prev_day = 0
        idx = 0
        for cases in data:
            today_increment = cases - prev_day
            increments.loc[idx] = today_increment
            increments_percentage.loc[idx] = 0 if prev_day == 0 else today_increment / prev_day
            prev_day = cases
            idx = idx + 1

        return increments, increments_percentage


class RepoManager:
    @staticmethod
    def update_repo(repository_path, base_output_path='.'):
        head_file = Path(f'{base_output_path}/lastrev')
        if head_file.is_file():
            with open(head_file, 'r') as file:
                c_ref = file.read().replace('\n', '')
                file.close()
        else:
            c_ref = None

        repo = Repo(repository_path)
        o = repo.remotes.origin
        for fetch_info in o.pull(progress=MyProgressPrinter()):
            print("Updated %s to %s" % (fetch_info.ref, fetch_info.commit))
            last_rev = f'{fetch_info.commit}'
            if c_ref == last_rev:
                return False
            else:
                print(f'{fetch_info.commit}')
                with open(head_file, 'w+') as file:
                    file.write(last_rev)
                    file.close()
                return True


class Utils:
    __valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    __char_limit = 255

    def clean_filename(self, filename, whitelist=None, replace=' '):
        whitelist = whitelist if whitelist is not None else self.__valid_filename_chars

        # replace spaces
        for r in replace:
            filename = filename.replace(r, '_')

        # keep only valid ascii chars
        cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

        # keep only whitelisted chars
        cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
        if len(cleaned_filename) > self.__char_limit:
            print(
                "Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(
                    self.__char_limit))
        return cleaned_filename[:self.__char_limit]


class AnalisiDati:
    utils_manager = Utils()

    def analisi_nazione(self, file_nazionale, output_base, show=None, store=None):
        print("Generazione grafici nazionali")
        data = DataManager.nazionale_data(file_nazionale, use_increments=True)

        self.__nazionale_linear(data, output_base=output_base, show=show, store=store)
        self.__nazionale_log(data, output_base=output_base, show=show, store=store)
        self.__nazionale_increment(data, output_base=output_base, use_percentage=False, show=show, store=store)
        self.__nazionale_increment(data, output_base=output_base, use_percentage=True, show=show, store=store)
        self.__nazionale_dettaglio(data, output_base=output_base, use_percentage=False, show=show, store=store)

    def analisi_regioni(self, regioni, output_base, head_region=0, must_region=None, use_percentage=True, show=None,
                        store=None):
        print("Generazione grafici regionali")
        must_region = must_region if must_region is not None else [15]
        data = DataManager.regioni_data(regioni, head_region=head_region, must_region=must_region, use_increments=True)

        self.__regioni_linear(data, output_base_reg=output_base, head_region=head_region, must_region=must_region,
                              show=show, store=store)
        self.__regioni_log(data, output_base_reg=output_base, head_region=head_region, must_region=must_region,
                           show=show, store=store)
        self.__regioni_increment(data, output_base_reg=output_base, use_percentage=True, show=show, store=store)
        self.__regioni_increment(data, output_base_reg=output_base, use_percentage=False, show=show, store=store)
        self.__regioni_dettaglio(data, output_base=output_base, use_percentage=False, show=show, store=store)

    def analisi_province(self, file_province, output_base, generate_bars=None, show=None, store=None):
        generate_bars = generate_bars if generate_bars is not None else [3, 15]

        print("Generazione grafici province")
        [codici_regione, data_reg] = DataManager.get_all_region(regioni)
        for reg in codici_regione:
            data = DataManager.province_data(file_province, target_region=reg, use_increments=True)
            idx = data_reg['codice_regione'] == reg
            denominazione = data_reg[idx].denominazione_regione.unique()[0]
            print(f'-> Generazione grafici provinciali per regione {denominazione}')
            self.__province_linear(data, output_base=output_base, show=show, store=store)
            self.__province_log(data, output_base=output_base, show=show, store=store)
            if reg in generate_bars:
                self.__province_increment(data, output_base=output_base, show=show, store=store)
                self.__province_increment(data, output_base=output_base, show=show, store=store)

    def __nazionale_plot(self, data, output_base, type, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        plt.close('all')
        figure = plt.figure(figsize=(16, 10))
        plt.plot(data["giorni"], data["totale_casi"], '-o', label="Totale")
        for x, y in zip(data["giorni"], data["totale_casi"]):
            label = f'{y}'
            plt.annotate(label,  # this is the text
                         (x, y),  # this is the point to label
                         textcoords="offset points",  # how to position the text
                         xytext=(0, 10),  # distance from text to points (x,y)
                         ha='center')  # horizontal alignment can be left, right or center

        plt.plot(data["giorni"], data["deceduti"], '-o', label="Deceduti")

        plt.plot(data["giorni"], data["dimessi_guariti"], '-o', label="Guariti")

        plt.plot(data["giorni"], data["terapia_intensiva"], '-o', label="Terapia Intensiva")

        plt.plot(data["giorni"], data["ricoverati_con_sintomi"], '-o', label="Ricoverati")

        plt.plot(data["giorni"], data["tamponi"], '-o', label="Tamponi")
        for x, y in zip(data["giorni"], data["tamponi"]):
            label = f'{y}'
            plt.annotate(label,  # this is the text
                         (x, y),  # this is the point to label
                         textcoords="offset points",  # how to position the text
                         xytext=(0, 10),  # distance from text to points (x,y)
                         ha='center')  # horizontal alignment can be left, right or center

        analysis_desc = ""
        if type == "log":
            analysis_desc = " logaritmica"

        plt.title(
            f'Analisi{analysis_desc} evoluzione COVID19 in Italia')
        plt.xticks(rotation=90)
        plt.yscale(type)
        plt.legend()
        plt.grid(b=True, which='major', axis='x')
        base_filename = self.utils_manager.clean_filename(f'Italia_{type}_{timestr}')
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()
        plt.close(figure)

    def __nazionale_log(self, data, output_base, show=None, store=None):
        print("-> Generazione grafico evoluzione logaritmica")
        self.__nazionale_plot(data, output_base=output_base, type="log", show=show, store=store)

    def __nazionale_linear(self, data, output_base, show=None, store=None):
        print("-> Generazione grafico evoluzione lineare")
        self.__nazionale_plot(data, output_base=output_base, type="linear", show=show, store=store)

    def __nazionale_increment(self, data, output_base, use_percentage=True, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        perc_text = " percentuale" if use_percentage else ""
        print(f'-> Generazione grafico a barre{perc_text} incrementi')

        incrementi = data['incrementi_percentuali'] if use_percentage else data['incrementi']
        figure = plt.figure(figsize=(16, 10))
        y_pos = np.arange(len(data['giorni']))
        plt.bar(y_pos, incrementi, align='center', alpha=0.5)
        plt.xticks(y_pos, data['giorni'])
        plt.ylabel('Incremento casi giornaliero')
        plt.xlabel('Giorni')
        plt.xticks(rotation=90)
        plt.title(f'Incremento{perc_text} contagi COVID19 in Italia')

        for i in range(len(y_pos)):
            label = "{0:.1%}".format(incrementi[i]) if use_percentage else f'{incrementi[i]}'
            y_off = 0.01 if use_percentage else 0.1
            plt.text(x=y_pos[i] - 0.25, y=incrementi[i] + y_off, s=label, size=6)

        base_filename = self.utils_manager.clean_filename(f'Italia_incrementi{perc_text}_{timestr}')
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()
        plt.close(figure)

    def __nazionale_dettaglio(self, data, output_base, use_percentage=True, show=None, store=None):
        print("-> Generazione dettaglio rapporto contagi-tamponi")
        self.__plot_increment_details(data, denominazione="Italia", output_base=output_base,
                                      use_percentage=use_percentage, show=show, store=store)

    def __regioni_plot(self, data, output_base, type, head_region, must_region, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        plt.close('all')
        figure = plt.figure(figsize=(16, 10))

        denominazioni = []
        for reg, values in data.items():
            X = values['giorni']
            Contagiati = values['totale_casi']
            denominazione = values['denominazione']
            if must_region is not None and reg in must_region:
                denominazioni.append(denominazione)
            plt.plot(X, Contagiati, '-o', label=denominazione + " Totale")

        analysis_desc = ""
        if type == "log":
            analysis_desc = " logaritmica"

        tail_text = ""
        if len(denominazioni) > 0:
            regioni = str(denominazioni).strip('[]')
            tail_text = f' e confronto con {regioni}'

        if head_region == 0:
            region_text = "regioni"
        elif head_region < 0:
            region_text = f'{abs(head_region)} meno colpite'
        else:
            region_text = f'{head_region} più colpite'

        plt.title(f'Analisi{analysis_desc} evoluzione COVID19 nelle {region_text} d\'Italia{tail_text}')
        plt.xticks(rotation=90)
        plt.yscale(type)
        plt.legend()
        plt.grid(b=True, which='major', axis='x')
        base_filename = self.utils_manager.clean_filename(f'Riassunto_regionale_{type}_{timestr}')
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()
        plt.close(figure)

    def __regioni_log(self, data, output_base_reg, head_region=5, must_region=None, show=None, store=None):
        print("-> Generazione grafico evoluzione logaritmica")
        must_region = must_region if must_region is not None else [15]
        self.__regioni_plot(data, output_base=output_base_reg, type="log", head_region=head_region,
                            must_region=must_region, show=show, store=store)

    def __regioni_linear(self, data, output_base_reg, head_region=5, must_region=None, show=None, store=None):
        print("-> Generazione grafico evoluzione lineare")
        must_region = must_region if must_region is not None else [15]
        self.__regioni_plot(data, output_base=output_base_reg, type="linear", head_region=head_region,
                            must_region=must_region, show=show, store=store)

    def __regioni_increment(self, data, output_base_reg, use_percentage=True, show=None, store=None):
        Path(output_base_reg).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        perc_text = " percentuale" if use_percentage else ""

        for reg, values in data.items():
            denominazione = values['denominazione']
            print(f'-> Generazione grafici a barre per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            incrementi = values['incrementi_percentuali'] if use_percentage else values['incrementi']
            y_pos = np.arange(len(values['giorni']))
            plt.bar(y_pos, incrementi, align='center', alpha=0.5)
            plt.xticks(y_pos, values['giorni'])
            plt.ylabel('Incremento casi giornaliero')
            plt.xlabel('Giorni')
            plt.xticks(rotation=90)
            plt.title(f'Incremento{perc_text} contagi COVID19 in {denominazione}')

            for i in range(len(y_pos)):
                label = "{0:.1%}".format(incrementi[i]) if use_percentage else f'{incrementi[i]}'
                y_off = 0.01 if use_percentage else 0.1
                plt.text(x=y_pos[i] - 0.25, y=incrementi[i] + y_off, s=label, size=6)

            base_filename = self.utils_manager.clean_filename(f'{denominazione}_incrementi{perc_text}_{timestr}')
            if store:
                plt.savefig(f'{output_base_reg}{base_filename}.png', bbox_inches='tight')
                plt.savefig(f'{output_base_reg}{base_filename}.pdf', bbox_inches='tight')
            if show:
                plt.show()
            plt.close(figure)

    def __regioni_increment_details(self, data, output_base, use_percentage=True, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        perc_text = " percentuale" if use_percentage else ""

        for reg, values in data.items():
            denominazione = values['denominazione']
            print(f'-> Generazione grafici a barre di dettaglio per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            barWidth = 0.4
            incrementi = values['incrementi_percentuali'] if use_percentage else values['incrementi']
            tamponi = values['incrementi_tamponi_percentuali'] if use_percentage else values['incrementi_tamponi']
            y_pos1 = np.arange(len(values['giorni']))
            y_pos2 = [x + barWidth for x in y_pos1]
            plt.bar(y_pos1, incrementi, align='center', alpha=0.5, width=barWidth, label="Incrementi")
            plt.bar(y_pos2, tamponi, align='center', alpha=0.5, width=barWidth, label="Tamponi")
            plt.xticks(y_pos1 + (barWidth / 2), values['giorni'])
            plt.ylabel('Incremento casi giornaliero')
            plt.xlabel('Giorni')
            plt.xticks(rotation=90)
            plt.title(f'Incremento{perc_text} tamponi e contagiati COVID19 in {denominazione}')
            plt.legend()

            for i in range(len(y_pos1)):
                label1 = "{0:.1%}".format(incrementi[i]) if use_percentage else f'{incrementi[i]}'
                label2 = "{0:.1%}".format(tamponi[i]) if use_percentage else f'{tamponi[i]}'
                y_off = 0.01 if use_percentage else 0.1
                plt.text(x=y_pos1[i] - 0.25, y=incrementi[i] + y_off, s=label1, size=6)
                plt.text(x=y_pos2[i] - 0.25, y=tamponi[i] + y_off, s=label2, size=6)

            base_filename = self.utils_manager.clean_filename(f'{denominazione}_dettagli{perc_text}_{timestr}')
            if store:
                plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
                plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
            if show:
                plt.show()
            plt.close(figure)

    def __regioni_dettaglio(self, data, output_base, use_percentage=True, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        for reg, values in data.items():
            denominazione = values['denominazione']
            self.__plot_increment_details(values, denominazione=denominazione, output_base=output_base,
                                          use_percentage=False, show=show, store=store)

    def __regione_plot_details(self, data, output_base, type, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        for reg, values in data.items():
            denominazione = values['denominazione']
            print(f'-> Generazione dettagli {type} per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            plt.plot(values["giorni"], values["totale_casi"], '-o', label="Totale")
            for x, y in zip(values["giorni"], values["totale_casi"]):
                label = f'{y}'
                plt.annotate(label,  # this is the text
                             (x, y),  # this is the point to label
                             textcoords="offset points",  # how to position the text
                             xytext=(0, 10),  # distance from text to points (x,y)
                             ha='center')  # horizontal alignment can be left, right or center

            plt.plot(values["giorni"], values["deceduti"], '-o', label="Deceduti")

            plt.plot(values["giorni"], values["dimessi_guariti"], '-o', label="Guariti")

            plt.plot(values["giorni"], values["terapia_intensiva"], '-o', label="Terapia Intensiva")

            plt.plot(values["giorni"], values["ricoverati_con_sintomi"], '-o', label="Ricoverati")

            plt.plot(values["giorni"], values["tamponi"], '-o', label="Tamponi")
            for x, y in zip(values["giorni"], values["tamponi"]):
                label = f'{y}'
                plt.annotate(label,  # this is the text
                             (x, y),  # this is the point to label
                             textcoords="offset points",  # how to position the text
                             xytext=(0, 10),  # distance from text to points (x,y)
                             ha='center',
                             clip_on=True)  # horizontal alignment can be left, right or center

            analysis_desc = ""
            if type == "log":
                analysis_desc = " logaritmica"

            plt.title(
                f'Analisi{analysis_desc} evoluzione COVID19 in Italia')
            plt.xticks(rotation=90)
            plt.yscale(type)
            plt.legend()
            plt.grid(b=True, which='major', axis='x')
            base_filename = self.utils_manager.clean_filename(f'{denominazione}_detail_{type}_{timestr}')
            if store:
                plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
                plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
            if show:
                plt.show()
            plt.close(figure)

    def __plot_increment_details(self, data, denominazione, output_base, use_percentage=True, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        perc_text = " percentuale" if use_percentage else ""

        print(f'-> Generazione grafici a barre di dettaglio per {denominazione}')
        plt.close('all')
        figure = plt.figure(figsize=(16, 10))
        giorni = data["giorni"]
        incrementi = data['incrementi_percentuali'] if use_percentage else data['incrementi']
        tamponi = data['incrementi_tamponi_percentuali'] if use_percentage else data['incrementi_tamponi']
        percentali = [x / y if x != 0 and y != 0 else 0 for x, y in zip(incrementi, tamponi)]
        columns = giorni.tolist()
        rows = ["Contagi", "Tamponi", "Percentuale"]

        colors = plt.cm.BuPu(np.linspace(0, 1, len(rows)))

        index = np.arange(len(columns))
        bar_width = 0.8
        format_str = "{:+.1%}" if use_percentage else '{:+d}'

        cell_text = []
        plt.bar(index, incrementi, bar_width, color=colors[0], align="center", label="Contagi", zorder=10)
        cell_text.append([format_str.format(x) for x in incrementi])
        plt.bar(index, tamponi, bar_width, color=colors[1], align="center", label="Tamponi", zorder=0)
        cell_text.append([format_str.format(x) for x in tamponi])
        cell_text.append(["{:+.1%}".format(x) for x in percentali])

        plt.title(f'Incremento{perc_text} tamponi e contagiati COVID19 in {denominazione}')

        plt.xticks(index, columns, rotation=90)
        plt.legend()

        for i in range(len(index)):
            label1 = "{0:.1%}".format(incrementi[i]) if use_percentage else f'{incrementi[i]}'
            label2 = "{0:.1%}".format(tamponi[i]) if use_percentage else f'{tamponi[i]}'
            y_off1 = incrementi[i] / 1000
            y_off2 = tamponi[i] / 1000
            x_off = (bar_width / 2)
            plt.text(x=index[i] - x_off, y=incrementi[i] + y_off1, s=label1, size=6, zorder=20)
            plt.text(x=index[i] - x_off, y=tamponi[i] + y_off2, s=label2, size=6, zorder=20)

        base_filename = self.utils_manager.clean_filename(f'{denominazione}_dettagli{perc_text}_{timestr}')
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()
        plt.close(figure)


    def __province_plot(self, data, output_base, type, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        plt.close('all')
        figure = plt.figure(figsize=(16, 10))

        regione = ""

        for prov, values in data.items():
            X = values['giorni']
            contagiati = values['totale_casi']
            denominazione = values['denominazione']
            regione = values['regione']
            plt.plot(X, contagiati, '-o', label=denominazione + " Totale")

        analysis_desc = ""
        if type == "log":
            analysis_desc = " logaritmica"
        plt.title(f'Analisi{analysis_desc} evoluzione COVID19 nelle province della {regione}')
        plt.xticks(rotation=90)
        plt.yscale(type)
        plt.legend()
        plt.grid(b=True, which='major', axis='x')
        base_filename = self.utils_manager.clean_filename(f'province_{regione}_{type}_{timestr}')
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()
        plt.close(figure)

    def __province_log(self, data, output_base, show=None, store=None):
        self.__province_plot(data, output_base=output_base, type="log", show=show, store=store)

    def __province_linear(self, data, output_base, show=None, store=None):
        self.__province_plot(data, output_base=output_base, type="linear", show=show, store=store)

    def __province_increment(self, data, output_base, use_percentage=True, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = storeGraph if store is None else store
        show = showGraph if show is None else store

        plt.close('all')

        for prov, values in data.items():
            denominazione = values['denominazione']
            regione = values['regione']
            print(f'--> Generazione grafici a barre per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            incrementi = values['incrementi_percentuali'] if use_percentage else values['incrementi']
            y_pos = np.arange(len(values['giorni']))
            plt.bar(y_pos, incrementi, align='center', alpha=0.5)
            plt.xticks(y_pos, values['giorni'])
            plt.ylabel('Incremento casi giornaliero')
            plt.xlabel('Giorni')
            plt.xticks(rotation=90)
            perc_text = " percentuale" if use_percentage else ""
            plt.title(f'Incremento{perc_text} contagi COVID19 in {denominazione}')

            for i in range(len(y_pos)):
                label = "{0:.1%}".format(incrementi[i]) if use_percentage else f'{incrementi[i]}'
                y_off = 0.01 if use_percentage else 0.1
                plt.text(x=y_pos[i] - 0.25, y=incrementi[i] + y_off, s=label, size=6)

            base_filename = self.utils_manager.clean_filename(
                f'{regione}_{denominazione}_incrementi{perc_text}_{timestr}')
            if store:
                plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
                plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
            if show:
                plt.show()
            plt.close(figure)


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")


if __name__ == '__main__':
    repo_path = '/Users/bruand/Documents Local/analisi/COVID-19'
    updated = RepoManager.update_repo(repo_path)
    if force_graph_generation or updated:
        print(f'Repository aggiornato. Rigenerazione grafici in corso')
        latest = f'{repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale-latest.csv'
        nazionale = f'{repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
        regioni = f'{repo_path}/dati-regioni/dpc-covid19-ita-regioni.csv'
        province = f'{repo_path}/dati-province/dpc-covid19-ita-province.csv'

        timestr = DataManager.get_last_update(latest)
        output_base_path = f'output/{timestr}/'
        output_base_path_reg = f'{output_base_path}regionale/'
        output_base_path_prov = f'{output_base_path}provinciale/'
        storeGraph = True
        showGraph = False
        analysis = AnalisiDati()
        analysis.analisi_nazione(nazionale, output_base=output_base_path)
        analysis.analisi_regioni(regioni, output_base=output_base_path_reg, head_region=0, must_region=None,
                                 use_percentage=True)
        analysis.analisi_province(province, output_base=output_base_path_prov, generate_bars=[3, 15])
    else:
        print('Aggiornamento dei grafici non necessario')
