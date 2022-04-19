import os
from plotly import graph_objects as go
import json
import numpy as np
from datetime import datetime, timedelta


class Graphique():

    def __init__(self):
        with open('data/output/intentionsCandidatsMoyenneMobile14JoursLoessDeuxiemeTour.json', 'r') as file:
            self.donnees_json = json.load(file)

    def switch_hypothese(self, hypothese: str):
        print(hypothese)
        self.candidats = []
        self.intentions = []
        self.donnees = self.donnees_json["hypotheses"][hypothese]

        for idx, candidat in enumerate(self.donnees["candidats"]):
            self.intentions += [round(self.donnees["candidats"][candidat]["intentions_loess"]["valeur"][-1], 1)]
            self.candidats += [candidat]

        idx_sorted = np.argsort(self.intentions )
        self.intentions = np.array(self.intentions)[idx_sorted]
        self.candidats = np.array(self.candidats)[idx_sorted]

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
        
    def plot(self, title_suffix="", zoom=False):
        fig = go.Figure()
        annotations = []

        date_max_graphique = datetime.strptime(max(self.donnees["candidats"][self.candidats[0]]["intentions_loess"]["fin_enquete"]), "%Y-%m-%d")
        temps_max_graphique = date_max_graphique + timedelta(days=50)
        for candidat in self.candidats:
            y = self.donnees["candidats"][candidat]["intentions_loess"]["valeur"]
            y_sup = self.donnees["candidats"][candidat]["intentions_loess"]["erreur_sup"]
            y_inf = self.donnees["candidats"][candidat]["intentions_loess"]["erreur_inf"]
            color = self.donnees["candidats"][candidat]["couleur"]

            fig.add_trace(
                go.Scatter(
                    x=self.donnees["candidats"][candidat]["intentions_loess"]["fin_enquete"],
                    y=y,
                    name = candidat,
                    line = {"color": color, "width": 3, "shape": 'spline'},
                    legendgroup = candidat,
                    mode = 'lines',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x = self.donnees["candidats"][candidat]["intentions"]["fin_enquete"],
                    y = self.donnees["candidats"][candidat]["intentions"]["valeur"],
                    name = candidat,
                    marker = {"size": 4, "color": color},
                    legendgroup = candidat,
                    mode = 'markers',
                    opacity = 0.3,
                )
            )

            fig.add_trace(
                go.Scatter(
                    x = self.donnees["candidats"][candidat]["intentions_loess"]["fin_enquete"],
                    y = y_sup,
                    name = candidat,
                    line = {"color": color, "width": 0, "shape": "spline"},
                    legendgroup = candidat,
                    mode = 'lines',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x = self.donnees["candidats"][candidat]["intentions_loess"]["fin_enquete"],
                    y = y_inf,
                    name = candidat,
                    line = {"color": color, "width": 0, "shape": 'spline'},
                    legendgroup = candidat,
                    fill = 'tonexty',
                    fillcolor = "rgba" + str(self.hex_to_rgb(color) + (0.18,)),
                    mode = 'lines',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x = [self.donnees["candidats"][candidat]["intentions_loess"]["fin_enquete"][-1]],
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
                        "x": self.donnees["candidats"][candidat]["intentions_loess"]["fin_enquete"][-1],
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

        fig.add_trace(
                go.Scatter(
                    x = ["2022-04-24", "2022-04-24"],
                    y = [33.9, 66.1],
                    mode = 'markers+text',
                    name = "Score 2017",
                    text=["  Résultat 2017 (33.9%)", "  Résultat 2017 (66.1%)"],
                    textfont = {"color": "rgba(0, 0, 0, 1)", "size": 10},
                    marker_symbol="x-thin",
                    textposition = 'middle right',
                    marker = {"color": "black", "size": 15, "line_color": "black", "line_width": 2},
                    legendgroup = "score 2017",
                    opacity=0.3,
                    showlegend = False  
                )
            )
            

        range_yaxis = [0, 100]
        if zoom:
            range_yaxis=[35, 65]

        fig.update_layout(
            showlegend = False,
            margin = {"t": 80, "r": 20, "l": 50, "b": 30},
            legend = {"orientation": "h"},
            yaxis = {
            "ticksuffix": "%",
            "range": range_yaxis
            },
            xaxis = {
            "range": ["2022-01-01", temps_max_graphique] 
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
                "text": "Sondages de l'élection présidentielle 2022 • Deuxième tour",
                "font": {"size": 25},
                "xanchor": "center",
                "showarrow": False,
            },
            {
                "x": 0.5,
                "y": 1.05,
                "xref": "paper",
                "yref": "paper",
                "text": f"Aggrégation de l'ensemble des sondages (Ipsos, Ifop, Opinionway...) • @ElecTracker • electracker.fr • Données NSPPolls • dernier sondage : {self.donnees['candidats'][candidat]['intentions_loess']['fin_enquete'][-1]}",
                "font": {"size": 15},
                "xanchor": "center",
                "showarrow": False,
            }
            ]

        for annotation in annotations:
            fig.add_annotation(annotation)

        for annotation in annotations_other:
            fig.add_annotation(annotation)

        fig.write_image(f"img/plot_presidentielles_deuxieme_tour{title_suffix}.png", width=1200, height=800, scale=2)

graphique = Graphique()

graphique.switch_hypothese("Hypothèse Macron / Le Pen")
graphique.plot(title_suffix="_macron_lepen")

#graphique.switch_hypothese("Hypothèse Macron / Mélenchon")
graphique.plot(title_suffix="_macron_lepen_zoom", zoom=True)

#graphique.switch_hypothese("Hypothèse Macron / Zemmour")
#graphique.plot(title_suffix="_macron_zemmour")

#graphique.switch_hypothese("Hypothèse Mélenchon / Le Pen")
#graphique.plot(title_suffix="_macron_lepen")
