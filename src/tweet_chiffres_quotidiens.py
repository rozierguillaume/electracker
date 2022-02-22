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

def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def tweet_intentions(message):
    try:
        api = twitter_api()
        filename = 'img/plot_presidentielles.png'
        tweet = api.update_status_with_media(status=message, filename=filename)
        print("Tweeted")
        return tweet
    except Exception as e:
        print("Error Tweet")
        print(e)

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
    message = "Moyenne sondages (10 jours) : \n"

    for idx in range(1, len(candidats)+1):
        candidat = candidats[-idx]
        ligne = "  " + str(idx) + ". " + candidat + " : " + str(intentions[-idx]) + "%\n"

        if(len(message)+len(ligne)<250):
            message += ligne

    message += "electracker.fr"
    message = message[:270]
    return message, candidats

def get_message_evolution_intentions(candidats):
    message = "Évolution sur 14 jours : \n"

    for idx in range(1, len(candidats)+1):
        candidat = candidats[-idx]
        intentions = donnees["candidats"][candidat]["intentions_moy_14d"]["valeur"]
        evol_intentions = intentions[-1] - intentions[-14-1]
        
        suffix=""
        if idx == 1:
            suffix=" points"
        ligne = "  " + str(idx) + ". " + candidat + " : " + printable_taux(evol_intentions) + suffix +"\n"

        if(len(message)+len(ligne)<250):
            message += ligne

    message += "electracker.fr"
    message = message[:270]
    return message

def export_table_html(candidats):
    table_html = ""

    def title(text):
        return f"<h3>{text} • {round(donnees['candidats'][candidat]['intentions_moy_14d']['valeur'][-1], 1)}%</h3>"

    def ligne_sondage(liste):
        text = ""
        for sondage in liste:
            text += f" {liste[sondage]['intentions']}% • (intervalle : {liste[sondage]['erreur_inf']}% - {liste[sondage]['erreur_sup']}%) • {liste[sondage]['nom_institut']} {liste[sondage]['commanditaire']} • Du {liste[sondage]['debut_enquete']} au {liste[sondage]['fin_enquete']}"
            text += "<br>"
        return text


    for candidat in candidats:
        table_html += title(candidat)
        table_html += ligne_sondage(derniers_sondages[candidat]["derniers_sondages"])
        table_html += "<br>"

    with open('html/derniers_sondages.html', 'w') as f:
        f.write(table_html)

message, candidats_sorted = get_message_intentions()
message_evolution = get_message_evolution_intentions(candidats_sorted)
export_table_html(candidats_sorted)
print(message)
print(message_evolution)
original_tweet = tweet_intentions(message)
second_tweet = tweet_evolution(message_evolution, original_tweet)
