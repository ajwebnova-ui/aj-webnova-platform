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
        self.upi_id = "8792496494@super"
        self.owner_email = os.getenv("SENDER_EMAIL")

    def process_new_lead(self, lead_info):
        """
        Pipeline: Hunt -> DB Save -> Telegram Approval
        """
        decision = self.agent.run_hunter(lead_info['job_description'])
        if "HIGH VALUE" not in decision.upper():
            return {"status": "skipped", "reason": "low_value"}

        lead_data = {
            "business_name": lead_info['business_name'],
            "website": lead_info['website'],
            "status": "PENDING_APPROVAL",
            "contact_email": lead_info.get('email'),
            "value_est": lead_info.get('budget', '20000')
        }
        db_response = self.db.save_lead(lead_data)
        lead_id = db_response.data[0]['id']

        self.telegram.send_approval_request(
            chat_id=os.getenv("MY_TELEGRAM_CHAT_ID"),
            lead_id=lead_id,
            business_name=lead_info['business_name'],
            amount=lead_info.get('budget', '20,000')
        )
        return {"status": "awaiting_approval", "lead_id": lead_id}

    def handle_approval(self, lead_id, approved=True):
        """
        The "Action" logic for Telegram buttons.
        """
        res = self.db.supabase.table("leads").select("*").eq("id", lead_id).single().execute()
        lead = res.data

        if not approved:
            # 1. Update DB
            self.db.update_lead_status(lead_id, "REJECTED")
            # 2. Notify Vikas via Telegram
            self.telegram.send_message(os.getenv("MY_TELEGRAM_CHAT_ID"), f"❌ Lead {lead['business_name']} rejected.")
            # 3. Notify Vikas via Email
            self.mail.send_internal_notification(
                self.owner_email,
                "Lead Rejected",
                f"You have rejected the lead: {lead['business_name']}. It has been marked as REJECTED in the database."
            )
            return "Rejected"

        # --- APPROVED WORKFLOW ---
        # 1. Audit the site
        audit_results = self.agent.run_analyst(f"Business: {lead['business_name']}, URL: {lead['website']}")
        self.db.update_lead_status(lead_id, "AUDITED")

        # 2. Generate high-ticket proposal
        proposal = self.agent.run_closer(audit_results)
        self.db.update_lead_status(lead_id, "PROPOSED")

        # 3. Send Proposal to Client
        if lead.get('contact_email'):
            self.mail.send_proposal(lead['contact_email'], lead['business_name'], proposal)

        # 4. Send Invoice with UPI ID to Client
        if lead.get('contact_email'):
            self.mail.send_invoice(
                lead['contact_email'],
                lead['business_name'],
                lead.get('value_est', '20,000'),
                self.upi_id
            )

        # 5. Final Notification to Vikas (Telegram & Email)
        self.telegram.send_invoice_notification(
            os.getenv("MY_TELEGRAM_CHAT_ID"),
            lead['business_name'],
            lead.get('value_est', '20,000')
        )
        self.mail.send_internal_notification(
            self.owner_email,
            "Automation Complete",
            f"High-Ticket Automation finished for {lead['business_name']}.\n\n- Audit completed.\n- Proposal sent.\n- Invoice with UPI (8792496494@super) sent."
        )

        return "Automation Complete"

if __name__ == "__main__":
    # Test lead for confirmation
    example_lead = {
        "business_name": "Test Luxury Clinic",
        "website": "www.testclinic.com",
        "job_description": "Looking for a high-end website redesign for our clinic.",
        "email": "test@client.com",
        "budget": "25000"
    }
    orchestrator = AJWebnovaMaster()
    orchestrator.process_new_lead(example_lead)
