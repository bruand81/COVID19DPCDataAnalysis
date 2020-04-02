from datamanager import DataManager
from repomanager import RepoManager
from dataanalysis import AnalisiDati

force_graph_generation = False
gen_nazionale = True
gen_regionale = True
gen_provinciale = True
gen_tabelle_riepilogo = True
show = False
store = True


def main_func():
    repo_path = '/Users/bruand/Documents Local/analisi/COVID-19'
    updated = RepoManager.update_repo(repo_path)
    if force_graph_generation or updated:
        print(f'Repository aggiornato. Rigenerazione grafici in corso')
        nazionale_latest = f'{repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale-latest.csv'
        nazionale = f'{repo_path}/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
        regioni = f'{repo_path}/dati-regioni/dpc-covid19-ita-regioni.csv'
        province = f'{repo_path}/dati-province/dpc-covid19-ita-province.csv'
        regioni_latest = f'{repo_path}/dati-regioni/dpc-covid19-ita-regioni-latest.csv'

        time_str = DataManager.get_last_update(nazionale_latest)
        output_base_path = f'output/{time_str}/'
        output_base_path_reg = f'{output_base_path}regionale/'
        output_base_path_prov = f'{output_base_path}provinciale/'
        analysis = AnalisiDati(time_str=time_str, file_nazionale=nazionale, file_regioni=regioni,
                               file_province=province, show=False, store=True)
        if gen_nazionale:
            analysis.analisi_nazione(file_nazionale=nazionale, output_base=output_base_path, show=show, store=store)

        if gen_tabelle_riepilogo:
            analysis.tabelle(file_nazionale=nazionale, file_regioni=regioni, output_base=output_base_path, show=show,
                             store=store)

        if gen_regionale:
            analysis.analisi_regioni(file_regioni=regioni, output_base=output_base_path_reg, head_region=0,
                                     must_region=None, show=show, store=store)

        if gen_provinciale:
            analysis.analisi_province(file_province=province, output_base=output_base_path_prov, generate_bars=[3, 15],
                                      file_regioni=regioni_latest, show=show, store=store)
    else:
        print('Aggiornamento dei grafici non necessario')


if __name__ == '__main__':
    main_func()
