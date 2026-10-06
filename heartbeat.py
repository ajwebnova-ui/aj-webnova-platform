import requests
import os

def send_heartbeat():
    TOKEN = "8768774796:AAEU2WQwxVubEktojFgSSwxtO-ucAOQJymY"
    CHAT_ID = "8615771277"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    text = "💓 <b>AJ Webnova Heartbeat Check</b>\n\nI am awake and listening! If you clicked a button and nothing happened, it is because the server was 'sleeping'. Try clicking it one more time now!"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Heartbeat sent!")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_heartbeat()
