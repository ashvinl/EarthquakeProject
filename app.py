from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    backend()
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

def backend():
    url = "https://everyearthquake.p.rapidapi.com/latestEarthquakeNearMe"

    querystring = {"latitude":"33.962523","longitude":"-118.3706975"}

    headers = {
        "X-RapidAPI-Key": "1245c0d08cmsh6048f1f2b40e429p1f824ejsnda64bb5ace07",
        "X-RapidAPI-Host": "everyearthquake.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.json)