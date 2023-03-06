from flask import Flask, render_template, redirect, url_for

import requests
import json
import math
import gmplot

import os
from twilio.rest import Client

from googleplaces import GooglePlaces, types, lang
import geopy
from geopy import distance

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
    url = "https://everyearthquake.p.rapidapi.com/recentEarthquakes"

    querystring = {"interval":"P1Y2M3W4DT1H2M3S","start":"1","count":"100","type":"earthquake","latitude":"33.962523","longitude":"-118.3706975","radius":"1000","units":"miles","magnitude":"3","intensity":"1"}

    headers = {
        "X-RapidAPI-Key": "1245c0d08cmsh6048f1f2b40e429p1f824ejsnda64bb5ace07",
        "X-RapidAPI-Host": "everyearthquake.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    data = json.loads(response.text)

    return data

def isThereAnEarthquake() -> bool:
    data = getEarthquakeData()
    return True

def radius() -> int:
    data = getEarthquakeData()

    if (isThereAnEarthquake()):
        magnitude = data["data"][0]["magnitude"]
        radius = math.exp(float(magnitude)/1.01-0.13)*1000
    else:    
        radius = 0

    return round(radius/10000,2)

def sendText():
    account_sid = "AC5a09a73cf0869ab2188548ca49051f08"
    auth_token  = "e06acb334821144e809a1c2195128872"
    client = Client(account_sid, auth_token)
    data = get_location()
    message = client.messages.create(
        body="\n\nHelp! I need emergency services. I am located at Latitude: " + str(data["latitude"]) + " and Longitude: " + str(data["longitude"]),
        from_="+18888235205",
        to="+19256405709"
    )

def getHospitalLink(hospital):
        dir = "https://www.google.com/maps/place/"
        strHosp = hospital
        strHosp = strHosp.replace(" ", "+")

        return dir + strHosp

def isInRadius():
    data = get_location()
    earth = getEarthquakeData()
    coords_1 = (data["latitude"], data["longitude"])
    coords_2 = (earth["latitude"], earth["longitude"])
    dist = distance.distance(coords_1, coords_2).km
    if(radius() > dist):
        return True
    return True

def getHospitals():
    google_places = GooglePlaces('AIzaSyAcHJq-yfKqAqJfCoPlfU-ZWlqL5DJp_rw')
    data = get_location()
    # call the function nearby search with
    # the parameters as longitude, latitude,
    # radius and type of place which needs to be searched of 
    # type can be HOSPITAL, CAFE, BAR, CASINO, etc
    query_result = google_places.nearby_search(
            lat_lng ={'lat': data["latitude"], 'lng': data["longitude"]},
            #lat_lng ={'lat': 28.4089, 'lng': 77.3178},
            radius = 8000,
            # types =[types.TYPE_HOSPITAL] or
            # [types.TYPE_CAFE] or [type.TYPE_BAR]
            # or [type.TYPE_CASINO])
            types =[types.TYPE_HOSPITAL])
    
    # If any attributions related 
    # with search results print them
    # if query_result.has_attributions:
    #     print (query_result.html_attributions)
    
    hospitalList = []

    count = 0
    # Iterate over the search results
    for place in query_result.places:
        tempArr = []
        tempArr.append(place.name)
        data = get_location()
        coords_1 = (data["latitude"], data["longitude"])
        coords_2 = (place.geo_location['lat'], place.geo_location['lng'])
        dist = distance.distance(coords_1, coords_2).km
        tempArr.append(round(dist, 2))
        tempArr.append(getHospitalLink(place.name))
        hospitalList.append(tempArr)

    hospitalList.sort(key=lambda x:x[1])

    return hospitalList

@app.route("/", methods=["POST", "GET"])
def index():

    text = radius()
    hospitals = getHospitals()
    return render_template("index.html", sentHelp=False, text=text, hospitals=hospitals)

@app.route("/help")
def help():
    sendText()
    text = radius()
    hospitals = getHospitals()
    return render_template("index.html", sentHelp=True, text=text, hospitals=hospitals)

@app.route("/info")
def info():
    return render_template("info.html")

if __name__ == "__main__":
    app.run(debug=True)

