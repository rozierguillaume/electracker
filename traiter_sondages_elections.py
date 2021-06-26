#!/usr/bin/python
# -*- coding: latin-1 -*-

import urllib.request, json
import pandas as pd
import numpy as np
import re

REGIONS = ["ARA", "BZH", "CVL", "GE", "HDF", "IDF", "NA", "N", "OCC", "PACA", "PDL", "BFC"]
REGIONS_NOMS = {"PACA":"Provence Alpes Côte d'Azur",
               "BZH":"Bretagne",
                "ARA":"Auvergne Rhône Alpes",
                "CVL":"Centre Val de Loire",
                "GE":"Grand Est",
                "HDF":"Hauts-de-France",
                "IDF":"Île-de-France",
                "N":"Normandie",
                "NA":"Nouvelle Aquitaine",
                "OCC":"Occitanie",
                "PDL":"Pays-de-Loire",
                "BFC":"Bourgogne-Franche-Comté"}

def download_data(url):
    data = []
    with urllib.request.urlopen(url) as url_object:
        data = json.loads(url_object.read().decode())
    return data[0]

def get_color_candidate(team):
    team = team.lower()

    if "socialiste" in team:
        return "pink"
    if "rassemblement national" in team:
        return "black"
    if "les républicains" in team:
        return "darkblue"
    if ("lrem" in team) or ("lrm" in team):
        return "blue"
    if "écologie" in team:
        return "green"
    if "lutte ouvrière" in team:
        return "red"
    if "ee-lv" in team:
        return "green"
    if ("communiste" in team) or ("insoumis" in team):
        return "red"
    return "grey"

def get_team(parti):
    if(type(parti) is str):
        return parti
    else:
        return ", ".join(list(parti))

def construire_liste_ordonnee_candidats(data):
    candidats = list(data.keys())
    intentions_rolling_mean = [round(data[candidat]["intentions_rolling_mean"][-1], 1) for candidat in candidats]
    indices_tries = np.argsort(-np.array(intentions_rolling_mean))
    return np.array(candidats)[indices_tries].tolist(), (np.array(intentions_rolling_mean)[indices_tries]).tolist()

def sondage_le_plus_recent(date_sondage, dates):
    if len(dates) == 0:
        return True
    if date_sondage >= max(dates):
        return True
    return False

def get_all_results(data, premier_tour=True):
    if premier_tour:
        filter = "Premier tour"
    else:
        filter = "Deuxième tour"

    data_output = {"data": {}}
    for sondage in data["sondages"]:
        for tour in sondage["tours"]:
            if tour["tour"] == filter:
                for hypothese in tour["hypotheses"]:
                    for liste in hypothese["tetes_liste"]:
                        tete_liste = liste["tete_liste"]
                        if tete_liste is None:
                            tete_liste = "".join(liste["parti"])
                        if sondage["fin_enquete"]>"2021-05-15":
                            data_output["data"][tete_liste] = data_output["data"].get(tete_liste, {})
                            data_output["data"][tete_liste]["intentions"] = data_output["data"][tete_liste].get("intentions", []) + [liste["intentions"]]
                            data_output["data"][tete_liste]["dates"] = data_output["data"][tete_liste].get("dates", []) + [sondage["fin_enquete"]]
                            if sondage_le_plus_recent(sondage["fin_enquete"], data_output["data"][tete_liste]["dates"]):
                                data_output["data"][tete_liste]["parti"] = get_team(liste["parti"])
                            data_output["data"][tete_liste]["couleur"] = get_color_candidate(team=data_output["data"][tete_liste]["parti"])
    return data_output


def compute_rolling_means(data_output):
    for candidat in data_output["data"]:
        if len(data_output["data"][candidat]["intentions"]) >=3:
            data_output["data"][candidat]["intentions_rolling_mean"] = pd.Series(data_output["data"][candidat]["intentions"]).rolling(window=3).mean().fillna(0).to_list()
        else:
            data_output["data"][candidat]["intentions_rolling_mean"] = data_output["data"][candidat]["intentions"]

    return data_output


def export_data(data, name, premier_tour):
    suffix = "second_tour"
    if premier_tour:
        suffix = "premier_tour"

    name = re.sub("[.*%20.*]", "", name)
    with open(f"data/output/sondages_{name}_{suffix}.json", 'w') as outfile:
        json.dump(data, outfile)

def export_metadata():
    metadata_json = {"regions": REGIONS, "regions_noms": REGIONS_NOMS}
    with open(f"data/output/regionales_metadata.json", 'w') as outfile:
        json.dump(metadata_json, outfile)


def clean_small_candidates(data):
    return data
    #for candidat in data:
        #if candidat["intentions"] < 3:



def get_regions_polls():
    for region in REGIONS:
        if region=="BZH":
            region="%20BZH"
        name = f"regionales_{region}"
        data = download_data(f"https://raw.githubusercontent.com/nsppolls/nsppolls/master/{name}.json")

        for premier_tour in [True, False]:
            data_output = get_all_results(data, premier_tour=premier_tour)
            data_output = compute_rolling_means(data_output)
            data_output["candidats_ordonnes"], data_output["intentions_ordonnees"] = construire_liste_ordonnee_candidats(data_output["data"])
            export_data(data=data_output, name=name, premier_tour=premier_tour)

    export_metadata()


if __name__ == '__main__':
    get_regions_polls()
