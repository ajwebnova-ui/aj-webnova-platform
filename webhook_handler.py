import os
from flask import Flask, request, jsonify
from orchestrator import AJWebnovaMaster

app = Flask(__name__)
orchestrator = AJWebnovaMaster()

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """
    This is the 'Ear' of your business.
    It listens for the button clicks (Approve/Reject) from Telegram.
    """
    update = request.get_json()

    # Check if this is a callback query (button click)
    if "callback_query" in update:
        callback_query = update["callback_query"]
        data = callback_query["data"] # e.g., "approve_uuid-123" or "reject_uuid-123"
        chat_id = callback_query["message"]["chat"]["id"]

        if data.startswith("approve_"):
            lead_id = data.replace("approve_", "")
            result = orchestrator.handle_approval(lead_id, approved=True)

            # Respond back to the user in Telegram
            # We can use a simple API call here to tell them "Done"
            # orchestrator.telegram.send_message(chat_id, "✅ Approval received! Starting AI Automation...")
            return jsonify({"status": "success", "message": result})

        elif data.startswith("reject_"):
            lead_id = data.replace("reject_", "")
            result = orchestrator.handle_approval(lead_id, approved=False)
            return jsonify({"status": "success", "message": result})

    return jsonify({"status": "ignored"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
