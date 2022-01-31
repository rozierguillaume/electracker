# -*- coding: utf-8 -*-

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm
import math
import plotly.graph_objects as go
import numpy as np
import kaleido
import os
import tweepy

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')

def return_normal_distribution_candidate(sondage, erreur):
  data = np.arange(sondage-3*erreur, sondage+3*erreur, 0.1)
  x_out=[]
  for x in data:
    x_out += [norm(sondage, erreur).pdf(x)]
  return data, x_out

informations_candidats = {
    "Valérie Pécresse": {
        "couleur": "rgba(22, 64, 121, 255)"
    },
    "Eric Zemmour": {
      "couleur": "rgba(9, 16, 96, 255)"
    },
    "Emmanuel Macron": {
       "couleur": "rgba(89, 185, 249, 255)"
    },
    "Yannick Jadot": {
        "couleur": "rgba(122, 181, 27, 255)"
    },
    "Anne Hidalgo": {
        "couleur": "rgba(219, 65, 91, 255)"
    },
    "Marine Le Pen": {
        "couleur": "rgba(29, 55, 88, 255)"
    },
    "Jean-Luc Mélenchon": {
        "couleur": "rgba(150, 29, 31, 255)"
    },
}

def obtenir_couleur_candidat(candidat):
  return informations_candidats.get(candidat, {'couleur': 'black'})["couleur"]

def recuperer_donnees():
  id_sondages = pd.read_csv("id_sondages.csv")
  df = pd.read_csv("https://raw.githubusercontent.com/nsppolls/nsppolls/master/presidentielle.csv").sort_values(by="fin_enquete", ascending=False)
  df = df[df["tour"] == "Premier tour"]
  df = df.sort_values(by="intentions", ascending=False)
  return df, id_sondages

def exporter_tous_les_id_sondages(df):
  df.sort_values(by="id").id.drop_duplicates().to_csv("id_sondages.csv", index=False)

def graphique_violons(df):
  fig = go.Figure()
  candidats = df.candidat
  idx=4*(len(candidats))

  for candidat in candidats.tolist():
    sondage = df[df["candidat"] == candidat]["intentions"].values[0]
    erreur = df[df["candidat"] == candidat]["erreur_sup"].values[0] - sondage
    couleur = obtenir_couleur_candidat(candidat)

    if sondage>=2:
      x, y = return_normal_distribution_candidate(sondage, erreur)
      fig.add_trace(go.Scatter(x=x, y=[idx]*len(x), line_color=couleur, line_width=0, showlegend=False))
      fig.add_trace(go.Scatter(x=x, y=np.array(y)*10+idx, line_color=couleur, name=candidat, fill="tonexty", showlegend=False))
      fig.add_annotation(
          x=sondage,
          y=idx-0.8,
          text=candidat+"<br>"+str(round(sondage, 1))+" %",
          font=dict(color=couleur),
          showarrow=False
      )
      idx -= 4

  fig.update_xaxes(ticksuffix=" %", title="", tickfont=dict(size=15), side="top")
  fig.update_yaxes(visible=False)
  fig.update_layout(xaxis_showgrid=True, yaxis_showgrid=True, xaxis_zeroline=False)

  fig.add_annotation(
          x=0.5,
          y=1.13,
          xref="paper",
          yref="paper",
          text="<b>Présidentielles</b> : intentions de vote du dernier sondage",
          font=dict(size=25),
          showarrow=False
      )

  info_sondage = df["nom_institut"].values[0] + ", " + df["commanditaire"].values[0]
  dates = [df["debut_enquete"].values[0], df["fin_enquete"].values[0]]
  dates[0] = dates[0][-2:] + "/" + dates[0][-5:-3]
  dates[1] = dates[1][-2:] + "/" + dates[1][-5:-3]
  echantillon = df["echantillon"].values[0]

  fig.add_annotation(
          x=0.5,
          y=1.09,
          xref="paper",
          yref="paper",
          text=f"Sondage {info_sondage} du {dates[0]} au {dates[1]}, {echantillon} interrogés<br>@GuillaumeRozier • @ElecTracker_off • Données NSPPolls",
          font=dict(size=15),
          showarrow=False
      )

  fig.write_image(f"out/violin_{df.id.values[0]}.png", engine="kaleido", width=900, height=900, scale=2)

def tweet_sondage(df):
  info_sondage = df["nom_institut"].values[0] + ", " + df["commanditaire"].values[0]
  dates = [df["debut_enquete"].values[0], df["fin_enquete"].values[0]]
  candidats = df.candidat

  tweet = "Nouveau sondage " + info_sondage + "(" + dates[1] + ") :"

  for candidat in candidats[:6]:
    intentions = df[df["candidat"] == candidat]["intentions"].values[0]
    tweet += "\n" + candidat + " : " + str(intentions) + "%"
  print(tweet)

def main():
  df, id_sondages = recuperer_donnees()
  exporter_tous_les_id_sondages(df)
  df = df[~df["id"].isin(id_sondages["id"])]

  if len(df)>0:
    for id in df.id.unique():
      df_temp = df[df["id"]==id]
      graphique_violons(df_temp)
      #tweet_sondage(df_temp)

if __name__ == '__main__':
  main()