import json
from multiprocessing.context import set_spawning_popen
from sqlite3 import Timestamp 
import pandas as pd
import datetime
from loess import loess_1d
import numpy as np
from plotly import graph_objects as go

df = pd.read_csv("https://raw.githubusercontent.com/nsppolls/nsppolls/master/presidentielle.csv")
df = df[df["tour"] == "Deuxième tour"]
df = df.sort_values(by="fin_enquete")
df = df[df["fin_enquete"]>"2021-09-01"]

HYPOTHÈSES = ["Hypothèse Macron / Le Pen"]

CANDIDATS = {"Marine Le Pen": {"couleur": "#04006e"},
            "Emmanuel Macron": {"couleur": "#0095eb"}, 
            "Jean-Luc Mélenchon": {"couleur": "#de001e"},
            "Eric Zemmour": {"couleur": "#010038"},    
            }

dict_candidats = {}
derniere_intention = pd.DataFrame() #columns=["candidat", "intentions"])

df["hypothese"] = df["hypothese"].fillna("hypothèse confirmée")

for hypothèse in HYPOTHÈSES:

  df_temp_hypothese = df[df["hypothese"].isin([hypothèse, "hypothèse confirmée"])]
  dict_hypothèses = {}

  for candidat in df_temp_hypothese.candidat.unique():
    print(candidat)
    df_temp = df_temp_hypothese[df_temp_hypothese["candidat"] == candidat]

    df_temp.index = pd.to_datetime(df_temp["fin_enquete"])
    
    df_temp_rolling = df_temp[["intentions", "erreur_inf", "erreur_sup"]].rolling('10d', min_periods=1).mean().shift(-5).dropna()

    df_temp_rolling_std = df_temp[["intentions"]].rolling('10d', min_periods=1).std().shift(-5).dropna()

    df_temp_rolling = round(df_temp_rolling.resample("1d").mean().dropna(), 2).rolling(window=3, center=True).mean().dropna()

    df_temp_rolling_std = round(df_temp_rolling_std.resample("1d").mean().dropna(), 2).rolling(window=3, center=True).mean().dropna()

    derniere_intention = derniere_intention.append({"candidat": candidat, "intentions": df_temp_rolling.intentions.to_list()[-1]}, ignore_index=True)
    
    fin_enquete_ts = pd.to_datetime(df_temp["fin_enquete"]).astype(np.int64) // 10 ** 9

    def calculer_sondages_candidat(frac=0.15):
        xout, yout, wout = loess_1d.loess_1d(fin_enquete_ts, df_temp.intentions.values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)

        _, yout_erreur_inf, _ = loess_1d.loess_1d(fin_enquete_ts, df_temp.erreur_inf.values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)
        _, yout_erreur_sup, _ = loess_1d.loess_1d(fin_enquete_ts, df_temp.erreur_sup.values, xnew=None, degree=1, frac=frac,
                                  npoints=None, rotate=False, sigy=None)

        xout_dt = [datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d') for date in xout]

        dict_hypothèses[candidat] = {"intentions_loess": {"fin_enquete": xout_dt, "valeur": list(yout.astype(float)), "std": df_temp_rolling_std.intentions.to_list(), "erreur_inf": list(yout_erreur_inf.astype(float)), "erreur_sup": list(yout_erreur_sup.astype(float))},
                                    "intentions": {"fin_enquete": df_temp.index.strftime('%Y-%m-%d').to_list(), "valeur": df_temp.intentions.to_list()},
                                    "derniers_sondages": [],
                                    "couleur": CANDIDATS[candidat]["couleur"]}

    try:
      calculer_sondages_candidat()
    except Exception as e:
      try:
        calculer_sondages_candidat(frac=0.5)
      except Exception as e:
        print("== error ==")
        print(e)
        print("==   ==")

  dict_candidats[hypothèse] = {"candidats": dict_hypothèses}

dict_donnees = {"dernier_sondage": df["fin_enquete"].max(), 
                "mise_a_jour": datetime.datetime.now().strftime(format="%Y-%m-%d %H:%M"),
                "hypotheses": dict_candidats}

with open('data/output/intentionsCandidatsMoyenneMobile14JoursLoessDeuxiemeTour.json', 'w') as outfile:
        json.dump(dict_donnees, outfile)

