import os
from flask import Flask, request, jsonify
from orchestrator import AJWebnovaMaster

app = Flask(__name__)
orchestrator = AJWebnovaMaster()

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()

    # Handle Text Messages (to get Chat ID)
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        import requests
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

        if data.startswith("approve_"):
            lead_id = data.replace("approve_", "")
            result = orchestrator.handle_approval(lead_id, approved=True)
            return jsonify({"status": "success", "message": result})

        elif data.startswith("reject_"):
            lead_id = data.replace("reject_", "")
            result = orchestrator.handle_approval(lead_id, approved=False)
            return jsonify({"status": "success", "message": result})

    return jsonify({"status": "ignored"})

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """
    API endpoint for the Dashboard to fetch live analytics.
    """
    try:
        metrics = orchestrator.get_live_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
