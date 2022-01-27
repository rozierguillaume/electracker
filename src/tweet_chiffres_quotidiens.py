import tweepy
import os
from plotly import graph_objects as go
import json
from urllib.request import urlopen
import numpy as np

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
print(CONSUMER_KEY)
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
ACCESS_SECRET = os.environ.get('ACCESS_SECRET')

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

url = 'https://raw.githubusercontent.com/rozierguillaume/electracker/main/data/output/intentionsCandidatsMoyenneMobile14Jours.json'
donnees = json.loads(urlopen(url).read())

def plot():
    fig = go.Figure()
    for candidat in donnees["candidats"]:
        y = donnees["candidats"][candidat]["intentions_moy_14d"]["valeur"]
        y_sup = donnees["candidats"][candidat]["intentions_moy_14d"]["erreur_sup"]
        y_inf = donnees["candidats"][candidat]["intentions_moy_14d"]["erreur_inf"]
        color = donnees["candidats"][candidat]["couleur"]

        fig.add_trace(
            go.Scatter(
                x=donnees["candidats"][candidat]["intentions_moy_14d"]["fin_enquete"],
                y=y,
                name = candidat,
                line = {"color": color, "width": 3, "shape": 'spline'},
                legendgroup = candidat,
                mode = 'lines',
            )
        )

        fig.add_trace(
            go.Scatter(
                x = donnees["candidats"][candidat]["intentions"]["fin_enquete"],
                y = donnees["candidats"][candidat]["intentions"]["valeur"],
                name = candidat,
                marker = {"size": 4, "color": color},
                legendgroup = candidat,
                mode = 'markers',
                opacity = 0.2,
            )
        )

        fig.add_trace(
            go.Scatter(
                x = donnees["candidats"][candidat]["intentions_moy_14d"]["fin_enquete"],
                y = y_sup,
                name = candidat,
                line = {"color": color, "width": 0, "shape": "spline"},
                legendgroup = candidat,
                mode = 'lines',
            )
        )

        fig.add_trace(
            go.Scatter(
                x = donnees["candidats"][candidat]["intentions_moy_14d"]["fin_enquete"],
                y = y_inf,
                name = candidat,
                line = {"color": color, "width": 0, "shape": 'spline'},
                legendgroup = candidat,
                fill = 'tonexty',
                fillcolor = "rgba" + str(hex_to_rgb(color) + (0.12,)),
                mode = 'lines',
            )
        )

        fig.add_trace(
            go.Scatter(
                x = [donnees["candidats"][candidat]["intentions_moy_14d"]["fin_enquete"][-1]],
                y = [y[-1]],
                mode = 'markers+text',
                text = candidat + " (" + str(round(y[-1], 1)) + "%)",
                textfont = {"color": color},
                textposition = 'middle right',
                marker = {"color": color, "size": 10},
                legendgroup = candidat,
                showlegend = False  
            )
        )

    fig.update_layout(
        showlegend = False,
        margin = {"t": 80, "r": 20, "l": 50, "b": 30},
        legend = {"orientation": "h"},
        yaxis = {
          "ticksuffix": "%",
          "range": [0, 30]
        },
        xaxis = {
          "range": ["2021-10-01", "2022-04-14"] 
        },
        shapes = [
          {
              "type": 'line',
              "x0": "2022-04-10",
              "y0": 0,
              "x1": "2022-04-10",
              "y1": 30,
              "line":{
                  "color": 'rgb(0, 0, 0)',
                  "width": 2,
                  "dash":'dot'
              }
          }
        ],
        annotations = [
          {
            "x": "2022-04-10",
            "y": 29,
            "text": "1er Tour",
            "xanchor": "right",
            "ax": -30,
            "ay": 0,
            "showarrow": True,
            "arrowsize": 0.8
          },
          {
            "x": 0.5,
            "y": 1.1,
            "xref": "paper",
            "yref": "paper",
            "text": "Sondages de l'élection présidentielle 2022",
            "font": {"size": 25},
            "xanchor": "center",
            "showarrow": False,
          },
          {
            "x": 0.5,
            "y": 1.05,
            "xref": "paper",
            "yref": "paper",
            "text": "Aggrégation de l'ensemble des sondages • @ElecTracker • electracker.fr",
            "font": {"size": 15},
            "xanchor": "center",
            "showarrow": False,
          }
        ]
    )

    fig.write_image("img/plot_presidentielles.png", width=1200, height=800, scale=2)
    

def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def tweet_image(message):
    try:
        api = twitter_api()
        filename = 'img/plot_presidentielles.png'
        api.update_with_media(filename, status=message)
        print("Tweeted")
    except:
        print("Error Tweet")

def get_message():
    message = "Moyenne sondages #Présidentielle2022 (14j) : \n"

    candidats = []
    intentions = []
    for idx, candidat in enumerate(donnees["candidats"]):
        intentions += [round(donnees["candidats"][candidat]["intentions_moy_14d"]["valeur"][-1], 1)]
        candidats += [candidat]
    
    idx_sorted = np.argsort(intentions )
    intentions = np.array(intentions)[idx_sorted]
    candidats = np.array(candidats)[idx_sorted]

    for idx in range(1, len(candidats)+1):
        candidat = candidats[-idx]
        if(len(message)<240):
            message += "  " + str(idx) + ". " + candidat + " : " + str(intentions[-idx]) + "%\n"
    message += "electracker.fr"
    return message

plot()
message = get_message()
#tweet_image(message)