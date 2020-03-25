import pandas
import numpy as np
import matplotlib.pyplot as plt
import time
from pathlib import Path
import unicodedata
import string
from git import Repo
from git import RemoteProgress

valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255
storeGraph = False
showGraph = False
timestr = ''
current_ref = ''
force_graph_generation = True

def update_repo(repo_path, base_output_path='.'):
    head_file = Path(f'{base_output_path}/lastrev')
    if head_file.is_file():
        with open(head_file, 'r') as file:
            current_ref = file.read().replace('\n', '')
            file.close()
    else:
        current_ref = None

    repo = Repo(repo_path)
    o = repo.remotes.origin
    for fetch_info in o.pull(progress=MyProgressPrinter()):
        print("Updated %s to %s" % (fetch_info.ref, fetch_info.commit))
        last_rev = f'{fetch_info.commit}'
        if current_ref == last_rev:
            return False
        else:
            print(f'{fetch_info.commit}')
            with open(head_file, 'w+') as file:
                file.write(last_rev)
                file.close()
            return True


def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    # replace spaces
    for r in replace:
        filename = filename.replace(r, '_')

    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename) > char_limit:
        print(
            "Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]

def compute_increments(Contagiati):
    increments = pandas.Series(np.zeros(len(Contagiati), dtype=int))
    increments_percentage = pandas.Series(np.zeros(len(Contagiati)))
    prev_day = 0
    idx = 0
    for cases in Contagiati:
        today_increment = cases - prev_day
        increments.loc[idx] = today_increment
        increments_percentage.loc[idx] = 0 if prev_day == 0 else today_increment / prev_day
        prev_day = cases
        idx = idx + 1
        # print(d)
    return (increments, increments_percentage)

def nazionale_data(nazionale, use_increments=False):
    data_naz = pandas.read_csv(nazionale)

    X = np.array(list(xi[:10] for xi in data_naz['data']))
    # X = range(XLabel.size)
    Contagiati = data_naz['totale_casi']
    Deceduti = data_naz['deceduti']
    Guariti = data_naz['dimessi_guariti']
    TerapiaIntensiva = data_naz['terapia_intensiva']
    Ricoverati = data_naz['ricoverati_con_sintomi']

    # increments = None
    #     # increments_percentage = None

    (increments, increments_percentage) = compute_increments(Contagiati) if use_increments else (None, None)

    # if compute_increments:
    #     increments = pandas.Series(np.zeros(len(Contagiati), dtype=int))
    #     increments_percentage = pandas.Series(np.zeros(len(Contagiati)))
    #     prev_day = 0
    #     idx = 0
    #     for cases in Contagiati:
    #         today_increment = cases - prev_day
    #         increments.loc[idx] = today_increment
    #         increments_percentage.loc[idx] = 0 if prev_day == 0 else today_increment / prev_day
    #         prev_day = cases
    #         idx = idx + 1
    #         # print(d)

    return {
        "giorni": X,
        "totale_casi": Contagiati,
        "deceduti": Deceduti,
        "dimessi_guariti": Guariti,
        "terapia_intensiva": TerapiaIntensiva,
        "ricoverati_con_sintomi": Ricoverati,
        "incrementi": increments,
        "incrementi_percentuali": increments_percentage
    }


def nazionale_plot(nazionale, output_base, type, show=None, store=None):
    Path(output_base).mkdir(parents=True, exist_ok=True)
    if store == None:
        store = storeGraph

    if show == None:
        show = showGraph

    data = nazionale_data(nazionale)

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
    # for x, y in zip(data["giorni"], data["deceduti"]):
    #     label = f'{y}'
    #     plt.annotate(label,  # this is the text
    #                  (x, y),  # this is the point to label
    #                  textcoords="offset points",  # how to position the text
    #                  xytext=(0, 10),  # distance from text to points (x,y)
    #                  ha='center')  # horizontal alignment can be left, right or center

    plt.plot(data["giorni"], data["dimessi_guariti"], '-o', label="Guariti")
    # for x, y in zip(data["giorni"], data["dimessi_guariti"]):
    #     label = f'{y}'
    #     plt.annotate(label,  # this is the text
    #                  (x, y),  # this is the point to label
    #                  textcoords="offset points",  # how to position the text
    #                  xytext=(0, 10),  # distance from text to points (x,y)
    #                  ha='center')  # horizontal alignment can be left, right or center

    plt.plot(data["giorni"], data["terapia_intensiva"], '-o', label="Terapia Intensiva")
    # for x, y in zip(data["giorni"], data["terapia_intensiva"]):
    #     label = f'{y}'
    #     plt.annotate(label,  # this is the text
    #                  (x, y),  # this is the point to label
    #                  textcoords="offset points",  # how to position the text
    #                  xytext=(0, 10),  # distance from text to points (x,y)
    #                  ha='center')  # horizontal alignment can be left, right or center

    plt.plot(data["giorni"], data["ricoverati_con_sintomi"], '-o', label="Ricoverati")
    # for x, y in zip(data["giorni"], data["ricoverati_con_sintomi"]):
    #     label = f'{y}'
    #     plt.annotate(label,  # this is the text
    #                  (x, y),  # this is the point to label
    #                  textcoords="offset points",  # how to position the text
    #                  xytext=(0, 10),  # distance from text to points (x,y)
    #                  ha='center')  # horizontal alignment can be left, right or center


    analysis_desc = ""
    if type == "log":
        analysis_desc = " logaritmica"

    plt.title(
        f'Analisi{analysis_desc} evoluzione COVID19 in Italia')
    plt.xticks(rotation=90)
    plt.yscale(type)
    plt.legend()
    plt.grid(b=True, which='major', axis='x')
    base_filename = clean_filename(f'nazionale_{type}_{timestr}')
    if store:
        #print(f'Salvataggio di {output_base}{base_filename}')
        plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
        plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
    if show:
        plt.show()
    plt.close(figure)


def nazionale_log(nazionale, output_base, show=None, store=None):
   nazionale_plot(nazionale, output_base=output_base, type="log", show=show, store=store)


def nazionale_linear(nazionale, output_base, show=None, store=None):
    nazionale_plot(nazionale, output_base=output_base, type="linear", show=show, store=store)


def nazionale_increment(nazionale, output_base, use_percentage=True, show=None, store=None):
    Path(output_base).mkdir(parents=True, exist_ok=True)
    if store == None:
        store = storeGraph

    if show == None:
        show = showGraph

    data = nazionale_data(nazionale, compute_increments=True)#[['giorni', 'totale_casi']]
    #print(len(data['totale_casi']))

    incrementi = data['incrementi_percentuali'] if use_percentage else data['incrementi']
    figure = plt.figure(figsize=(16, 10))
    y_pos = np.arange(len(data['giorni']))
    plt.bar(y_pos, incrementi, align='center', alpha=0.5)
    plt.xticks(y_pos, data['giorni'])
    plt.ylabel('Incremento casi giornaliero')
    plt.xlabel('Giorni')
    plt.xticks(rotation=90)
    perc_text = " percentuale" if use_percentage else ""
    plt.title(f'Incremento{perc_text} contagi COVID19 in Italia')

    for i in range(len(y_pos)):
        label = "{0:.1%}".format(incrementi[i]) if use_percentage else f'{incrementi[i]}'
        y_off = 0.01 if use_percentage else 0.1
        plt.text(x=y_pos[i]-0.25, y=incrementi[i]+0.01, s=label, size=6)

    base_filename = clean_filename(f'nazionale_incrementi{perc_text}_{timestr}')
    if store:
        # print(f'Salvataggio di {output_base}{base_filename}')
        plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
        plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
    if show:
        plt.show()
    plt.close(figure)


def regioni_data(regioni, head_region, must_region, use_increments=False):
    data_reg = pandas.read_csv(regioni)
    idx = data_reg.groupby(['codice_regione'])['totale_casi'].transform(max) == data_reg['totale_casi']

    if head_region == 0:
        head_region = len(data_reg.groupby(['codice_regione'])['codice_regione'])

    if head_region > 0:
        codici_regione = data_reg[idx].sort_values(by="totale_casi", ascending=False).head(head_region)[
            "codice_regione"].to_numpy()
    else:
        codici_regione = data_reg[idx].sort_values(by="totale_casi", ascending=False).tail(abs(head_region))[
            "codice_regione"].to_numpy()

    # print(type(codici_regione))

    #b = np.array([15])
    if must_region is not None and len(must_region)>0:
        codici_regione = np.unique(np.concatenate((codici_regione, must_region)))
    # print(codici_regione)
    return_data = {}

    for reg in codici_regione:
        data = data_reg[data_reg["codice_regione"] == reg]
        # print(data.denominazione_regione.unique()[0])
        X = np.array(list(xi[:10] for xi in data['data']))
        # X = range(XLabel.size)
        Contagiati = data['totale_casi']
        Deceduti = data['deceduti']
        Guariti = data['dimessi_guariti']

        (increments, increments_percentage) = compute_increments(Contagiati) if use_increments else (None, None)
        # increments = None
        # increments_percentage = None
        #
        # if compute_increments:
        #     increments = pandas.Series(np.zeros(len(Contagiati), dtype=int))
        #     increments_percentage = pandas.Series(np.zeros(len(Contagiati)))
        #     prev_day = 0
        #     idx = 0
        #     for cases in Contagiati:
        #         today_increment = cases - prev_day
        #         increments.loc[idx] = today_increment
        #         increments_percentage.loc[idx] = 0 if prev_day == 0 else today_increment / prev_day
        #         prev_day = cases
        #         idx = idx + 1
        #         # print(d)

        return_data[reg] = {
            "denominazione": data.denominazione_regione.unique()[0],
            "giorni": X,
            "totale_casi": Contagiati,
            "deceduti": Deceduti,
            "dimessi_guariti": Guariti,
            "incrementi": increments,
            "incrementi_percentuali": increments_percentage
        }

    #print(return_data)
    return return_data
        # X = DataFrame(data, columns=['data'])
        # Y = DataFrame(data, columns=['totale_casi'])


def regioni_plot(regioni, output_base,type, head_region, must_region, show=None, store=None):
    Path(output_base).mkdir(parents=True, exist_ok=True)
    if store == None:
        store = storeGraph

    if show == None:
        show=showGraph

    plt.close('all')
    figure = plt.figure(figsize=(16, 10))
    # codici_regione= data_reg.codice_regione.unique()
    # print(data_reg.groupby(['codice_regione'], sort=False)['totale_casi'].transform(max).sort_values(ascending=False).head(5))
    # idx = data_reg.groupby(['codice_regione'], sort=False)['totale_casi'].transform(max) == data_reg['totale_casi']

    data = regioni_data(regioni, head_region=head_region, must_region=must_region)

    denominazioni = []
    for reg, values in data.items():
        X = values['giorni']
        Contagiati = values['totale_casi']
        denominazione = values['denominazione']
        if reg in must_region:
            denominazioni.append(denominazione)
        plt.plot(X, Contagiati, '-o', label=denominazione + " Totale")
        #for x, y in zip(X, Contagiati):
        #    label = f'{y}'
        #    plt.annotate(label,  # this is the text
        #                 (x, y),  # this is the point to label
        #                 textcoords="offset points",  # how to position the text
        #                 xytext=(0, 10),  # distance from text to points (x,y)
        #                 ha='center')  # horizontal alignment can be left, right or center


    analysis_desc = ""
    if type == "log":
        analysis_desc = " logaritmica"

    tail_text = ""
    if len(denominazioni)>0 :
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
    base_filename = clean_filename(f'regionale_{type}_{timestr}')
    if store:
        #print(f'Salvataggio di {output_base}{base_filename}')
        plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
        plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
    if show:
        plt.show()
    plt.close(figure)


def regioni_log(regioni, output_base, head_region=5, must_region=[15], show=None, store=None):
    regioni_plot(regioni, output_base=output_base, type="log", head_region=head_region,
                 must_region=must_region, show=show, store=store)


def regioni_linear(regioni, output_base, head_region=5, must_region=[15], show=None, store=None):
    regioni_plot(regioni, output_base=output_base, type="linear", head_region=head_region,
                 must_region=must_region, show=show, store=store)


def regioni_increment(regioni, output_base, head_region=1, must_region=[15], use_percentage=True, show=None, store=None):
    Path(output_base).mkdir(parents=True, exist_ok=True)
    if store == None:
        store = storeGraph

    if show == None:
        show=showGraph
    # codici_regione= data_reg.codice_regione.unique()
    # print(data_reg.groupby(['codice_regione'], sort=False)['totale_casi'].transform(max).sort_values(ascending=False).head(5))
    # idx = data_reg.groupby(['codice_regione'], sort=False)['totale_casi'].transform(max) == data_reg['totale_casi']

    data = regioni_data(regioni, head_region=head_region, must_region=must_region)

    for reg, values in data.items():
        denominazione = values['denominazione']
        print(f'-> Generazione grafici a barre per {denominazione}')
        plt.close('all')
        figure = plt.figure(figsize=(16, 10))
        incrementi = values['incrementi_percentuali'] if use_percentage else values['incrementi']
        plt.close('all')
        figure = plt.figure(figsize=(16, 10))
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
            plt.text(x=y_pos[i] - 0.25, y=incrementi[i] + 0.01, s=label, size=6)

        base_filename = clean_filename(f'{denominazione}_incrementi{perc_text}_{timestr}')
        if store:
            # print(f'Salvataggio di {output_base}{base_filename}')
            plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
            plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
        if show:
            plt.show()
        plt.close(figure)


def province_data(province, target_region=15, use_increments=False):
    data_prov = pandas.read_csv(province)
    data_prov_in_reg = data_prov[data_prov.codice_regione.eq(target_region)]

    idx = data_prov_in_reg.groupby(['codice_provincia'])['totale_casi'].transform(max) == data_prov_in_reg[
        'totale_casi']

    codici_province = data_prov_in_reg[idx].sort_values(by="totale_casi", ascending=False)[
        "codice_provincia"].to_numpy()
    # print(codici_regione)
    return_data = {}

    for prov in codici_province:
        data = data_prov_in_reg[data_prov_in_reg["codice_provincia"] == prov]
        # print(data.denominazione_regione.unique()[0])
        X = np.array(list(xi[:10] for xi in data['data']))
        # X = range(XLabel.size)
        Contagiati = data['totale_casi']

        (increments, increments_percentage) = compute_increments(Contagiati) if use_increments else (None, None)
        # increments = pandas.Series(np.zeros(len(Contagiati), dtype=int))
        # increments_percentage = pandas.Series(np.zeros(len(Contagiati)))
        # prev_day = 0
        # idx = 0
        # for cases in Contagiati:
        #     today_increment = cases - prev_day
        #     increments.loc[idx] = today_increment
        #     increments_percentage.loc[idx] = 1 if prev_day == 0 else today_increment / prev_day
        #     prev_day = cases
        #     idx = idx + 1

        return_data[prov] = {
            "regione": data.denominazione_regione.unique()[0],
            "denominazione": data.denominazione_provincia.unique()[0],
            "giorni": X,
            "totale_casi": Contagiati,
            "incrementi": increments,
            "incrementi_percentuali": increments_percentage
        }

    # print(return_data)
    return return_data


# noinspection DuplicatedCode
def province_plot(province, output_base, type, target_region, show=None, store=None):
    Path(output_base).mkdir(parents=True, exist_ok=True)
    if store == None:
        store = storeGraph

    if show == None:
        show=showGraph

    plt.close('all')
    figure = plt.figure(figsize=(16, 10))

    data = province_data(province, target_region=target_region)
    regione = ""

    for prov, values in data.items():
        X = values['giorni']
        Contagiati = values['totale_casi']
        denominazione = values['denominazione']
        regione = values['regione']
        plt.plot(X, Contagiati, '-o', label=denominazione + " Totale")
        #for x, y in zip(X, Contagiati):
        #    label = f'{y}'
        #    plt.annotate(label,  # this is the text
        #                 (x, y),  # this is the point to label
        #                 textcoords="offset points",  # how to position the text
        #                 xytext=(0, 10),  # distance from text to points (x,y)
        #                 ha='center')  # horizontal alignment can be left, right or center

    analysis_desc = ""
    if type == "log":
        analysis_desc = " logaritmica"
    plt.title(f'Analisi{analysis_desc} evoluzione COVID19 nelle province della {regione}')
    plt.xticks(rotation=90)
    plt.yscale(type)
    plt.legend()
    plt.grid(b=True, which='major', axis='x')
    base_filename = clean_filename(f'province_{regione}_{type}_{timestr}')
    if store:
        #print(f'Salvataggio di {output_base}{base_filename}')
        plt.savefig(f'{output_base}{base_filename}.png', bbox_inches='tight')
        plt.savefig(f'{output_base}{base_filename}.pdf', bbox_inches='tight')
    if show:
        plt.show()
    plt.close(figure)


def province_log(province, output_base, target_region=15, show=None, store=None):
    province_plot(province, output_base=output_base, type="log",
                  target_region=target_region, show=show, store=store)


def province_linear(province, output_base, target_region=15, show=None, store=None):
    province_plot(province, output_base=output_base, type="linear",
                  target_region=target_region, show=show, store=store)


def get_all_region(regioni):
    data_reg = pandas.read_csv(regioni)

    codici_regione = np.unique(data_reg.codice_regione.to_numpy())

    #print(codici_regione)

    return [codici_regione, data_reg]


def get_last_update(latest):
    data = pandas.read_csv(latest)
    return data.data[0][:10].replace("-","")


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")


if __name__ == '__main__':
    repo_path = '/Users/bruand/Documents Local/analisi/COVID-19'
    updated = update_repo(repo_path)
    #updated = False
    if force_graph_generation or updated:
        print(f'Repository aggiornato. Rigenerazione grafici in corso')
        latest = f'{repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale-latest.csv'
        nazionale = f'{repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
        regioni = f'{repo_path}/dati-regioni/dpc-covid19-ita-regioni.csv'
        province = f'{repo_path}/dati-province/dpc-covid19-ita-province.csv'

        timestr = get_last_update(latest)
        output_base = f'output/{timestr}/'
        output_base_reg = f'output/{timestr}/regionale/'
        output_base_prov = f'output/{timestr}/provinciale/'
        storeGraph = True
        showGraph = False


        print("Generazione grafici nazionali")
        nazionale_linear(nazionale, output_base=output_base)
        nazionale_log(nazionale, output_base=output_base)
        nazionale_increment(nazionale, output_base=output_base, use_percentage=False)
        nazionale_increment(nazionale, output_base=output_base, use_percentage=True)
        print("Generazione grafici regionali")
        regioni_linear(regioni, output_base=output_base_reg, head_region=5, must_region=[15, 16])
        regioni_log(regioni, output_base=output_base_reg, head_region=5, must_region=[15, 16])
        regioni_increment(regioni, output_base=output_base_reg, head_region=0, must_region=[], use_percentage=False)
        regioni_increment(regioni, output_base=output_base_reg, head_region=0, must_region=[], use_percentage=True)
        [codici_regione, data_reg] = get_all_region(regioni)
        for reg in codici_regione:
            idx = data_reg['codice_regione'] == reg
            denominazione = data_reg[idx].denominazione_regione.unique()[0]
            print(f'Generazione grafici provinciali per regione {denominazione}')
            province_linear(province, output_base=output_base_prov, target_region=reg)
            province_log(province, output_base=output_base_prov, target_region=reg)
    else:
        print('Aggiornamento dei grafici non necessario')