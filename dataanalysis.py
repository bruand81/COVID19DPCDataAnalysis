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

    def __init__(self, time_str, show=False, store=True):
        self.__time_str = time_str
        self.__showGraph = show
        self.__storeGraph = store

    def tabelle(self, file_nazionale, file_regioni, output_base, show=None, store=None):
        print("Generazione tabelle riepilogative")
        Path(output_base).mkdir(parents=True, exist_ok=True)
        if self.__data_nazionale is None:
            self.__data_nazionale = DataManager.nazionale_data(file_nazionale)
        if self.__data_regionale is None:
            self.__data_regionale, self.__codici_regione = DataManager.regioni_data(file_regioni)
        self.__table_rapporto_tamponi_contagi(data_nazionale=self.__data_nazionale,
                                              data_regionale=self.__data_regionale,
                                              output_base=output_base,
                                              show=show,
                                              store=store)

    def analisi_nazione(self, file_nazionale, output_base, latest, show=None, store=None):
        print("Generazione grafici nazionali")
        Path(output_base).mkdir(parents=True, exist_ok=True)

        if self.__data_nazionale is None:
            self.__data_nazionale = DataManager.nazionale_data(file_nazionale)

        self.__nazionale_linear(self.__data_nazionale, output_base=output_base, show=show, store=store)
        self.__nazionale_log(self.__data_nazionale, output_base=output_base, show=show, store=store)
        self.__nazionale_increment(self.__data_nazionale, output_base=output_base, use_percentage=False, show=show, store=store)
        self.__nazionale_increment(self.__data_nazionale, output_base=output_base, use_percentage=True, show=show, store=store)
        self.__nazionale_dettaglio(self.__data_nazionale, output_base=output_base, use_percentage=False, show=show, store=store)

    def analisi_regioni(self, file_regioni, output_base, head_region=0, must_region=None,
                        show=None,
                        store=None):
        print("Generazione grafici regionali")

        Path(output_base).mkdir(parents=True, exist_ok=True)
        must_region = must_region if must_region is not None else [15, 16]
        if self.__data_regionale is None:
            self.__data_regionale, self.__codici_regione = DataManager.regioni_data(file_regioni,
                                                                                    head_region=head_region,
                                                                                    must_region=must_region)

        self.__regioni_linear(self.__data_regionale, output_base_reg=output_base, codici_regione=self.__codici_regione, head_region=5,
                              must_region=must_region, show=show, store=store)
        self.__regioni_log(self.__data_regionale, output_base_reg=output_base, codici_regione=self.__codici_regione, head_region=5,
                           must_region=must_region, show=show, store=store)
        self.__regioni_increment(self.__data_regionale, output_base_reg=output_base, use_percentage=True, show=show, store=store)
        self.__regioni_increment(self.__data_regionale, output_base_reg=output_base, use_percentage=False, show=show, store=store)
        self.__regioni_dettaglio(self.__data_regionale, output_base=output_base, use_percentage=False, show=show, store=store)

    def analisi_province(self, file_province, file_regioni, output_base, generate_bars=None, show=None,
                         store=None):
        print("Generazione grafici province")
        Path(output_base).mkdir(parents=True, exist_ok=True)

        generate_bars = generate_bars if generate_bars is not None else [3, 15]

        for reg in self.__codici_regione:
            data = DataManager.province_data(file_province, target_region=reg, use_increments=True)
            idx = self.__data_regionale['codice_regione'] == reg
            denominazione = ",".join(self.__data_regionale[idx].denominazione_regione.unique())
            print(f'-> Generazione grafici provinciali per regione {denominazione}')
            self.__province_linear(data, output_base=output_base, show=show, store=store)
            self.__province_log(data, output_base=output_base, show=show, store=store)
            if reg in generate_bars:
                self.__province_increment(data, output_base=output_base, show=show, store=store)
                self.__province_increment(data, output_base=output_base, show=show, store=store)

    def __nazionale_plot(self, data, output_base, type, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show

        plt.close('all')
        figure = plt.figure(figsize=(16, 10))
        plt.plot(data["giorni"], data["totale_casi"], '-o', label="Totale")
        if type == "linear":
            for x, y in zip(data["giorni"].to_numpy(), data["totale_casi"].to_numpy()):
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
        if type == "linear":
            for x, y in zip(data["giorni"].to_numpy(), data["tamponi"].to_numpy()):
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
        base_filename = self.__utils_manager.clean_filename(f'Italia_{type}_{self.__time_str}')
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
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show

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

        base_filename = self.__utils_manager.clean_filename(f'Italia_incrementi{perc_text}_{self.__time_str}')
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

    def __regioni_plot(self, data, output_base, type, head_region, must_region, codici_regione, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show

        plt.close('all')
        figure = plt.figure(figsize=(16, 10))

        selection = np.unique(np.concatenate((codici_regione[:head_region], must_region)))
        data_selected = {x: data[data["codice_regione"] == x] for x in selection}

        denominazioni = []
        for reg, values in data_selected.items():
            X = values['giorni']
            Contagiati = values['totale_casi']
            denominazione = ", ".join(values['denominazione'].unique())
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
        base_filename = self.__utils_manager.clean_filename(f'Riassunto_regionale_{type}_{self.__time_str}')
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()
        plt.close(figure)

    def __regioni_log(self, data, output_base_reg, codici_regione, head_region=5, must_region=None, show=None,
                      store=None):
        print("-> Generazione grafico evoluzione logaritmica")
        must_region = must_region if must_region is not None else [15]
        self.__regioni_plot(data, output_base=output_base_reg, type="log", codici_regione=codici_regione,
                            head_region=head_region,
                            must_region=must_region, show=show, store=store)

    def __regioni_linear(self, data, output_base_reg, codici_regione, head_region=5, must_region=None, show=None,
                         store=None):
        print("-> Generazione grafico evoluzione lineare")
        must_region = must_region if must_region is not None else [15]
        self.__regioni_plot(data, output_base=output_base_reg, type="linear", codici_regione=codici_regione,
                            head_region=head_region,
                            must_region=must_region, show=show, store=store)

    def __regioni_increment(self, data, output_base_reg, use_percentage=True, show=None, store=None):
        Path(output_base_reg).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show

        perc_text = " percentuale" if use_percentage else ""
        idx = data.sort_values(by="totale_casi", ascending=False).codice_regione.unique()

        for reg in idx:
            values = data[data['codice_regione'] == reg]
            denominazione = ", ".join(values['denominazione'].unique())
            print(f'-> Generazione grafici a barre per {denominazione}')
            plt.close('all')
            figure = plt.figure(figsize=(16, 10))
            incrementi = values['incrementi_percentuali'] if use_percentage else values['incrementi']
            incrementi = incrementi.to_numpy()
            giorni = values['giorni'].to_numpy()
            y_pos = np.arange(len(giorni))
            plt.bar(y_pos, incrementi, align='center', alpha=0.5)
            plt.xticks(y_pos, giorni)
            plt.ylabel('Incremento casi giornaliero')
            plt.xlabel('Giorni')
            plt.xticks(rotation=90)
            plt.title(f'Incremento{perc_text} contagi COVID19 in {denominazione}')

            for i in range(len(y_pos)):
                label = "{0:.1%}".format(incrementi[i]) if use_percentage else f'{incrementi[i]}'
                y_off = 0.01 if use_percentage else 0.1
                plt.text(x=y_pos[i] - 0.25, y=incrementi[i] + y_off, s=label, size=6)

            base_filename = self.__utils_manager.clean_filename(
                f'{denominazione}_incrementi{perc_text}_{self.__time_str}')
            if store:
                plt.savefig(f'{output_base_reg}{base_filename}.png', bbox_inches='tight')
                plt.savefig(f'{output_base_reg}{base_filename}.pdf', bbox_inches='tight')
            if show:
                plt.show()
            plt.close(figure)

    def __regioni_increment_details(self, data, output_base, use_percentage=True, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show

        perc_text = " percentuale" if use_percentage else ""
        idx = data.sort_values(by="totale_casi", ascending=False).codice_regione.unique()

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

            base_filename = self.__utils_manager.clean_filename(
                f'{denominazione}_dettagli{perc_text}_{self.__time_str}')
            if store:
                plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
                plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
            if show:
                plt.show()
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
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show
        idx = data.sort_values(by="totale_casi", ascending=False).codice_regione.unique()

        for reg in idx:
            values = data[data['codice_regione'] == reg]
            denominazione = ", ".join(values['denominazione'].unique())
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
            base_filename = self.__utils_manager.clean_filename(f'{denominazione}_detail_{type}_{self.__time_str}')
            if store:
                plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
                plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
            if show:
                plt.show()
            plt.close(figure)

    def __plot_increment_details(self, data, denominazione, output_base, use_percentage=True, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show

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

        colors = plt.cm.rainbow(np.linspace(0, 1, len(rows)))

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
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()
        plt.close(figure)

    def __province_plot(self, data, output_base, type, show=None, store=None):
        Path(output_base).mkdir(parents=True, exist_ok=True)
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show

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
        base_filename = self.__utils_manager.clean_filename(f'province_{regione}_{type}_{self.__time_str}')
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
        store = self.__storeGraph if store is None else store
        show = self.__showGraph if show is None else show

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

            incrementi_array = incrementi.to_numpy()
            for i in range(len(y_pos)):
                label = "{0:.1%}".format(incrementi_array[i]) if use_percentage else f'{incrementi_array[i]}'
                y_off = 0.01 if use_percentage else 0.1
                plt.text(x=y_pos[i] - 0.25, y=incrementi_array[i] + y_off, s=label, size=6)

            base_filename = self.__utils_manager.clean_filename(
                f'{regione}_{denominazione}_incrementi{perc_text}_{self.__time_str}')
            if store:
                plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
                plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
            if show:
                plt.show()
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
                cell_text.append(self.__table_rapporto_tamponi_contagi_row(data_regionale[data_regionale['codice_regione'] == x]))
        # print(cell_text)
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
        plt.close('all')
        plt.table(cellText=cell_text,
                  rowLabels=rows,
                  colLabels=columns,
                  loc='center')
        plt.title("Tabella andamento giornaliero")
        base_filename = self.__utils_manager.clean_filename(
            f'{table_title}_table_{self.__time_str}')
        plt.xticks([])
        plt.yticks([])
        if store:
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()