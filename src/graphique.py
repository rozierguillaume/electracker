import os
from plotly import graph_objects as go
import json
import numpy as np
from datetime import datetime, timedelta

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

with open('data/output/intentionsCandidatsMoyenneMobile14Jours.json', 'r') as file:
    donnees = json.load(file)

with open('data/output/derniersSondagesCandidats.json', 'r') as file:
    derniers_sondages = json.load(file)

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
        if y[-1]>0.5:
            annotations += [
                {
                    "x": donnees["candidats"][candidat]["intentions_moy_14d"]["fin_enquete"][-1],
                    "y": y[-1],
                    "text": candidat + " (" + str(round(y[-1], 1)) + "%)",
                    "font": {"color": color, "size": 20},
                    "xanchor": "left",
                    "yanchor": "middle",
                    "ax": 30,
                    "ay": max(0.8, y[-1]),
                    "yref": "y",
                    "ayref": "y"
                }
            ]

    for idx in range(0, len(annotations)-1):
        annotation = annotations[idx] # Macron
        annotation_prev = annotations[idx+1] # MLP
        diff = - annotation["ay"] + annotation_prev["ay"]
        if (diff) < 1:
            #annotations[-idx-1]["ay"] = 1 #max(1-diff, 0)
            annotations[idx+1]["ayref"] = "y"
            annotations[idx+1]["yref"] = "y"
            annotations[idx+1]["ay"] = annotations[idx+1]["y"] + max(1-diff, 0) #max(1-diff, 0)

    date_max_graphique = datetime.strptime(max(donnees["candidats"][candidat]["intentions_moy_14d"]["fin_enquete"]), "%Y-%m-%d")
    temps_max_graphique = date_max_graphique + timedelta(days=70)

    fig.update_layout(
        showlegend = False,
        margin = {"t": 80, "r": 20, "l": 50, "b": 30},
        legend = {"orientation": "h"},
        yaxis = {
          "ticksuffix": "%",
          "range": [0, 35]
        },
        xaxis = {
          "range": ["2021-10-01", temps_max_graphique] 
        },
        shapes = [
          {
              "type": 'line',
              "x0": "2022-04-10",
              "y0": 0,
              "x1": "2022-04-10",
              "y1": 35,
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
            "y": 34,
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
            "text": f"Aggrégation de l'ensemble des sondages (Ipsos, Ifop, Opinionway...) • @ElecTracker • electracker.fr • Données NSPPolls • dernier sondage : {donnees['candidats'][candidat]['intentions_moy_14d']['fin_enquete'][-1]}",
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

plot()
