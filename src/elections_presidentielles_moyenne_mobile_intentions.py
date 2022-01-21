import json 
import pandas as pd

df = pd.read_csv("https://raw.githubusercontent.com/nsppolls/nsppolls/master/presidentielle.csv")
df = df[df["tour"] == "Premier tour"]
df = df.sort_values(by="fin_enquete")
df = df[df["fin_enquete"]>"2021-09-01"]

CANDIDATS = ["Marine Le Pen", "Emmanuel Macron", "Yannick Jadot", "Olivier Faure", "Jean-Luc Mélenchon", "Fabien Roussel", "Valérie Pécresse", "Anne Hidalgo", "Christiane Taubira", "Eric Zemmour"]

dict_candidats = {}
for candidat in CANDIDATS:
  df_temp = df[df["candidat"] == "Marine Le Pen"]
  df_temp.index = pd.to_datetime(df_temp["fin_enquete"])
  df_temp = df_temp.resample("1d").mean()
  df_temp_rolling = round(df_temp[["intentions"]].rolling('14d', min_periods=1).mean().dropna(), 2)
  
  dict_candidats[candidat] = {"intentions": df_temp_rolling.intentions.to_list(), "fin_enquete": df_temp_rolling.index.strftime('%Y-%m-%d').to_list()}


with open('data/output/intentionsCandidatsMoyenneMobile14Jours.json', 'w') as outfile:
        json.dump(dict_candidats, outfile)