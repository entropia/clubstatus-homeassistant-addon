#!/usr/bin/env python3
# coding=utf-8
import paho.mqtt.client as mqtt
from flask import Flask, Response, jsonify
import json, time, os, threading

debug = bool(os.getenv('DEBUG'))
mqtt_topic = str(os.getenv('MQTT_TOPIC'))
mqtt_broker = str(os.getenv('MQTT_BROKER'))
mqtt_broker_port = int(os.getenv('MQTT_BROKER_PORT'))
app = Flask(__name__)

class Clubstatus:
    def __init__(self):
        self.spaceapi_status = None
        self.spaceapi_html_status = "Unbekannt"
        self.spaceapi_output = {}
        self.spaceapi_human_output = ""

clubstatus = Clubstatus()

def on_connect(client, userdata, flags, rc):
    if debug:
        print("Connected with result code "+str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    if debug:
        print(msg.topic + " " + str(msg.payload))

    status_payload = msg.payload.decode()
    timestamp = int(time.time())

    if status_payload == "1":
        clubstatus.spaceapi_status = True
        clubstatus.spaceapi_html_status = "Offen"
    elif status_payload == "0":
        clubstatus.spaceapi_status = False
        clubstatus.spaceapi_html_status = "Geschlossen"
    else:
        clubstatus.spaceapi_status = None
        clubstatus. spaceapi_html_status = "Unbekannt"

    clubstatus.spaceapi_output = {
        "api_compatibility": ["14", "15"],
        "space": "Entropia",
        "logo": "https://entropia.de/wiki/images/e/ed/Teebeutel1_noev.png",
        "url": "https://entropia.de/",
        "location": {
            "address": "Entropia e.V., Gewerbehof Steinstraße 23, 76133 Karlsruhe, Germany, Planet Earth",
            "lat": 49.0067,
            "lon": 8.407438,
            "timezone": "Europe/Berlin",
            "country_code": "DE"
        },
        "contact": {
            "email": "info@entropia.de",
            "irc": "irc://irc.hackint.eu/#entropia",
            "issue_mail": "oops@lists.entropia.de",
            "mastodon": "@entropia@chaos.social",
            "matrix": "#entropia:entropia.de",
            "ml": "news@list.entropia.de",
            "phone": "+49 721 5604732"
        },
        "feeds": {
            "wiki": {
                "type": "html",
                "url": "https://entropia.de/Hauptseite"
            },
            "calendar": {
                "type": "html",
                "url": "https://entropia.de/Vorlage:Termine"
            }
        },
        "membership_plans": [
            {
                "billing_interval": "monthly",
                "currency": "EUR",
                "description": "Normale Mitglieder gem. https://entropia.de/Satzung_des_Vereins_Entropia_e.V.#Beitragsordnung",
                "name": "Regular Members",
                "value": 25,
            },
            {
                "billing_interval": "monthly",
                "currency": "EUR",
                "description": "Mitglieder des CCC e.V. gem. https://entropia.de/Satzung_des_Vereins_Entropia_e.V.#Beitragsordnung",
                "name": "Members of CCC e.V.",
                "value": 19,
            },
            {
                "billing_interval": "monthly",
                "currency": "EUR",
                "description": "Schüler, Studenten, Auszubildende und Menschen mit geringem Einkommen gem. https://entropia.de/Satzung_des_Vereins_Entropia_e.V.#Beitragsordnung",
                "name": "Reduced Fee Members",
                "value": 15,
            },
            {
                "billing_interval": "monthly",
                "currency": "EUR",
                "description": "Fördermitglieder gem. https://entropia.de/Satzung_des_Vereins_Entropia_e.V.#Beitragsordnung",
                "name": "Sustaining Membership",
                "value": 6,
            },
            {
                "billing_interval": "monthly",
                "currency": "EUR",
                "description": "Ehrenmitglieder gem. https://entropia.de/Satzung_des_Vereins_Entropia_e.V.#Beitragsordnung",
                "name": "Honorary Membership",
                "value": 0,
            }
        ],
        "spacefed": {
            "spacenet": False,
            "spacesaml": False
        },
        "state": {
            "icon": {
                "closed": "https://entropia.de/wiki/images/7/76/Clubstatus_zu.png",
                "open": "https://entropia.de/wiki/images/7/7a/Clubstatus_offen.png"
            },
            "lastchange": timestamp,
            "open": clubstatus.spaceapi_status,
            "message": clubstatus.spaceapi_html_status
        },
        "projects": [
            "https://entropia.de/Kategorie:Projekte",
            "https://gulas.ch/"
        ]
    }

    clubstatus.spaceapi_human_output = ("<!-- this is not meant to be machine-readable. please use /spaceapi or /status.json -->"
             "<html>"
                "<head><title>Clubstatus</title></head>"
                f"<body>{clubstatus.spaceapi_html_status}</body>"
             "</html>"
             )

    if debug:
        print(f"HTML: \n{clubstatus.spaceapi_human_output}")
        print("JSON: \n"+json.dumps(clubstatus.spaceapi_output, indent=2))


def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_broker_port)
    client.loop_forever()

thread = threading.Thread(target=mqtt_thread)
thread.daemon = True
thread.start()

@app.route("/")
def human():
    return clubstatus.spaceapi_human_output

@app.route("/spaceapi")
def spaceapi():
    # Adhere to headers recommended by https://spaceapi.io/provide-an-endpoint/#http-and-cors
    return (
        jsonify(clubstatus.spaceapi_output),
        200,
        {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json; charset=utf-8",
        }
    )

app.run(host='0.0.0.0', port=5000)
