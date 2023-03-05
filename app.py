from flask import Flask, render_template

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import WebDriverWait
import time
import requests
import json
import math

app = Flask(__name__)

def backend():
    url = "https://everyearthquake.p.rapidapi.com/latestEarthquakeNearMe"

    loc = getLocation()

    querystring = {"latitude":str(loc.latitude),"longitude": str(loc.longitude)}

    headers = {
        "X-RapidAPI-Key": "1245c0d08cmsh6048f1f2b40e429p1f824ejsnda64bb5ace07",
        "X-RapidAPI-Host": "everyearthquake.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    data = json.loads(response.text)

    magnitude = data["data"][0]["title"][1:5]
    radius = math.exp(float(magnitude)/1.01-0.13)*1000

    return radius


@app.route("/", methods=["POST", "GET"])
def index():
    text = backend()
    return render_template("index.html", text=text)

if __name__ == "__main__":
    app.run(debug=True)

def getLocation():
    options = Options()
    options.add_argument("--use--fake-ui-for-media-stream")
    driver = webdriver.Chrome(executable_path = './chromedriver.exe',options=options) #Edit path of chromedriver accordingly

    timeout = 20
    driver.get("https://mycurrentlocation.net/")
    wait = WebDriverWait(driver, timeout)
    time.sleep(3)

    longitude = driver.find_elements_by_xpath('//*[@id="longitude"]') #Replace with any XPath    
    longitude = [x.text for x in longitude]    
    longitude = str(longitude[0])    
    latitude = driver.find_elements_by_xpath('//*[@id="latitude"]')    
    latitude = [x.text for x in latitude]    
    latitude = str(latitude[0])    
    driver.quit()    
    return (latitude,longitude)