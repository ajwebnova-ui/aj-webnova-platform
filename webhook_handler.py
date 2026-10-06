import os
import requests
from flask import Flask, request, jsonify
from orchestrator import AJWebnovaMaster

app = Flask(__name__)

# Global orchestrator instance
orchestrator = None

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        print("--- INITIALIZING ORCHESTRATOR ---")
        try:
            orchestrator = AJWebnovaMaster()
            print("--- ORCHESTRATOR INITIALIZED SUCCESSFULLY ---")
        except Exception as e:
            print(f"--- CRITICAL ERROR initializing AJWebnovaMaster: {e} ---")
            return None
    return orchestrator

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    print(f"RECEIVED WEBHOOK: {update}")

    if not update:
        return jsonify({"status": "no_data"}), 400

    # 1. Handle Text Messages (to get Chat ID)
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        print(f"Message received from chat {chat_id}")

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("ERROR: TELEGRAM_BOT_TOKEN not found in environment")
            return jsonify({"status": "config_error"}), 500

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"✅ Connection Established!\n\nYour numeric Chat ID is: <code>{chat_id}</code>\n\nPlease copy this number and send it to me so I can launch the automation!",
            "parse_mode": "HTML"
        }
        requests.post(url, json=payload)
        return jsonify({"status": "id_sent"})

    # 2. Handle Button Clicks (Callback Queries)
    if "callback_query" in update:
        callback_query = update["callback_query"]
        data = callback_query["data"]
        chat_id = callback_query["message"]["chat"]["id"]
        callback_id = callback_query["id"]

        print(f"Callback received: {data} from chat {chat_id}")

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("ERROR: TELEGRAM_BOT_TOKEN not found in environment")
            return jsonify({"status": "config_error"}), 500

        # IMMEDIATELY respond to Telegram to stop the spinner
        try:
            answer_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
            requests.post(answer_url, json={
                "callback_query_id": callback_id,
                "text": "Processing your request... please wait a moment. 🚀"
            })
            print("Successfully sent 'Processing...' response to Telegram.")
        except Exception as e:
            print(f"Failed to send answerCallbackQuery: {e}")

        if data.startswith("approve_"):
            lead_id = data.replace("approve_", "")
            print(f"Processing approval for lead: {lead_id}")

            master = get_orchestrator()
            if master:
                try:
                    result = master.handle_approval(lead_id, approved=True)
                    print(f"Orchestrator result: {result}")
                    return jsonify({"status": "success", "message": result})
                except Exception as e:
                    print(f"Error in handle_approval: {e}")
                    return jsonify({"status": "error", "message": str(e)}), 500
            else:
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
