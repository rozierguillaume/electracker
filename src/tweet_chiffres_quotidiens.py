import tweepy
import os
from plotly import graph_objects as go
import json
from urllib.request import urlopen
import numpy as np

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_KEY = os.getenv('ACCESS_KEY')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

url = 'https://raw.githubusercontent.com/rozierguillaume/electracker/main/data/output/intentionsCandidatsMoyenneMobile14Jours.json'
donnees = json.loads(urlopen(url).read())

candidats = []
intentions = []
for idx, candidat in enumerate(donnees["candidats"]):
    intentions += [round(donnees["candidats"][candidat]["intentions_moy_14d"]["valeur"][-1], 1)]
    candidats += [candidat]

idx_sorted = np.argsort(intentions )
intentions = np.array(intentions)[idx_sorted]
candidats = np.array(candidats)[idx_sorted]
    
def plot():
    fig = go.Figure()
    annotations = []

    for candidat in candidats:
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
                text = "", #candidat + " (" + str(round(y[-1], 1)) + "%)",
                textfont = {"color": color, "size": 20},
                textposition = 'middle right',
                marker = {"color": color, "size": 15},
                legendgroup = candidat,
                showlegend = False  
            )
        )

        annotations += [
            {
                "x": donnees["candidats"][candidat]["intentions_moy_14d"]["fin_enquete"][-1],
                "y": y[-1],
                "text": candidat + " (" + str(round(y[-1], 1)) + "%)",
                "font": {"color": color, "size": 20},
                "xanchor": "left",
                "yanchor": "middle",
                "ax": 30,
                "ay": 0
            }
        ]

    for idx in range(1, len(annotations)):
        annotation = annotations[-idx]
        annotation_prev = annotations[-idx-1]

        if (annotation["y"] + annotation["ay"] - annotation_prev["y"] - annotation_prev["ay"]) < 1:
            annotations[-idx-1]["ay"] = 15

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
    )

    annotations_other = [
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

    for annotation in annotations:
        fig.add_annotation(annotation)

    for annotation in annotations_other:
        fig.add_annotation(annotation)

    fig.write_image("img/plot_presidentielles.png", width=1200, height=800, scale=2)
    

def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def tweet_intentions(message):
    try:
        api = twitter_api()
        filename = 'img/plot_presidentielles.png'
        tweet = api.update_with_media(filename, status=message)
        print("Tweeted")
        return tweet
    except:
        print("Error Tweet")

def tweet_evolution(message, previous):
    try:
        api = twitter_api()
        tweet = api.update_status(status=message, in_reply_to_status_id=previous.id)
        print("Tweeted")
        return tweet
    except:
        print("Error Tweet")

def printable_taux(evol_intentions):
    taux_str = ""
    if evol_intentions > 0.5:
        taux_str = "↗️  +" + str(round(evol_intentions, 1))
    elif evol_intentions < -0.5:
        taux_str = "↘️  " + str(round(evol_intentions, 1))
    elif evol_intentions < 0:
        taux_str = "➡️  " + str(round(evol_intentions, 1))
    else:
        taux_str = "➡️  +" + str(round(evol_intentions, 1))
    return taux_str


def get_message_intentions():
    message = "Moyenne sondages (14 jours) : \n"

    for idx in range(1, len(candidats)+1):
        candidat = candidats[-idx]
        if(len(message)<240):
            message += "  " + str(idx) + ". " + candidat + " : " + str(intentions[-idx]) + "%\n"
    message += "electracker.fr"
    return message, candidats

def get_message_evolution_intentions(candidats):
    message = "Évolution sur 14 jours : \n"

    for idx in range(1, len(candidats)+1):
        candidat = candidats[-idx]
        intentions = donnees["candidats"][candidat]["intentions_moy_14d"]["valeur"]
        evol_intentions = intentions[-1] - intentions[-14-1]
        if(len(message)<240):
            suffix=""
            if idx == 1:
                suffix=" points"

            message += "  " + str(idx) + ". " + candidat + " : " + printable_taux(evol_intentions) + suffix +"\n"
    message += "electracker.fr"
    return message

def export_table_html(candidats):
    table_html = ""

    def title(text):
        return f"<h3>{text} • {donnees["candidats"][candidat]["intentions_moy_14d"]["valeur"]}%</h3>"

    def ligne_sondage(donnees_candidat):
        return donnees_candidat[]


    for candidat in candidats:
        table_html += title(candidat)
        table_html += ligne_sondage(donnees["candidats"][candidat])

plot()
message, candidats_sorted = get_message_intentions()
message_evolution = get_message_evolution_intentions(candidats_sorted)
export_table_html(candidats_sorted)

#original_tweet = tweet_intentions(message)
#second_tweet = tweet_evolution(message_evolution, original_tweet)