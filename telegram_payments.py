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

    def send_approval_request(self, chat_id, lead_id, business_name, amount):
        """
        Sends a lead approval request with INTERACTIVE BUTTONS.
        Buttons: [Approve ✅] [Reject ❌]
        """
        url = f"{self.base_url}/sendMessage"

        text = (
            f"💰 <b>High-Ticket Lead Found!</b>\n\n"
            f"<b>Client:</b> {business_name}\n"
            f"<b>Est. Value:</b> {amount}\n"
            f"<b>Lead ID:</b> <code>{lead_id}</code>\n\n"
            f"Do you want to trigger the Analyst Agent and send a proposal?"
        )

        # Inline keyboard for Approve/Reject
        keyboard = {
            "inline_keyboard": [[
                {"text": "Approve ✅", "callback_data": f"approve_{lead_id}"},
                {"text": "Reject ❌", "callback_data": f"reject_{lead_id}"}
            ]]
        }

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        }
        return requests.post(url, json=payload).json()

    def create_payment_invoice(self, chat_id, title, description, price_amount, currency="USD"):
        url = f"{self.base_url}/sendInvoice"
        payload = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": "aj_webnova_payment",
            "provider_token": os.getenv("TELEGRAM_PAYMENT_PROVIDER_TOKEN"),
            "currency": currency,
            "prices": [{"label": title, "amount": price_amount}]
        }
        return requests.post(url, json=payload).json()
