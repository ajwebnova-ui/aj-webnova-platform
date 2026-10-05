import os
import requests

class AJWebnovaTelegram:
    def __init__(self, bot_token=None):
        self.token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("Telegram Bot Token is missing! Set TELEGRAM_BOT_TOKEN env var.")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id, text):
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        return requests.post(url, json=payload).json()

    def send_approval_request(self, chat_id, lead_id, business_name, amount):
        url = f"{self.base_url}/sendMessage"
        text = (
            f"💰 <b>High-Ticket Lead Found!</b>\n\n"
            f"<b>Client:</b> {business_name}\n"
            f"<b>Est. Value:</b> {amount}\n"
            f"<b>Lead ID:</b> <code>{lead_id}</code>\n\n"
            f"Do you want to trigger the Analyst Agent and send a proposal?"
        )
        keyboard = {
            "inline_keyboard": [[
                {"text": "Approve ✅", "callback_data": f"approve_{lead_id}"},
                {"text": "Reject ❌", "callback_data": f"reject_{lead_id}"}
            ]]
        }
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_markup": keyboard}
        return requests.post(url, json=payload).json()

    def send_invoice_notification(self, chat_id, business_name, amount):
        """Notifies the owner that an invoice was sent."""
        text = (
            f"💸 <b>Invoice Sent!</b>\n\n"
            f"An invoice of <b>{amount}</strong> has been sent to <b>{business_name}</b>.\n"
            f"Payment Method: UPI (8792496494@super)\n\n"
            f"I will notify you the moment payment is confirmed."
        )
        return self.send_message(chat_id, text)
