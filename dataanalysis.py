import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datamanager import DataManager
from utils import Utils


class AnalisiDati:
    __utils_manager = Utils()
    __time_str = ''
    __storeGraph = False
    __showGraph = False
    __data_nazionale = None
    __data_regionale = None
    __codici_regione = None
    __data_provinciale = None
    __color_map = "gist_rainbow"
    __max_days= 0

    def __init__(self, file_nazionale, file_regioni, file_province, show=False, store=True, color_map=None,
                 time_str=None, max_days=0):
        self.__showGraph = show
        self.__storeGraph = store
        self.__max_days=max_days
        self.__data_nazionale = DataManager.nazionale_data(file_nazionale, max_days=self.__max_days)
        max_data = self.__data_nazionale.data.max()
        self.__time_str = time_str if time_str is not None else max_data[:10].replace("-", "")
        self.__data_regionale, self.__codici_regione = DataManager.regioni_data(file_regioni, max_days=self.__max_days)
        self.__data_provinciale = DataManager.province_data(file_province, max_days=self.__max_days)
        self.__color_map = self.__color_map if color_map is None else color_map

    @property
    def data_nazionale(self):
        return self.__data_nazionale

    @property
    def data_nazionale_latest(self):
        return self.data_latest(self.__data_nazionale)

    @property
    def data_regionale(self):
        return self.__data_regionale

    @property
    def data_regionale_latest(self):
        return self.data_latest(self.__data_regionale)

    @property
    def data_provinciale(self):
        return self.__data_provinciale

    @property
    def data_provinciale_latest(self):
        return self.data_latest(self.__data_provinciale)

    @property
    def last_update(self):
        return self.__data_nazionale.data.max()

    def data_latest(self, data):
        max_data = self.__data_nazionale.data.max()
        return data[data.data == max_data]

    def tabelle(self, file_nazionale, file_regioni, output_base, show=None, store=None):
        print(f'Generazione tabelle riepilogative al {self.__time_str}')

        if self.__data_nazionale is None:
            self.__data_nazionale = DataManager.nazionale_data(file_nazionale)
        if self.__data_regionale is None:
            self.__data_regionale, self.__codici_regione = DataManager.regioni_data(file_regioni)
        self.__table_rapporto_tamponi_contagi(data_nazionale=self.__data_nazionale,
                                              data_regionale=self.__data_regionale,
                                              output_base=output_base,
                                              show=show,
                                              store=store)

    def analisi_nazione(self, file_nazionale, output_base, show=None, store=None):
        print(f'Generazione grafici nazionali al {self.__time_str}')

        if self.__data_nazionale is None:
            self.__data_nazionale = DataManager.nazionale_data(file_nazionale)

        self.__nazionale_linear(self.__data_nazionale, output_base=output_base, show=show, store=store)
        self.__nazionale_log(self.__data_nazionale, output_base=output_base, show=show, store=store)
        self.__nazionale_increment(self.__data_nazionale, output_base=output_base, use_percentage=False, show=show,
                                   store=store)
        self.__nazionale_increment(self.__data_nazionale, output_base=output_base, use_percentage=True, show=show,
                                   store=store)
        self.__nazionale_dettaglio(self.__data_nazionale, output_base=output_base, use_percentage=False, show=show,
                                   store=store)

    def analisi_regioni(self, file_regioni, output_base, head_region=5, must_region=None,
                        show=None,
                        store=None):
        print(f'Generazione grafici regionali al {self.__time_str}')

        must_region = must_region if must_region is not None else []
        if self.__data_regionale is None:
            self.__data_regionale, self.__codici_regione = DataManager.regioni_data(file_regioni)

        self.__regioni_linear(self.__data_regionale, output_base_reg=output_base, codici_regione=self.__codici_regione,
                              head_region=head_region,
                              must_region=must_region, show=show, store=store)
        self.__regioni_log(self.__data_regionale, output_base_reg=output_base, codici_regione=self.__codici_regione,
                           head_region=head_region,
                           must_region=must_region, show=show, store=store)
        self.__regioni_increment(self.__data_regionale, output_base_reg=output_base, use_percentage=True, show=show,
                                 store=store)
        self.__regioni_increment(self.__data_regionale, output_base_reg=output_base, use_percentage=True, show=show,
                                 store=store)
        self.__regioni_dettaglio(self.__data_regionale, output_base=output_base, use_percentage=False, show=show,
                                 store=store)

    def analisi_province(self, file_province, file_regioni, output_base, generate_bars=None, show=None, store=None):
        print(f'Generazione grafici province al {self.__time_str}')

        if self.__data_regionale is None:
            self.__data_regionale, self.__codici_regione = DataManager.regioni_data(file_regioni)

        if self.__data_provinciale is None:
            self.__data_provinciale = DataManager.province_data(file_province)

        generate_bars = generate_bars if generate_bars is not None else self.__codici_regione
        for reg in self.__codici_regione:
            denominazione = ",".join(
                self.__data_regionale[self.__data_regionale['codice_regione'] == reg].denominazione_regione.unique())
            print(f'-> Generazione grafici provinciali per regione {denominazione} al {self.__time_str}')
            values = self.__data_provinciale[self.__data_provinciale['codice_regione'] == reg]
            self.__province_linear(values, output_base=output_base, show=show, store=store)
            self.__province_log(values, output_base=output_base, show=show, store=store)
            if reg in generate_bars:
                self.__province_increment(values, output_base=output_base, show=show, store=store)

    def __nazionale_plot(self, data, output_base, graph_type, show=None, store=None):
        plt.close('all')
        figure = plt.figure(figsize=(16, 10))
        colors = plt.get_cmap(self.__color_map)(np.linspace(0, 1, 6))

        plt.plot(data["giorni"], data["totale_casi"], '-o', label=f'Totale ({data["totale_casi"].max()})', color=colors[0])
        if graph_type == "linear":
            for x, y in zip(data["giorni"].to_numpy(), data["totale_casi"].to_numpy()):
                label = f'{y}'
                plt.annotate(label,  # this is the text
                             (x, y),  # this is the point to label
                             textcoords="offset points",  # how to position the text
                             xytext=(0, 10),  # distance from text to points (x,y)
                             ha='center')  # horizontal alignment can be left, right or center

        plt.plot(data["giorni"], data["deceduti"], '-o', label=f'Deceduti ({data["deceduti"].max()})', color=colors[1])

        plt.plot(data["giorni"], data["dimessi_guariti"], '-o', label=f'Guariti ({data["dimessi_guariti"].max()})', color=colors[2])

        plt.plot(data["giorni"], data["terapia_intensiva"], '-o',
                 label=f'Terapia Intensiva ({data["terapia_intensiva"].max()})', color=colors[3])

        plt.plot(data["giorni"], data["ricoverati_con_sintomi"], '-o',
                 label=f'Ricoverati ({data["ricoverati_con_sintomi"].max()})', color=colors[4])

        plt.plot(data["giorni"], data["tamponi"], '-o', label=f'Tamponi ({data["tamponi"].max()})', color=colors[5])
        if graph_type == "linear":
            for x, y in zip(data["giorni"].to_numpy(), data["tamponi"].to_numpy()):
                label = f'{y}'
                plt.annotate(label,  # this is the text
                             (x, y),  # this is the point to label
                             textcoords="offset points",  # how to position the text
                             xytext=(0, 10),  # distance from text to points (x,y)
                             ha='center')  # horizontal alignment can be left, right or center

        analysis_desc = " logaritmica" if graph_type == "log" else ""

        plt.title(
            f'Analisi{analysis_desc} evoluzione COVID19 in Italia al {self.__time_str}')
        plt.xticks(rotation=90)
        plt.yscale(graph_type)
        plt.legend()
        plt.grid(b=True, which='major', axis='x')
        base_filename = self.__utils_manager.clean_filename(f'Italia_{graph_type}_{self.__time_str}')
        self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
        plt.close(figure)

    def __nazionale_log(self, data, output_base, show=None, store=None):
        print("-> Generazione grafico evoluzione logaritmica")
        self.__nazionale_plot(data, output_base=output_base, graph_type="log", show=show, store=store)

    def __nazionale_linear(self, data, output_base, show=None, store=None):
        print("-> Generazione grafico evoluzione lineare")
        self.__nazionale_plot(data, output_base=output_base, graph_type="linear", show=show, store=store)

    def __nazionale_increment(self, data, output_base, use_percentage=True, show=None, store=None):
        perc_text = " percentuale" if use_percentage else ""
        print(f'-> Generazione grafico a barre{perc_text} incrementi')

        figure = plt.figure(figsize=(16, 10))
        denominazione = ", ".join(data.denominazione.unique())
        self.__plot_increment(data=data, denominazione=denominazione, use_percentage=use_percentage)

        base_filename = self.__utils_manager.clean_filename(f'Italia_incrementi{perc_text}_{self.__time_str}')
        self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
        plt.close(figure)

    def __nazionale_dettaglio(self, data, output_base, use_percentage=True, show=None, store=None):
        print("-> Generazione dettaglio rapporto contagi-tamponi")
        self.__plot_increment_details(data, denominazione="Italia", output_base=output_base,
                                      use_percentage=use_percentage, show=show, store=store)

    def __regioni_plot(self, data, output_base, graph_type, head_region, must_region, codici_regione, show=None,
                       store=None):
        plt.close('all')
        figure = plt.figure(figsize=(16, 10))

        head_region = len(codici_regione) if head_region < 1 else head_region
        selection = np.unique(np.concatenate((codici_regione[:head_region], must_region)))
        data_selected = {x: data[data["codice_regione"] == x] for x in selection}
        colors = plt.get_cmap(self.__color_map)(np.linspace(0, 1, len(selection)))

        denominazioni = []
        i = 0
        for reg, values in data_selected.items():
            giorni = values['giorni']
            contagiati = values['totale_casi']
            max_casi = contagiati.max()
            denominazione = ", ".join(values['denominazione'].unique())
            if must_region is not None and reg in must_region:
                denominazioni.append(denominazione)
            plt.plot(giorni, contagiati, '-o', label=f'{denominazione}  Totale ({max_casi})', color=colors[i])
            i = i+1

        analysis_desc = " logaritmica" if graph_type == "log" else ""

        tail_text = ""
        if len(denominazioni) > 0:
            regioni = ", ".join(denominazioni)
            tail_text = f' e confronto con {regioni}'

        if head_region == 0:
            region_text = "regioni"
        elif head_region < 0:
            region_text = f'{abs(head_region)} meno colpite'
        else:
            region_text = f'{head_region} più colpite'

        plt.title(f'Analisi{analysis_desc} evoluzione COVID19 nelle {region_text} d\'Italia{tail_text} al {self.__time_str}')
        plt.xticks(rotation=90)
        plt.yscale(graph_type)
        plt.legend()
        plt.grid(b=True, which='major', axis='x')
        base_filename = self.__utils_manager.clean_filename(f'Riassunto_regionale_{graph_type}_{self.__time_str}')
        self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
        plt.close(figure)

    def __regioni_log(self, data, output_base_reg, codici_regione, head_region=5, must_region=None, show=None,
                      store=None):
        print("-> Generazione grafico evoluzione logaritmica")
        must_region = must_region if must_region is not None else [15]
        self.__regioni_plot(data, output_base=output_base_reg, graph_type="log", codici_regione=codici_regione,
                            head_region=head_region,
                            must_region=must_region, show=show, store=store)

    def __regioni_linear(self, data, output_base_reg, codici_regione, head_region=5, must_region=None, show=None,
                         store=None):
        print("-> Generazione grafico evoluzione lineare")
        must_region = must_region if must_region is not None else [15]
        self.__regioni_plot(data, output_base=output_base_reg, graph_type="linear", codici_regione=codici_regione,
                            head_region=head_region,
                            must_region=must_region, show=show, store=store)

    def __plot_increment(self, data, denominazione, use_percentage=True):
        perc_text = " percentuale" if use_percentage else ""
        incrementi = data['incrementi_percentuali'] if use_percentage else data['incrementi']
        y_pos = np.arange(len(data['giorni']))
        colors = plt.get_cmap(self.__color_map)(np.linspace(0, 1, 2))

        plt.bar(y_pos, incrementi, align='center', alpha=0.5, color=colors[0])
        plt.xticks(y_pos, data['giorni'])
        plt.ylabel('Incremento casi giornaliero')
        plt.xlabel('Giorni')
        plt.xticks(rotation=90)
        plt.title(f'Incremento{perc_text} contagi COVID19 in {denominazione} al {self.__time_str}')

        incrementi_array = incrementi.to_numpy()
        for i in range(len(y_pos)):
            label = "{0:.1%}".format(incrementi_array[i]) if use_percentage else f'{incrementi_array[i]}'
            y_off = 0.01 if use_percentage else 0.1
            plt.text(x=y_pos[i] - 0.25, y=incrementi_array[i] + y_off, s=label, size=6)

    def __regioni_increment(self, data, output_base_reg, use_percentage=True, show=None, store=None):
        perc_text = " percentuale" if use_percentage else ""
        idx = data.sort_values(by="totale_casi", ascending=False).codice_regione.unique()

        for reg in idx:
            values = data[data['codice_regione'] == reg]
            denominazione = ", ".join(values['denominazione'].unique())
            print(f'-> Generazione grafici a barre per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            self.__plot_increment(data=values, denominazione=denominazione, use_percentage=use_percentage)

            base_filename = self.__utils_manager.clean_filename(
                f'{denominazione}_incrementi{perc_text}_{self.__time_str}')
            self.__store_and_show(output_base=output_base_reg, base_filename=base_filename, show=show, store=store)
            plt.close(figure)

    def __store_and_show(self,output_base, base_filename, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()

    def __regioni_increment_details(self, data, output_base, use_percentage=True, show=None, store=None):
        perc_text = " percentuale" if use_percentage else ""
        idx = data.sort_values(by="totale_casi", ascending=False).codice_regione.unique()
        colors = plt.get_cmap(self.__color_map)(np.linspace(0, 1, 2))

        for reg in idx:
            values = data[data['codice_regione'] == reg]
            denominazione = ", ".join(values['denominazione'].unique())
            print(f'-> Generazione grafici a barre di dettaglio per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            barWidth = 0.4
            incrementi = values['incrementi_percentuali'] if use_percentage else values['incrementi']
            tamponi = values['incrementi_tamponi_percentuali'] if use_percentage else values['incrementi_tamponi']
            y_pos1 = np.arange(len(values['giorni']))
            y_pos2 = [x + barWidth for x in y_pos1]
            plt.bar(y_pos1, incrementi, align='center', alpha=0.5, width=barWidth, label="Incrementi", color=colors[0])
            plt.bar(y_pos2, tamponi, align='center', alpha=0.5, width=barWidth, label="Tamponi", color=colors[1])
            plt.xticks(y_pos1 + (barWidth / 2), values['giorni'])
            plt.ylabel('Incremento casi giornaliero')
            plt.xlabel('Giorni')
            plt.xticks(rotation=90)
            plt.title(f'Incremento{perc_text} tamponi e contagiati COVID19 in {denominazione} al {self.__time_str}')
            plt.legend()

            for i in range(len(y_pos1)):
                label1 = "{0:.1%}".format(incrementi[i]) if use_percentage else f'{incrementi[i]}'
                label2 = "{0:.1%}".format(tamponi[i]) if use_percentage else f'{tamponi[i]}'
                y_off = 0.01 if use_percentage else 0.1
                plt.text(x=y_pos1[i] - 0.25, y=incrementi[i] + y_off, s=label1, size=6)
                plt.text(x=y_pos2[i] - 0.25, y=tamponi[i] + y_off, s=label2, size=6)

            base_filename = self.__utils_manager.clean_filename(
                f'{denominazione}_dettagli{perc_text}_{self.__time_str}')
            self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
            plt.close(figure)

    def __regioni_dettaglio(self, data, output_base, use_percentage=True, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show
        idx = data.sort_values(by="totale_casi", ascending=False).codice_regione.unique()

        for reg in idx:
            values = data[data['codice_regione'] == reg]
            denominazione = ", ".join(values['denominazione'].unique())
            self.__plot_increment_details(values, denominazione=denominazione, output_base=output_base,
                                          use_percentage=False, show=show, store=store)

    def __regione_plot_details(self, data, output_base, type, show=None, store=None):
        idx = data.sort_values(by="totale_casi", ascending=False).codice_regione.unique()
        colors = plt.get_cmap(self.__color_map)(np.linspace(0, 1, 6))

        for reg in idx:
            values = data[data['codice_regione'] == reg]
            denominazione = ", ".join(values['denominazione'].unique())
            print(f'-> Generazione dettagli {type} per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            plt.plot(values["giorni"], values["totale_casi"], '-o', label="Totale", color=colors[0])
            for x, y in zip(values["giorni"], values["totale_casi"]):
                label = f'{y}'
                plt.annotate(label,  # this is the text
                             (x, y),  # this is the point to label
                             textcoords="offset points",  # how to position the text
                             xytext=(0, 10),  # distance from text to points (x,y)
                             ha='center')  # horizontal alignment can be left, right or center

            plt.plot(values["giorni"], values["deceduti"], '-o', label="Deceduti", color=colors[1])

            plt.plot(values["giorni"], values["dimessi_guariti"], '-o', label="Guariti", color=colors[2])

            plt.plot(values["giorni"], values["terapia_intensiva"], '-o', label="Terapia Intensiva", color=colors[3])

            plt.plot(values["giorni"], values["ricoverati_con_sintomi"], '-o', label="Ricoverati", color=colors[4])

            plt.plot(values["giorni"], values["tamponi"], '-o', label="Tamponi", color=colors[5])
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
                f'Analisi{analysis_desc} evoluzione COVID19 in Italia al {self.__time_str}')
            plt.xticks(rotation=90)
            plt.yscale(type)
            plt.legend()
            plt.grid(b=True, which='major', axis='x')
            base_filename = self.__utils_manager.clean_filename(f'{denominazione}_detail_{type}_{self.__time_str}')
            self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
            plt.close(figure)

    def __plot_increment_details(self, data, denominazione, output_base, use_percentage=True, show=None, store=None):
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

        # colors = plt.cm.rainbow(np.linspace(0, 1, len(rows)))
        colors = plt.get_cmap(self.__color_map)(np.linspace(0, 1, len(rows)))

        index = np.arange(len(columns))
        bar_width = 0.8
        format_str = "{:+.1%}" if use_percentage else '{:+d}'

        cell_text = []
        plt.bar(index, incrementi, bar_width, color=colors[0], align="center", label="Contagi", zorder=10)
        cell_text.append([format_str.format(x) for x in incrementi])
        plt.bar(index, tamponi, bar_width, color=colors[1], align="center", label="Tamponi", zorder=0)
        cell_text.append([format_str.format(x) for x in tamponi])
        cell_text.append(["{:+.1%}".format(x) for x in percentali])

        plt.title(f'Incremento{perc_text} tamponi e contagiati COVID19 in {denominazione} al {self.__time_str}')

        plt.xticks(index, columns, rotation=90)
        plt.legend()

        incrementi_array = incrementi.to_numpy()
        tamponi_array = tamponi.to_numpy()
        for i in range(len(index)):
            label1 = "{0:.1%}".format(incrementi_array[i]) if use_percentage else f'{incrementi_array[i]}'
            label2 = "{0:.1%}".format(tamponi_array[i]) if use_percentage else f'{tamponi_array[i]}'
            y_off1 = incrementi_array[i] / 1000
            y_off2 = tamponi_array[i] / 1000
            x_off = (bar_width / 2)
            plt.text(x=index[i] - x_off, y=incrementi_array[i] + y_off1, s=label1, size=6, zorder=20)
            plt.text(x=index[i] - x_off, y=tamponi_array[i] + y_off2, s=label2, size=6, zorder=20)

        base_filename = self.__utils_manager.clean_filename(f'{denominazione}_dettagli{perc_text}_{self.__time_str}')
        self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
        plt.close(figure)

    def __province_plot(self, data, output_base, type, show=None, store=None):
        plt.close('all')
        figure = plt.figure(figsize=(16, 10))

        regione = ", ".join(data.denominazione_regione.unique())

        idx = data.sort_values(by="totale_casi", ascending=False).codice_provincia.unique()
        colors = plt.get_cmap(self.__color_map)(np.linspace(0, 1, len(idx)))

        i=0
        for prov in idx:
            values = data[data['codice_provincia'] == prov]
            denominazione = ", ".join(values.denominazione.unique())
            giorni = values['giorni']
            contagiati = values['totale_casi']
            plt.plot(giorni, contagiati, '-o', label=denominazione + " Totale", color=colors[i])
            i = i+1

        analysis_desc = ""
        if type == "log":
            analysis_desc = " logaritmica"
        plt.title(f'Analisi{analysis_desc} evoluzione COVID19 nelle province della {regione} al {self.__time_str}')
        plt.xticks(rotation=90)
        plt.yscale(type)
        plt.legend()
        plt.grid(b=True, which='major', axis='x')
        base_filename = self.__utils_manager.clean_filename(f'province_{regione}_{type}_{self.__time_str}')
        self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
        plt.close(figure)

    def __province_log(self, data, output_base, show=None, store=None):
        self.__province_plot(data, output_base=output_base, type="log", show=show, store=store)

    def __province_linear(self, data, output_base, show=None, store=None):
        self.__province_plot(data, output_base=output_base, type="linear", show=show, store=store)

    def __province_increment(self, data, output_base, use_percentage=True, show=None, store=None):
        plt.close('all')

        regione = ", ".join(data.denominazione_regione.unique())

        idx = data.sort_values(by="totale_casi", ascending=False).codice_provincia.unique()

        for prov in idx:
            values = data[data['codice_provincia'] == prov]
            perc_text = " percentuale" if use_percentage else ""
            denominazione = ", ".join(values.denominazione.unique())
            print(f'--> Generazione grafici a barre per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            self.__plot_increment(data=values, denominazione=denominazione, use_percentage=use_percentage)

            base_filename = self.__utils_manager.clean_filename(
                f'{regione}_{denominazione}_incrementi{perc_text}_{self.__time_str}')
            self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
            plt.close(figure)

    def __table_rapporto_tamponi_contagi(self, data_nazionale, data_regionale, output_base, show=None,
                                         store=None):
        columns = ('Tamponi', 'Contagi', 'delta contagi', '% su tamponi')
        idx = data_regionale.sort_values(by="totale_casi", ascending=False).codice_regione.unique()
        rows = [data_nazionale['denominazione'].unique()[0], ] + [
            data_regionale[data_regionale['codice_regione'] == x]['denominazione'].unique()[0] for x in
            idx]
        n_rows = [0, ] + [x for x in idx]
        cell_text = []

        for x in n_rows:
            if x == 0:
                cell_text.append(self.__table_rapporto_tamponi_contagi_row(data_nazionale))
            else:
                cell_text.append(
                    self.__table_rapporto_tamponi_contagi_row(data_regionale[data_regionale['codice_regione'] == x]))

        self.__plot_table(cell_text=cell_text, columns=columns, rows=rows, output_base=output_base,
                          table_title="Riepilogo_TamponiContagi", show=show, store=store)

    def __table_rapporto_tamponi_contagi_row(self, data):
        incrementi_tamponi = "{:+d}".format(abs(data['incrementi_tamponi'].array[-1]))
        incrementi = "{:+d}".format(data['incrementi'].array[-1])
        incrementi_percentuali = "{0:+.1%}".format(data['incrementi_percentuali'].array[-1])
        rapporto = "{0:+.1%}".format(data['incrementi'].array[-1] / abs(data['incrementi_tamponi'].array[-1])) if \
            data['incrementi_tamponi'].array[-1] != 0 else "ND/NP"
        row = [incrementi_tamponi, incrementi, incrementi_percentuali, rapporto]
        return row

    def __plot_table(self, cell_text, columns, rows, output_base, table_title, show=None, store=None):
        colors = plt.get_cmap(self.__color_map)(np.linspace(0, 1, len(rows)))
        plt.close('all')
        plt.table(cellText=cell_text,
                  rowLabels=rows,
                  colLabels=columns,
                  rowColours=colors,
                  loc='center')
        plt.title(f'Tabella riepilogo tamponi/contagi COVID 19 in Italia al {self.__time_str}')
        base_filename = self.__utils_manager.clean_filename(
            f'{table_title}_table_{self.__time_str}')
        plt.xticks([])
        plt.yticks([])
        self.__store_and_show(output_base=output_base, base_filename=base_filename, show=show, store=store)
