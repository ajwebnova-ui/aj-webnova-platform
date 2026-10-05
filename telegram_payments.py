import os
import requests

class AJWebnovaTelegram:
    def __init__(self, bot_token=None):
        self.token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("Telegram Bot Token is missing! Set TELEGRAM_BOT_TOKEN env var.")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id, text):
        """Sends a professional update to the owner or client."""
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        return requests.post(url, json=payload).json()

    def create_payment_invoice(self, chat_id, title, description, price_amount, currency="USD"):
        """
        Sends a payment invoice.
        Note: For real payments, you must configure a provider in @BotFather.
        """
        url = f"{self.base_url}/sendInvoice"
        payload = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": "aj_webnova_payment",
            "provider_token": os.getenv("TELEGRAM_PAYMENT_PROVIDER_TOKEN"), # Configured via BotFather
            "currency": currency,
            "prices": [{"label": title, "amount": price_amount}] # amount is in smallest unit (cents)
        }
        return requests.post(url, json=payload).json()

    def check_payment_status(self, update_json):
        """Processes payment updates from the Telegram webhook."""
        # This would be called by a webhook handler
        if "payment" in update_json:
            return f"Payment received for {update_json['payment']['order_id']}"
        return "No payment update."
