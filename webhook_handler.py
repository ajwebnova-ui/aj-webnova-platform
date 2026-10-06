import os
from flask import Flask, request, jsonify
from orchestrator import AJWebnovaMaster
import requests

app = Flask(__name__)

# Initialize orchestrator lazily to prevent crash on startup if env vars are missing
orchestrator = None

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        try:
            orchestrator = AJWebnovaMaster()
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to initialize AJWebnovaMaster: {e}")
            return None
    return orchestrator

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()

    # Handle Text Messages (to get Chat ID)
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"✅ Connection Established!\n\nYour numeric Chat ID is: <code>{chat_id}</code>\n\nPlease copy this number and send it to me so I can launch the automation!",
            "parse_mode": "HTML"
        }
        requests.post(url, json=payload)
        return jsonify({"status": "id_sent"})

    # Handle Button Clicks
    if "callback_query" in update:
        callback_query = update["callback_query"]
        data = callback_query["data"]
        chat_id = callback_query["message"]["chat"]["id"]

        # Respond to Telegram immediately to stop the loading spinner
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={
            "callback_query_id": callback_query["id"],
            "text": "Processing your request... please wait a moment. 🚀"
        })

        if data.startswith("approve_"):
            lead_id = data.replace("approve_", "")
            master = get_orchestrator()
            if master:
                result = master.handle_approval(lead_id, approved=True)
                return jsonify({"status": "success", "message": result})
            return jsonify({"status": "error", "message": "AI Engine not initialized"}), 500

        elif data.startswith("reject_"):
            lead_id = data.replace("reject_", "")
            master = get_orchestrator()
            if master:
                result = master.handle_approval(lead_id, approved=False)
                return jsonify({"status": "success", "message": result})
            return jsonify({"status": "error", "message": "AI Engine not initialized"}), 500

    return jsonify({"status": "ignored"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "AJ Webnova AI is awake!"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
