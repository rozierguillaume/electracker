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
df["hypothese"] = df["candidat_T1"] + " " + df["choix_T2"]


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
            "Nicolas Dupont-Aignan": {"couleur": "#3a84c4"}            
            }

dict_candidats = {}

for hypothèse in df.hypothese.unique():

  df_temp_hypothese = df[df["hypothese"] == hypothèse]
  dict_hypothèses = {}

  for candidat in df_temp_hypothese.candidat_T1.unique():
    print(candidat)
    df_temp = df_temp_hypothese[df_temp_hypothese["candidat_T1"] == candidat]
  
    fin_enquete_ts = df_temp["fin_enquete"].astype(np.int64) // 10 ** 9

    def calculer_sondages_candidat(frac=0.2):
        xout, yout, wout = loess_1d.loess_1d(fin_enquete_ts.values, df_temp.part.values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)

        _, yout_erreur_inf, _ = loess_1d.loess_1d(fin_enquete_ts.values, (df_temp.part-2).values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)
        _, yout_erreur_sup, _ = loess_1d.loess_1d(fin_enquete_ts.values, (df_temp.part+2).values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)

        xout_dt = [datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d') for date in xout]
        fin_enquete_dt = [date.strftime('%Y-%m-%d') for date in df["fin_enquete"].to_list()]

        dict_hypothèses[candidat] = {"intentions_loess": {"fin_enquete": xout_dt, "valeur": list(yout.astype(float)), "erreur_inf": list(yout_erreur_inf.astype(float)), "erreur_sup": list(yout_erreur_sup.astype(float))},
                                    "intentions": {"fin_enquete": fin_enquete_dt, "valeur": df_temp.part.to_list()},
                                    "derniers_sondages": [],
                                    "couleur": CANDIDATS[candidat]["couleur"]}

    try:
      calculer_sondages_candidat()
    except Exception as e:
      try:
        calculer_sondages_candidat(frac=0.5)
      except Exception as e:
        fin_enquete_dt = [date.strftime('%Y-%m-%d') for date in df["fin_enquete"].to_list()]
        dict_hypothèses[candidat] = {"intentions_loess": {"fin_enquete": [], "valeur": [], "erreur_inf": [], "erreur_sup": []},
                                    "intentions": {"fin_enquete": fin_enquete_dt, "valeur": df_temp.part.to_list()},
                                    "derniers_sondages": [],
                                    "couleur": CANDIDATS[candidat]["couleur"]}
        #print("== error ==")
        #print(e)
        #print("==   ==")

  dict_candidats[hypothèse] = {"candidats": dict_hypothèses}

dict_donnees = {"dernier_sondage": df["fin_enquete"].max().strftime('%Y-%m-%d'), 
                "mise_a_jour": datetime.datetime.now().strftime(format="%Y-%m-%d %H:%M"),
                "hypotheses": dict_candidats}

with open('data/output/intentionsCandidatsLoessReportsVoix.json', 'w') as outfile:
        json.dump(dict_donnees, outfile)

