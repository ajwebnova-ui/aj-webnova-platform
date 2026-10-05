import os
from agent_engine import AJWebnovaAgent
from supabase_client import AJWebnovaDB
from telegram_payments import AJWebnovaTelegram
from mail_automation import AJWebnovaMail

class AJWebnovaMaster:
    def __init__(self):
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
        NEW AUTOMATED PIPELINE:
        Hunt -> DB Save -> Telegram Approval (Buttons) -> [User Click] -> Audit -> Proposal -> Email
        """
        print(f"🚀 Starting Pipeline for: {lead_info['business_name']}")

        # 1. HUNT: Filter the lead
        decision = self.agent.run_hunter(lead_info['job_description'])
        if "HIGH VALUE" not in decision.upper():
            print("❌ Low value lead. Skipping.")
            return {"status": "skipped", "reason": "low_value"}

        print("✅ High Value Lead Detected!")

        # 2. SAVE: Store in Supabase as 'PENDING_APPROVAL'
        lead_data = {
            "business_name": lead_info['business_name'],
            "website": lead_info['website'],
            "status": "PENDING_APPROVAL",
            "contact_email": lead_info.get('email'),
            "value_est": lead_info.get('budget', '20000')
        }
        db_response = self.db.save_lead(lead_data)
        lead_id = db_response.data[0]['id']
        print(f"💾 Saved to Supabase. Lead ID: {lead_id}")

        # 3. APPROVAL: Send Interactive Buttons to Vikas
        # Instead of just a message, we send Approve/Reject buttons.
        self.telegram.send_approval_request(
            chat_id=os.getenv("MY_TELEGRAM_CHAT_ID"),
            lead_id=lead_id,
            business_name=lead_info['business_name'],
            amount=lead_info.get('budget', '20,000')
        )
        print("📱 Approval request sent to Telegram with buttons.")

        return {"status": "awaiting_approval", "lead_id": lead_id}

    def handle_approval(self, lead_id, approved=True):
        """
        This is called when you click the 'Approve' button in Telegram.
        It triggers the rest of the automation.
        """
        if not approved:
            self.db.update_lead_status(lead_id, "REJECTED")
            self.telegram.send_message(os.getenv("MY_TELEGRAM_CHAT_ID"), f"❌ Lead {lead_id} rejected.")
            return "Rejected"

        # --- THE FULL AUTOMATION TRIGGER ---
        # Fetch lead details from DB
        res = self.db.supabase.table("leads").select("*").eq("id", lead_id).single().execute()
        lead = res.data

        print(f"🚀 Approval received for {lead['business_name']}. Running AI Agents...")

        # 1. ANALYZE: Run the audit
        audit_results = self.agent.run_analyst(f"Business: {lead['business_name']}, URL: {lead['website']}")
        self.db.update_lead_status(lead_id, "AUDITED")

        # 2. CLOSE: Generate proposal
        proposal = self.agent.run_closer(audit_results)
        self.db.update_lead_status(lead_id, "PROPOSED")

        # 3. DELIVERY: Send Email
        if lead.get('contact_email'):
            self.mail.send_proposal(lead['contact_email'], lead['business_name'], proposal)

        # 4. NOTIFY: Alert Vikas that the work is done
        self.telegram.send_message(
            os.getenv("MY_TELEGRAM_CHAT_ID"),
            f"✅ <b>Automation Complete!</b>\n\nAudit and Proposal sent to {lead['business_name']}.<br>Lead ID: {lead_id}",
            # Note: send_message needs to handle parse_mode='HTML' which it does in our tool
        )

        return "Automation Complete"

if __name__ == "__main__":
    # Test Lead
    example_lead = {
        "business_name": "Luxury Dental Clinic",
        "website": "www.luxurydental.com",
        "job_description": "Looking for a high-end website to attract premium patients.",
        "email": "contact@luxurydental.com",
        "budget": "25000"
    }

    orchestrator = AJWebnovaMaster()
    orchestrator.process_new_lead(example_lead)
