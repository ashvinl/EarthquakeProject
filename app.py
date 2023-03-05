from flask import Flask, render_template

import requests
import json
import math
import gmplot

app = Flask(__name__)

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

def plot_map():
    lats = get_location()
    gmap = gmplot.GoogleMapPlotter(lats["latitude"], lats["longitude"], 13)
    gmap.circle(lats["latitude"], lats["longitude"], radius())
    gmap.draw("bob.html")

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


@app.route("/", methods=["POST", "GET"])
def index():
    text = radius()
    return render_template("index.html", text=text)

if __name__ == "__main__":
    app.run(debug=True)

