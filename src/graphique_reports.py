import os
from plotly import graph_objects as go
import json
import numpy as np
from datetime import datetime, timedelta


class Graphique():

    def __init__(self):
        with open('data/output/intentionsCandidatsLoessReportsVoix.json', 'r') as file:
            self.donnees_json = json.load(file)

    def switch_hypothese(self, hypothese: str):
        self.candidats = []
        self.intentions = []
        self.donnees = self.donnees_json["hypotheses"][hypothese]
        for idx, choix_T2 in enumerate(self.donnees["candidats"]):
            self.intentions += [round(self.donnees["candidats"][choix_T2]["intentions"]["valeur"][-1], 1)]
            self.candidats += [choix_T2]

        idx_sorted = np.argsort(self.intentions )
        self.intentions = np.array(self.intentions)[idx_sorted]
        self.candidats = np.array(self.candidats)[idx_sorted]

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
        
    def plot(self, title_suffix="", candidat_T1="", couleur_candidat_T1="black"):
        fig = go.Figure()
        annotations = []

        date_max_graphique = datetime.strptime(max(self.donnees["candidats"][self.candidats[0]]["intentions"]["fin_enquete"]), "%Y-%m-%d")
        temps_max_graphique = date_max_graphique + timedelta(days=15)

        for candidat in self.candidats:
            y = self.donnees["candidats"][candidat]["intentions_loess"]["valeur"]
            color = self.donnees["candidats"][candidat]["couleur"]

            fig.add_trace(
                go.Scatter(
                    x=self.donnees["candidats"][candidat]["intentions_loess"]["fin_enquete"],
                    y=y,
                    name = candidat,
                    line = {"color": color, "width": 50, "shape": 'spline'},
                    legendgroup = candidat,
                    opacity=0.15,
                    mode = 'lines',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x = self.donnees["candidats"][candidat]["intentions"]["fin_enquete"],
                    y = self.donnees["candidats"][candidat]["intentions"]["valeur"],
                    name = candidat,
                    marker = {"size": 8, "color": color},
                    legendgroup = candidat,
                    mode = 'markers',
                    opacity = 0.8,
                )
            )

            # fig.add_trace(
            #     go.Scatter(
            #         x = [self.donnees["candidats"][candidat]["intentions_loess"]["fin_enquete"][-1]],
            #         y = [y[-1]],
            #         mode = 'markers+text',
            #         text = "", #candidat + " (" + str(round(y[-1], 1)) + "%)",
            #         textfont = {"color": color, "size": 20},
            #         textposition = 'middle right',
            #         marker = {"color": color, "size": 8},
            #         legendgroup = candidat,
            #         showlegend = False  
            #     )
            # )
            if y[-1]>0.5:
                annotations += [
                    {
                        "x": self.donnees["candidats"][candidat]["intentions_loess"]["fin_enquete"][-1],
                        "y": y[-1],
                        "text": candidat + " (" + str(round(y[-1], 2)) + "%)",
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
            if (diff) < 3:
                #annotations[-idx-1]["ay"] = 1 #max(1-diff, 0)
                annotations[idx+1]["ayref"] = "y"
                annotations[idx+1]["yref"] = "y"
                annotations[idx+1]["ay"] = annotations[idx+1]["y"] + max(3-diff, 0) #max(1-diff, 0)


        fig.update_layout(
            showlegend = False,
            margin = {"t": 80, "r": 20, "l": 50, "b": 30},
            legend = {"orientation": "h"},
            yaxis = {
            "ticksuffix": "%",
            "range": [0, 100]
            },
            xaxis = {
            "range": ["2022-04-09", temps_max_graphique] 
            },
            shapes = [
            {
                "type": 'line',
                "x0": "2022-04-10",
                "y0": 0,
                "x1": "2022-04-10",
                "y1": 100,
                "line":{
                    "color": 'rgb(0, 0, 0)',
                    "width": 1,
                    "dash":'dot'
                }
            },
            {
                "type": 'line',
                "x0": "2022-04-24",
                "y0": 0,
                "x1": "2022-04-24",
                "y1": 100,
                "line":{
                    "color": 'rgb(0, 0, 0)',
                    "width": 1,
                    "dash":'dot'
                }
            },
            {
                "type": 'line',
                "x0": "2022-01-01",
                "y0": 50,
                "x1": temps_max_graphique,
                "y1": 50,
                "line":{
                    "color": 'rgb(0, 0, 0.5)',
                    "width": 1,
                }
            }
            ],
        )

        annotations_other = [
            {
                "x": "2022-04-10",
                "y": 97,
                "text": "1er Tour",
                "xanchor": "right",
                "ax": -30,
                "ay": 0,
                "showarrow": True,
                "arrowsize": 0.8
            },
            {
                "x": "2022-04-24",
                "y": 97,
                "text": "2ème Tour",
                "xanchor": "left",
                "ax": +30,
                "ay": 0,
                "showarrow": True,
                "arrowsize": 0.8
            },
            {
                "x": 0.5,
                "y": 1.1,
                "xref": "paper",
                "yref": "paper",
                "text": f"Intention de vote au 2nd tour des électeurs <b>{candidat_T1}</b> du 1er tour",
                "font": {"size": 25, "color": couleur_candidat_T1},
                "xanchor": "center",
                "showarrow": False,
            },
            {
                "x": 0.5,
                "y": 1.05,
                "xref": "paper",
                "yref": "paper",
                "text": f"Aggrégation de l'ensemble des sondages (Ipsos, Ifop, Opinionway...) • @ElecTracker • electracker.fr • Données NSPPolls • dernier sondage : {self.donnees['candidats'][candidat]['intentions']['fin_enquete'][-1]}",
                "font": {"size": 15},
                "xanchor": "center",
                "showarrow": False,
            }
            ]

        for annotation in annotations:
            fig.add_annotation(annotation)

        for annotation in annotations_other:
            fig.add_annotation(annotation)

        fig.write_image(f"img/plot_presidentielles_deuxieme_tour_reports{title_suffix}.png", width=1200, height=800, scale=2)

graphique = Graphique()

graphique.switch_hypothese("Jean-Luc Mélenchon")
graphique.plot(title_suffix="_melenchon", candidat_T1="Jean-Luc Mélenchon", couleur_candidat_T1=graphique.donnees["couleur"])

graphique.switch_hypothese("Yannick Jadot")
graphique.plot(title_suffix="_jadot", candidat_T1="Yannick Jadot", couleur_candidat_T1=graphique.donnees["couleur"])

graphique.switch_hypothese("Valérie Pécresse")
graphique.plot(title_suffix="_pecresse", candidat_T1="Valérie Pécresse", couleur_candidat_T1=graphique.donnees["couleur"])

graphique.switch_hypothese("Eric Zemmour")
graphique.plot(title_suffix="_zemmour", candidat_T1="Éric Zemmour", couleur_candidat_T1=graphique.donnees["couleur"])

graphique.switch_hypothese("Marine Le Pen")
graphique.plot(title_suffix="_lepen", candidat_T1="Marine Le Pen", couleur_candidat_T1=graphique.donnees["couleur"])

graphique.switch_hypothese("Emmanuel Macron")
graphique.plot(title_suffix="_macron", candidat_T1="Emmanuel Macron", couleur_candidat_T1=graphique.donnees["couleur"])

graphique.switch_hypothese("Abstebtion")
graphique.plot(title_suffix="_abstention", candidat_T1="Abstention", couleur_candidat_T1=graphique.donnees["couleur"])

#graphique.switch_hypothese("Hypothèse Mélenchon / Le Pen")
#graphique.plot(title_suffix="_macron_lepen")
