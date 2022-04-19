import json
from multiprocessing.context import set_spawning_popen
from sqlite3 import Timestamp 
import pandas as pd
import datetime
from loess import loess_1d
import numpy as np
from plotly import graph_objects as go
import dateparser

df = pd.read_csv("https://raw.githubusercontent.com/nsppolls/nsppolls/master/reports.csv", parse_dates=['fin_enquete'], date_parser=dateparser.parse)
df = df.sort_values(by="fin_enquete")


CANDIDATS = {"Marine Le Pen": {"couleur": "#04006e"},
            "Emmanuel Macron": {"couleur": "#0095eb"}, 
            "Yannick Jadot": {"couleur": "#0bb029"},
            "Jean-Luc Mélenchon": {"couleur": "#de001e"},
            "Fabien Roussel": {"couleur": "#940014"},
            "Valérie Pécresse": {"couleur": "#0242e3"},
            "Anne Hidalgo": {"couleur": "#b339a4"},
            "Eric Zemmour": {"couleur": "#010038"},
            "Nathalie Arthaud": {"couleur": "#8f0007"},
            "Jean Lassalle": {"couleur": "#c96800"},
            "Philippe Poutou": {"couleur": "#82001a"},
            "Nicolas Dupont-Aignan": {"couleur": "#3a84c4"},
            "Abstention": {"couleur": "grey"}         
            }

dict_candidats = {}

for candidat_T1 in df.candidat_T1.unique():

  df_candidat_T1 = df[df["candidat_T1"] == candidat_T1]
  dict_candidats_T1 = {}
  print(df_candidat_T1.choix_T2.unique())
  for choix_T2 in df_candidat_T1.choix_T2.unique():
    print(f"{candidat_T1} -> {choix_T2}")
    df_temp = df_candidat_T1[df_candidat_T1["choix_T2"] == choix_T2]
  
    fin_enquete_ts = df_temp["fin_enquete"].astype(np.int64) // 10 ** 9

    def calculer_sondages_candidat(frac=0.4):
        xout, yout, wout = loess_1d.loess_1d(fin_enquete_ts.values, df_temp.part.values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)

        _, yout_erreur_inf, _ = loess_1d.loess_1d(fin_enquete_ts.values, (df_temp.part-2).values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)
        _, yout_erreur_sup, _ = loess_1d.loess_1d(fin_enquete_ts.values, (df_temp.part+2).values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)

        xout_dt = [datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d') for date in xout]
        fin_enquete_dt = [date.strftime('%Y-%m-%d') for date in df_temp["fin_enquete"].to_list()]

        dict_candidats_T1[choix_T2] = {"intentions_loess": {"fin_enquete": xout_dt, "valeur": list(yout.astype(float)), "erreur_inf": list(yout_erreur_inf.astype(float)), "erreur_sup": list(yout_erreur_sup.astype(float))},
                                    "intentions": {"fin_enquete": fin_enquete_dt, "valeur": df_temp.part.to_list()},
                                    "derniers_sondages": [],
                                    "couleur": CANDIDATS[choix_T2]["couleur"]}

    try:
      calculer_sondages_candidat()
    except Exception as e:
      try:
        calculer_sondages_candidat(frac=0.9)
      except Exception as e:
        fin_enquete_dt = [date.strftime('%Y-%m-%d') for date in df_temp["fin_enquete"].to_list()]
        dict_candidats_T1[choix_T2] = {"intentions_loess": {"fin_enquete": [], "valeur": [], "erreur_inf": [], "erreur_sup": []},
                                    "intentions": {"fin_enquete": fin_enquete_dt, "valeur": df_temp.part.to_list()},
                                    "derniers_sondages": [],
                                    "couleur": CANDIDATS[choix_T2]["couleur"]}
        #print("== error ==")
        #print(e)
        #print("==   ==")

  dict_candidats[candidat_T1] = {"candidats": dict_candidats_T1, "couleur": CANDIDATS[candidat_T1]["couleur"]}

dict_donnees = {"dernier_sondage": df["fin_enquete"].max().strftime('%Y-%m-%d'), 
                "mise_a_jour": datetime.datetime.now().strftime(format="%Y-%m-%d %H:%M"),
                "hypotheses": dict_candidats}

with open('data/output/intentionsCandidatsLoessReportsVoix.json', 'w') as outfile:
        json.dump(dict_donnees, outfile)

