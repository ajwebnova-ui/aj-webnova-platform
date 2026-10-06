import os
from orchestrator import AJWebnovaMaster

# Configuration
os.environ["NVIDIA_API_KEY"] = "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"
os.environ["SUPABASE_URL"] = "https://cfmfzubrapvrsiceobmd.supabase.co"
os.environ["SUPABASE_KEY"] = "sb_publishable_XKCTLJ1zAV456ms6Cp8y9A_PmTkBHZf"
os.environ["SENDER_EMAIL"] = "ajwebnova@gmail.com"
os.environ["SENDER_PASSWORD"] = "hwvg ozou bbak xdic"
os.environ["TELEGRAM_BOT_TOKEN"] = "8768774796:AAEU2WQwxVubEktojFgSSwxtO-ucAOQJymY"
os.environ["MY_TELEGRAM_CHAT_ID"] = "8615771277"

def trigger_manual_lead():
    try:
        print("🚀 Triggering manual high-ticket lead notification...")
        orchestrator = AJWebnovaMaster()

        # High-Value Target
        lead_info = {
            "business_name": "Diamond Dental Boutique",
            "website": "https://diamonddental.example.com",
            "job_description": "High-end luxury dental clinic in a wealthy district. Budget is flexible for a world-class agency.",
            "email": "contact@diamonddental.example.com",
            "budget": "50000"
        }

        # We skip the Hunter's analysis to avoid timeout and go straight to the "High Value" logic
        # We manually save to DB and send the Telegram notification.

        # 1. Save to DB
        lead_data = {
            "business_name": lead_info['business_name'],
            "website": lead_info['website'],
            "status": "PENDING_APPROVAL",
            "contact_email": lead_info['email'],
            "value_est": lead_info['budget']
        }
        db_response = orchestrator.db.save_lead(lead_data)
        lead_id = db_response.data[0]['id']
        print(f"💾 Saved lead to Supabase: {lead_id}")

        # 2. Send the Approval Buttons to Telegram
        orchestrator.telegram.send_approval_request(
            chat_id=os.getenv("MY_TELEGRAM_CHAT_ID"),
            lead_id=lead_id,
            business_name=lead_info['business_name'],
            amount=lead_info['budget']
        )
        print("\n✅ SUCCESS: Approval buttons sent to your Telegram!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    trigger_manual_lead()
