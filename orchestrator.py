import os
from agent_engine import AJWebnovaAgent
from supabase_client import AJWebnovaDB
from telegram_payments import AJWebnovaTelegram
from mail_automation import AJWebnovaMail

class AJWebnovaMaster:
    def __init__(self):
        # Initialize all components
        # These should ideally be in a .env file
        self.agent = AJWebnovaAgent(api_key=os.getenv("NVIDIA_API_KEY"))
        self.db = AJWebnovaDB(
            url=os.getenv("SUPABASE_URL"),
            key=os.getenv("SUPABASE_KEY")
        )
        self.telegram = AJWebnovaTelegram(bot_token=os.getenv("TELEGRAM_BOT_TOKEN"))
        self.mail = AJWebnovaMail(
            email=os.getenv("SENDER_EMAIL"),
            password=os.getenv("SENDER_PASSWORD")
        )

    def process_new_lead(self, lead_info):
        """
        Full Pipeline:
        Hunt -> DB Save -> Audit -> Proposal -> Email -> Telegram Notify
        """
        print(f"🚀 Starting Pipeline for: {lead_info['business_name']}")

        # 1. HUNT: Filter the lead
        decision = self.agent.run_hunter(lead_info['job_description'])
        if "HIGH VALUE" not in decision.upper():
            print("❌ Low value lead. Skipping.")
            return {"status": "skipped", "reason": "low_value"}

        print("✅ High Value Lead Detected!")

        # 2. SAVE: Store in Supabase
        lead_data = {
            "business_name": lead_info['business_name'],
            "website": lead_info['website'],
            "status": "HIGH_VALUE",
            "contact_email": lead_info.get('email')
        }
        db_response = self.db.save_lead(lead_data)
        lead_id = db_response.data[0]['id']
        print(f"💾 Saved to Supabase. Lead ID: {lead_id}")

        # 3. ANALYZE: Run the audit
        audit_results = self.agent.run_analyst(f"Business: {lead_info['business_name']}, URL: {lead_info['website']}")
        self.db.update_lead_status(lead_id, "AUDITED")
        print("🔍 Audit completed.")

        # 4. CLOSE: Generate proposal
        proposal = self.agent.run_closer(audit_results)
        self.db.update_lead_status(lead_id, "PROPOSED")
        print("✍️ Proposal generated.")

        # 5. DELIVERY: Send Email
        if lead_info.get('email'):
            mail_sent = self.mail.send_proposal(lead_info['email'], lead_info['business_name'], proposal)
            if mail_sent:
                print("📧 Proposal emailed to client!")

        # 6. NOTIFY: Alert Vikas via Telegram
        msg = (
            f"💰 <b>New High-Ticket Lead Processed!</b>\n\n"
            f"<b>Client:</b> {lead_info['business_name']}\n"
            f"<b>Status:</b> Proposal Sent\n"
            f"<b>Lead ID:</b> {lead_id}\n\n"
            f"Check your Supabase dashboard for details."
        )
        self.telegram.send_message(os.getenv("MY_TELEGRAM_CHAT_ID"), msg)
        print("📱 Telegram notification sent.")

        return {"status": "success", "lead_id": lead_id}

if __name__ == "__main__":
    # Example Lead
    example_lead = {
        "business_name": "Global Tech Solutions",
        "website": "www.globaltech.com",
        "job_description": "We are looking for a top-tier agency to rebuild our enterprise portal. Budget is flexible for the right expert.",
        "email": "contact@globaltech.com"
    }

    orchestrator = AJWebnovaMaster()
    orchestrator.process_new_lead(example_lead)
