import os
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load .env
load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY", "").strip()
print("DEBUG: OPENWEATHER_KEY loaded?", "YES" if OPENWEATHER_KEY else "NO")

# Providers
OPEN_NOTIFY_URL = "http://api.open-notify.org/iss-now.json"  # sometimes slow/down
WTIA_URL = "https://api.wheretheiss.at/v1/satellites/25544"  # fallback (no key)

OWM_REVERSE_URL = "https://api.openweathermap.org/geo/1.0/reverse"

def try_open_notify(timeout=6):
    """Try the Open Notify ISS endpoint."""
    r = requests.get(OPEN_NOTIFY_URL, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    ts = int(data["timestamp"])
    lat = float(data["iss_position"]["latitude"])
    lon = float(data["iss_position"]["longitude"])
    return ts, lat, lon

def try_where_the_iss_at(timeout=6):
    """Fallback: WhereTheISS.at endpoint."""
    r = requests.get(WTIA_URL, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    # returns: latitude, longitude, timestamp
    ts = int(data["timestamp"])
    lat = float(data["latitude"])
    lon = float(data["longitude"])
    return ts, lat, lon

def get_iss_now():
    """Resilient fetch: Open-Notify first, then WTIA fallback, with brief retry."""
    # first attempt Open-Notify (2 quick tries)
    for i in range(2):
        try:
            return try_open_notify(timeout=6)
        except Exception as e:
            if i == 0:
                time.sleep(1.0)  # brief pause then retry
            else:
                break
    # fallback to WhereTheISS.at
    for i in range(2):
        try:
            return try_where_the_iss_at(timeout=8)
        except Exception as e:
            if i == 0:
                time.sleep(1.0)
            else:
                raise  # bubble up after failing both tries

def reverse_geocode(lat: float, lon: float) -> str:
    if not OPENWEATHER_KEY:
        return "(No OPENWEATHER_KEY in .env)"
    params = {"lat": lat, "lon": lon, "limit": 1, "appid": OPENWEATHER_KEY}
    r = requests.get(OWM_REVERSE_URL, params=params, timeout=10)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        return f"(geocode HTTP {r.status_code}: {r.text[:120]})"
    try:
        arr = r.json()
    except ValueError:
        return "(geocode: non-JSON response)"
    if not arr:
        return "(no location found — likely over ocean)"
    item = arr[0]
    name = item.get("name")
    state = item.get("state")
    country = item.get("country")
    parts = [p for p in [name, state, country] if p]
    return ", ".join(parts) if parts else "(no name returned)"

if __name__ == "__main__":
    try:
        ts, lat, lon = get_iss_now()
        human = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%a %b %d %H:%M:%S %Y UTC")
        print(f"🛰️  At {human}, the ISS was at ({lat:.4f}, {lon:.4f})")
        place = reverse_geocode(lat, lon)
        print(f"🌍  Reverse geocode: {place}")
    except Exception as e:
        print(f"ERROR getting ISS data: {e}")
