import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

def get_iss_location():
    url = "http://api.open-notify.org/iss-now.json"
    response = requests.get(url)
    data = response.json()

    position = data["iss_position"]
    latitude = position["latitude"]
    longitude = position["longitude"]
    timestamp = data["timestamp"]

    readable_time = datetime.utcfromtimestamp(timestamp).strftime("%a %b %d %H:%M:%S %Y UTC")
    print(f"\n🛰️  At {readable_time}, the ISS was at Latitude: {latitude}, Longitude: {longitude}")
    return float(latitude), float(longitude)

def reverse_geocode(lat, lon):
    url = "http://api.openweathermap.org/geo/1.0/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "limit": 1,
        "appid": OPENWEATHER_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if len(data) == 0:
        return "Over an ocean or unknown location"

    location = data[0]
    name = location.get("name", "")
    country = location.get("country", "")
    state = location.get("state", "")
    place = ", ".join(filter(None, [name, state, country]))
    return place

if __name__ == "__main__":
    lat, lon = get_iss_location()
    place = reverse_geocode(lat, lon)
    print(f"🌍  The ISS is currently flying over: {place}")


