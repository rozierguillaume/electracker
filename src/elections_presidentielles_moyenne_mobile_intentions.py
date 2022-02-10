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
            "Eric Zemmour": {"couleur": "#010038"},
            "Nathalie Arthaud": {"couleur": "#8f0007"},
            "Jean Lassalle": {"couleur": "#c96800"},
            "Philippe Poutou": {"couleur": "#82001a"},
            "François Asselineau": {"couleur": "#12004f"}            
            }

dict_candidats = {}
derniere_intention = pd.DataFrame() #columns=["candidat", "intentions"])
for candidat in CANDIDATS:
  df_temp = df[df["candidat"] == candidat]
  df_temp.index = pd.to_datetime(df_temp["fin_enquete"])
  
  df_temp_rolling = df_temp[["intentions", "erreur_inf", "erreur_sup"]].rolling('14d', min_periods=1).mean().dropna()
  df_temp_rolling_std = df_temp[["intentions"]].rolling('14d', min_periods=1).std().fillna(method="bfill")

  df_temp_rolling = round(df_temp_rolling.resample("1d").mean().dropna(), 2).rolling(window=7).mean().dropna()
  df_temp_rolling_std = round(df_temp_rolling_std.resample("1d").mean().dropna(), 2).rolling(window=7).mean().dropna()
  
  derniere_intention = derniere_intention.append({"candidat": candidat, "intentions": df_temp_rolling.intentions.to_list()[-1]}, ignore_index=True)

  dict_candidats[candidat] = {"intentions_moy_14d": {"fin_enquete": df_temp_rolling.index.strftime('%Y-%m-%d').to_list(), "valeur": df_temp_rolling.intentions.to_list(), "std": df_temp_rolling_std.intentions.to_list(), "erreur_inf": df_temp_rolling.erreur_inf.to_list(), "erreur_sup": df_temp_rolling.erreur_sup.to_list()},
                              "intentions": {"fin_enquete": df_temp.index.strftime('%Y-%m-%d').to_list(), "valeur": df_temp.intentions.to_list()},
                              "derniers_sondages": [],
                              "couleur": CANDIDATS[candidat]["couleur"]}

dict_donnees = {"dernier_sondage": df["fin_enquete"].max(), 
                "mise_a_jour": datetime.datetime.now().strftime(format="%Y-%m-%d %H:%M"),
                "candidats": dict_candidats}

with open('data/output/intentionsCandidatsMoyenneMobile14Jours.json', 'w') as outfile:
        json.dump(dict_donnees, outfile)

derniere_intention.sort_values(by="intentions", ascending=False, inplace=True)

dict_derniers_sondages = {}
for (idx, candidat_sorted) in enumerate(reversed(derniere_intention.candidat.values)):
  dict_derniers_sondages[candidat_sorted] = {"derniere_intention": round(derniere_intention.intentions.values[idx],1), "derniers_sondages": {}}

  df_temp = df[df["candidat"] == candidat_sorted].sort_values(by="fin_enquete", ascending=False).reset_index()

  for idx in range(0, 10):
    sondage = df_temp.loc[idx, :]
    dict_derniers_sondages[candidat_sorted]["derniers_sondages"][str(sondage["id"])] = {"fin_enquete": sondage["fin_enquete"], 
                                                                                        "debut_enquete": sondage["debut_enquete"],
                                                                                        "commanditaire": sondage["commanditaire"],
                                                                                        "nom_institut": sondage["nom_institut"],
                                                                                        "intentions": sondage["intentions"],
                                                                                        "erreur_sup": round(sondage["erreur_sup"], 1),
                                                                                        "erreur_inf": round(sondage["erreur_inf"], 1)}


with open('data/output/derniersSondagesCandidats.json', 'w') as outfile:
        json.dump(dict_derniers_sondages, outfile)