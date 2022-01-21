import json 
import pandas as pd
import datetime

df = pd.read_csv("https://raw.githubusercontent.com/nsppolls/nsppolls/master/presidentielle.csv")
df = df[df["tour"] == "Premier tour"]
df = df.sort_values(by="fin_enquete")
df = df[df["fin_enquete"]>"2021-09-01"]

CANDIDATS = {"Marine Le Pen": {"couleur": "#04006e"}, 
            "Emmanuel Macron": {"couleur": "#0095eb"}, 
            "Yannick Jadot": {"couleur": "#0bb029"},
            "Jean-Luc Mélenchon": {"couleur": "#de001e"},
            "Fabien Roussel": {"couleur": "#940014"},
            "Valérie Pécresse": {"couleur": "#0242e3"},
            "Anne Hidalgo": {"couleur": "#b339a4"},
            "Christiane Taubira": {"couleur": "#c7a71a"},
            "Eric Zemmour": {"couleur": "#010038"}}

dict_candidats = {}
for candidat in CANDIDATS:
  df_temp = df[df["candidat"] == candidat]
  df_temp.index = pd.to_datetime(df_temp["fin_enquete"])
  
  df_temp_rolling = df_temp[["intentions"]].rolling('14d', min_periods=1).mean().dropna()
  df_temp_rolling_std = df_temp[["intentions"]].rolling('14d', min_periods=1).std().fillna(method="bfill")

  df_temp_rolling = round(df_temp_rolling.resample("1d").mean().dropna(), 2)
  df_temp_rolling_std = round(df_temp_rolling_std.resample("1d").mean().dropna(), 2)
  
  dict_candidats[candidat] = {"intentions_moy_14d": {"fin_enquete": df_temp_rolling.index.strftime('%Y-%m-%d').to_list(), "valeur": df_temp_rolling.intentions.to_list(), "std": df_temp_rolling_std.intentions.to_list()},
                              "intentions": {"fin_enquete": df_temp.index.strftime('%Y-%m-%d').to_list(), "valeur": df_temp.intentions.to_list()},
                              "couleur": CANDIDATS[candidat]["couleur"],}

  dict_candidats["dernier_sondage"] = df["fin_enquete"].max()
  dict_candidats["mise_a_jour"] = datetime.datetime.now().strftime(format="%Y-%m-%d %H:%M")

with open('data/output/intentionsCandidatsMoyenneMobile14Jours.json', 'w') as outfile:
        json.dump(dict_candidats, outfile)