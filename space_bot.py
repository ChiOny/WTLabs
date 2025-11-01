import os, json, re, time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# --------- Setup / config ---------
load_dotenv()

WEBEX_TOKEN = os.getenv("WEBEX_TOKEN", "").strip()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY", "").strip()

WEBEX_ROOMS = "https://webexapis.com/v1/rooms"
WEBEX_MESSAGES = "https://webexapis.com/v1/messages"

OPEN_NOTIFY_URL = "http://api.open-notify.org/iss-now.json"       # primary (can be flaky)
WTIA_URL = "https://api.wheretheiss.at/v1/satellites/25544"       # fallback
OWM_REVERSE_URL = "https://api.openweathermap.org/geo/1.0/reverse"

# --------- Helpers ---------
def webex_headers():
    if not WEBEX_TOKEN:
        raise SystemExit("ERROR: WEBEX_TOKEN missing in .env")
    return {
        "Authorization": f"Bearer {WEBEX_TOKEN}",
        "Content-Type": "application/json"
    }

def list_rooms():
    r = requests.get(WEBEX_ROOMS, headers=webex_headers(), timeout=15)
    if r.status_code == 401:
        raise SystemExit("ERROR 401 Unauthorized: refresh your Webex token.")
    r.raise_for_status()
    return [{"id": it["id"], "title": it.get("title",""), "type": it.get("type","")} for it in r.json().get("items", [])]

def pick_room_by_title(title: str):
    for r in list_rooms():
        if r["title"].strip().lower() == title.strip().lower():
            return r
    return None

def latest_message(room_id: str):
    """Return (message_id, text) of the latest message in room (or (None, ''))."""
    params = {"roomId": room_id, "max": 1}
    r = requests.get(WEBEX_MESSAGES, headers=webex_headers(), params=params, timeout=15)
    if r.status_code == 401:
        raise SystemExit("ERROR 401 Unauthorized when reading messages.")
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None, ""
    msg = items[0]
    return msg.get("id"), (msg.get("text") or "").strip()

def post_message(room_id: str, text: str):
    payload = {"roomId": room_id, "text": text}
    r = requests.post(WEBEX_MESSAGES, headers=webex_headers(), data=json.dumps(payload), timeout=15)
    if r.status_code == 401:
        raise SystemExit("ERROR 401 Unauthorized when posting message.")
    r.raise_for_status()
    return True

# --------- ISS + reverse geocode ---------
def try_open_notify(timeout=6):
    r = requests.get(OPEN_NOTIFY_URL, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    ts = int(data["timestamp"])
    lat = float(data["iss_position"]["latitude"])
    lon = float(data["iss_position"]["longitude"])
    return ts, lat, lon

def try_where_the_iss_at(timeout=8):
    r = requests.get(WTIA_URL, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    ts = int(data["timestamp"])
    lat = float(data["latitude"])
    lon = float(data["longitude"])
    return ts, lat, lon

def get_iss_now_resilient():
    # 2 short attempts primary
    for i in range(2):
        try:
            return try_open_notify(timeout=6)
        except Exception:
            time.sleep(0.8)
    # 2 attempts fallback
    for i in range(2):
        try:
            return try_where_the_iss_at(timeout=8)
        except Exception:
            time.sleep(0.8)
    raise RuntimeError("Both ISS providers failed")

def reverse_geocode(lat: float, lon: float) -> str:
    if not OPENWEATHER_KEY:
        return "(No OPENWEATHER_KEY in .env)"
    params = {"lat": lat, "lon": lon, "limit": 1, "appid": OPENWEATHER_KEY}
    r = requests.get(OWM_REVERSE_URL, params=params, timeout=10)
    try:
        r.raise_for_status()
        arr = r.json()
    except Exception:
        return "(geocode error)"
    if not arr:
        return "(over ocean)"
    item = arr[0]
    parts = [item.get("name"), item.get("state"), item.get("country")]
    parts = [p for p in parts if p]
    return ", ".join(parts) if parts else "(no name)"

# --------- Main loop ---------
def main():
    # 1) Show rooms and pick one
    print("Your Webex rooms:")
    rooms = list_rooms()
    for r in rooms:
        print(f"- {r['type']:<6}  {r['title']}")
    title = input("\nType the EXACT room title to monitor (for messages like /5): ").strip()
    room = pick_room_by_title(title)
    if not room:
        raise SystemExit("Room not found. Re-run and pick a printed title.")

    room_id = room["id"]
    print(f"Monitoring: {room['title']}. Type /5 in that room to test.")

    last_seen_id = None
    while True:
        try:
            msg_id, text = latest_message(room_id)
            if msg_id and msg_id != last_seen_id:
                last_seen_id = msg_id
                print(f"Latest: {text}")

                m = re.match(r"^/(\d+)\s*$", text)
                if m:
                    delay = int(m.group(1))
                    # safety cap: 0..300 seconds
                    delay = max(0, min(delay, 300))
                    time.sleep(delay)
                    ts, lat, lon = get_iss_now_resilient()
                    human = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%a %b %d %H:%M:%S %Y UTC")
                    place = reverse_geocode(lat, lon)
                    reply = f"On {human}, the ISS was over {place}. ({lat:.4f}°, {lon:.4f}°)"
                    post_message(room_id, reply)
                    print("Posted response.")

            time.sleep(1)  # polite polling
        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except requests.HTTPError as e:
            # 429 or temporary errors → wait a bit
            print(f"HTTP error: {e}. Waiting 10s.")
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}. Waiting 5s.")
            time.sleep(5)

if __name__ == "__main__":
    main()
