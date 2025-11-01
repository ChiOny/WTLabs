import os, json
import requests
from dotenv import load_dotenv

load_dotenv()

WEBEX_TOKEN = os.getenv("WEBEX_TOKEN", "").strip()
WEBEX_ROOMS = "https://webexapis.com/v1/rooms"
WEBEX_MESSAGES = "https://webexapis.com/v1/messages"

def webex_headers():
    if not WEBEX_TOKEN:
        raise SystemExit("ERROR: WEBEX_TOKEN missing in .env")
    return {
        "Authorization": f"Bearer {WEBEX_TOKEN}",
        "Content-Type": "application/json"
    }

def list_rooms():
    h = webex_headers()
    r = requests.get(WEBEX_ROOMS, headers=h, timeout=15)
    if r.status_code == 401:
        raise SystemExit("ERROR 401 Unauthorized: Check your Webex token.")
    r.raise_for_status()
    items = r.json().get("items", [])
    return [{"id": it["id"], "title": it.get("title",""), "type": it.get("type","")} for it in items]

def pick_room_by_title(title: str):
    for r in list_rooms():
        if r["title"].strip().lower() == title.strip().lower():
            return r
    return None

def post_message(room_id: str, text: str):
    h = webex_headers()
    payload = {"roomId": room_id, "text": text}
    r = requests.post(WEBEX_MESSAGES, headers=h, data=json.dumps(payload), timeout=15)
    if r.status_code == 401:
        raise SystemExit("ERROR 401 Unauthorized when posting message.")
    r.raise_for_status()
    return True

if __name__ == "__main__":
    print("\nYour Webex rooms:")
    rooms = list_rooms()
    for r in rooms:
        print(f"- {r['type']:<6}  {r['title']}")

    title = input("\nType the EXACT room title to post a test message: ").strip()
    room = pick_room_by_title(title)
    if not room:
        raise SystemExit("Room not found. Check the title and try again.")

    print(f"Posting to: {room['title']}")
    ok = post_message(room["id"], "Hello from Space Bot test 👋")
    print("Posted? ", "YES" if ok else "NO")

