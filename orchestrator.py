import os
import threading
from agent_engine import AJWebnovaAgent
from supabase_client import AJWebnovaDB
from telegram_payments import AJWebnovaTelegram
from mail_automation import AJWebnovaMail

class AJWebnovaMaster:
    def __init__(self):
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

    def _get_agent(self):
        return AJWebnovaAgent(api_key=os.getenv("NVIDIA_API_KEY"))

    def get_live_metrics(self):
        hunter_res = self.db.supabase.table("leads").select("id", count="exact").execute()
        analyst_res = self.db.supabase.table("leads").select("id", count="exact").eq("status", "AUDITED").execute()
        closer_res = self.db.supabase.table("leads").select("id", count="exact").eq("status", "PROPOSED").execute()
        value_res = self.db.supabase.table("leads").select("value_est").execute()
        total_value = sum([float(item.get('value_est', 0)) for item in value_res.data])

        return {
            "hunter_count": hunter_res.count,
            "analyst_count": analyst_res.count,
            "closer_count": closer_res.count,
            "total_value": total_value
        }

    def process_new_lead(self, lead_info):
        agent = self._get_agent()
        decision = agent.run_hunter(lead_info['job_description'])

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
        lead_id = db_//_response.data[0]['id']

        self.telegram.send_approval_request(
            chat_id=os.getenv("MY_TELEGRAM_CHAT_ID"),
            lead_id=lead_id,
            business_name=lead_info['business_name'],
            amount=lead_info.get('budget', '20,000')
        )
        return {"status": "awaiting_approval", "lead_id": lead_id}

    def handle_approval(self, lead_id, approved=True):
        # This function now starts a BACKGROUND THREAD
        # This allows the server to respond to Telegram INSTANTLY
        # while the AI works in the background.

        if not approved:
            self.db.update_lead_status(lead_id, "REJECTED")
            self.telegram.send_message(os.getenv("MY_TELEGRAM_CHAT_ID"), f"❌ Lead {lead_id} rejected.")
            self.mail.send_internal_notification(self.owner_email, "Lead Rejected", f"Rejected lead {lead_id}.")
            return "Rejected"

        # Start background processing
        thread = threading.Thread(target=self._run_ai_pipeline, args=(lead_id,))
        thread.start()

        return "Processing in background..."

    def _run_ai_pipeline(self, lead_id):
        """The heavy lifting happens here, in the background."""
        try:
            res = self.db.supabase.table("leads").select("*").eq("id", lead_id).single().execute()
            lead = res.data
            agent = self._get_agent()

            # 1. Audit
            audit_results = agent.run_analyst(f"Business: {lead['business_name']}, URL: {lead['website']}")
            self.db.update_lead_status(lead_id, "AUDITED")

            # 2. Proposal
            proposal = agent.run_closer(audit_results)
            self.db.update_lead_status(lead_id, "PROPOSED")

            # 3. Delivery
            if lead.get('contact_email'):
                self.mail.send_proposal(lead['contact_email'], lead['business_name'], proposal)
                self.mail.send_invoice(lead['contact_email'], lead['business_name'], lead.get('value_est', '20,000'), self.upi_id)

            # 4. Notify Owner
            self.telegram.send_invoice_notification(os.getenv("MY_TELEGRAM_CHAT_ID"), lead['business_name'], lead.get('value_est', '20,000'))
            self.mail.send_internal_notification(self.owner_email, "Automation Complete", f"High-Ticket Automation finished for {lead['business_name']}.")

        except Exception as e:
            self.telegram.send_message(os.getenv("MY_TELEGRAM_CHAT_ID"), f"⚠️ AI Error for lead {lead_id}: {str(e)}")
