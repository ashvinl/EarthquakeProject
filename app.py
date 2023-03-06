from flask import Flask, render_template, redirect, url_for

import requests
import json
import math

import os
from twilio.rest import Client

app = Flask(__name__)

sentHelp = False

def get_ip() -> str:
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "longitude": response.get("longitude"),
        "latitude": response.get("latitude")
    }
    return location_data

def getEarthquakeData():
    url = "https://everyearthquake.p.rapidapi.com/latestEarthquakeNearMe"

    longitude = get_location()["longitude"]
    latitude = get_location()["latitude"]

    querystring = {"latitude":longitude,"longitude": latitude}

    headers = {
        "X-RapidAPI-Key": "1245c0d08cmsh6048f1f2b40e429p1f824ejsnda64bb5ace07",
        "X-RapidAPI-Host": "everyearthquake.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    data = json.loads(response.text)

    return data

def isThereAnEarthquake() -> bool:
    data = getEarthquakeData()
    return data["errorCode"] != "none"

def radius() -> int:
    data = getEarthquakeData()

    if (isThereAnEarthquake()):
        magnitude = data["data"][0]["title"][1:5]
        radius = math.exp(float(magnitude)/1.01-0.13)*1000
    else:    
        radius = 0

    return radius

def sendText():
    account_sid = "AC5a09a73cf0869ab2188548ca49051f08"
    auth_token  = "4e8a065cf7d9764863f85de2e69e9252"
    client = Client(account_sid, auth_token)
    data = get_location()
    message = client.messages.create(
        body="Help! I need emergency services. I am located at Latitude: " + str(data["latitude"]) + " and Longitude: " + str(data["longitude"]),
        from_="+18888235205",
        to="+19256405709"
    )
    sentHelp = True

@app.route("/", methods=["POST", "GET"])
def index():
    text = radius()
    return render_template("index.html", sentHelp=sentHelp, text=text)

@app.route("/help")
def help():
    sendText()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

