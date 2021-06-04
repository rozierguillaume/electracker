import urllib.request, json
import pandas as pd

def download_data(url):
    data = []
    with urllib.request.urlopen(url) as url_object:
        data = json.loads(url_object.read().decode())
    return data[0]


def get_all_results(data):
    data_output = {}
    for sondage in data["sondages"]:
        for tour in sondage["tours"]:
            if tour["tour"] == "Premier tour":
                for hypothese in tour["hypotheses"]:
                    for liste in hypothese["tetes_liste"]:
                        tete_liste = liste["tete_liste"]
                        if tete_liste is None:
                            tete_liste = "".join(liste["parti"])
                        if sondage["fin_enquete"]>"2021-02-01":
                            data_output[tete_liste] = data_output.get(tete_liste, {})
                            data_output[tete_liste]["intentions"] = data_output[tete_liste].get("intentions", []) + [liste["intentions"]]
                            data_output[tete_liste]["dates"] = data_output[tete_liste].get("dates", []) + [sondage["fin_enquete"]]
    return data_output


def compute_rolling_means(data_output):
    for candidat in data_output:
        data_output[candidat]["intentions_rolling_mean"] = pd.Series(data_output[candidat]["intentions"]).rolling(window=3).mean().fillna(0).to_list()
    return data_output


def export_data(data, name):
    with open(f"data/output/{name}.json", 'w') as outfile:
        json.dump(data, outfile)


if __name__ == '__main__':
    name = "regionales_PACA"
    data = download_data(f"https://raw.githubusercontent.com/nsppolls/nsppolls/master/{name}.json")
    data_output = get_all_results(data)
    data_output = compute_rolling_means(data_output)
    export_data(data=data_output, name=name)
