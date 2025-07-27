import os
import random

import requests
from flask import Flask
from prometheus_client import make_wsgi_app, Counter, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
DEFAULT_CITY = "BOGOTA"
WEATHER_API = "https://api.weatherapi.com/v1"
# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})


# Define prometheus metrics
REQUEST_COUNTER = Counter(
    "app_requests_total", "Total number of requests to the app", ["endpoint"]
)
RANDOM_NUMBER_GAUGE = Gauge("app_random_number", "Current value of the random number")


@app.route("/current")
def current():
    api_key = os.getenv("WEATHER_API_KEY")
    endpoint = f"{WEATHER_API}/current.json"
    params = {"key": api_key, "q": DEFAULT_CITY, "aqi": "no"}
    r = requests.get(endpoint, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Error API", r)


@app.route("/")
def index():
    # Increment the request counter
    REQUEST_COUNTER.labels(endpoint="/").inc()

    random_number = random.randint(a=0, b=100)

    # Set the random number gauge
    RANDOM_NUMBER_GAUGE.set(random_number)

    return {"status": "ok", "random_number": random_number}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
