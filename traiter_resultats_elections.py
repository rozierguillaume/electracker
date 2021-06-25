#!/usr/bin/python
# -*- coding: latin-1 -*-

import urllib.request, json
import pandas as pd
import numpy as np
import re

REGIONS = ["ARA", "BZH", "CVL", "GE", "HDF", "IDF", "NA", "N", "OCC", "PACA", "PDL"]
REGIONS_NOMS = {"PACA":"Provence Alpes Côte d'Azur",
               "BZH":"Bretagne",
                "ARA":"Auvergne Rhône Alpes",
                "CVL":"Centre Val de Loire",
                "GE":"Grand Est",
                "HDF":"Hauts-de-France",
                "IDF":"Île-de-France",
                "N":"Nord",
                "NA":"Nouvelle Aquitaine",
                "OCC":"Occitanie",
                "PDL":"Pays-de-Loire"}

def get_data(region, tour):
    return pd.read_csv(f"data/input/resultats_regionales_{region}_{tour}_tour.csv")

def data_to_dic(data):
    data = data.set_index("candidat")
    return data.to_json(orient="index")

def export_data(dic_data, region, tour):
    with open(f"data/output/resultats_regionales_{region}_{tour}_tour.json", 'w') as outfile:
        json.dump(dic_data, outfile)

def execute():
    for region in REGIONS:
        for tour in ["premier"]:
            data = get_data(region, tour)
            dic_data = data_to_dic(data)
            export_data(dic_data, region, tour)


if __name__ == '__main__':
    execute()
