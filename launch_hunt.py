import os
from orchestrator import AJWebnovaMaster

# Environment Configuration
os.environ["NVIDIA_API_KEY"] = "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"
os.environ["SUPABASE_URL"] = "https://cfmfzubrapvrsiceobmd.supabase.co"
os.environ["SUPABASE_KEY"] = "sb_publishable_XKCTLJ1zAV456ms6Cp8y9A_PmTkBHZf"
os.environ["SENDER_EMAIL"] = "ajwebnova@gmail.com"
os.environ["SENDER_PASSWORD"] = "hwvg ozou bbak xdic"
os.environ["TELEGRAM_BOT_TOKEN"] = "8768774796:AAEU2WQwxVubEktojFgSSwxtO-ucAOQJymY"
os.environ["MY_TELEGRAM_CHAT_ID"] = "8615771277"

def launch_first_hunt():
    try:
        print("🚀 Launching the first high-ticket hunt...")
        orchestrator = AJWebnovaMaster()

        # Targeted High-Ticket Lead: Luxury Dental/Aesthetics
        # In a real scenario, the Hunter Agent finds this via WebSearch.
        # For this first test, we are feeding the system a high-value target.
        test_lead = {
            "business_name": "Elite Aura Dental Studio",
            "website": "https://www.eliteauradental.example.com",
            "job_description": "We are a luxury dental clinic specializing in porcelain veneers and full-mouth reconstructions. We need a website that reflects our premium pricing and attracts high-net-worth individuals. Budget is flexible for a world-class design.",
            "email": "contact@eliteauradental.example.com",
            "budget": "45000"
        }

        print(f"Targeting: {test_lead['business_name']}...")
        result = orchestrator.process_new_lead(test_lead)

        if result.get("status") == "awaiting_approval":
            print("\n✅ SUCCESS!")
            print("The Hunter Agent has found the lead and saved it to Supabase.")
            print("The approval request has been sent to your Telegram.")
            print("\n👉 CHECK YOUR TELEGRAM NOW! You should see the [Approve ✅] button.")
        else:
            print(f"Unexpected result: {result}")

    except Exception as e:
        print(f"❌ Error during hunt: {e}")

if __name__ == "__main__":
    launch_first_hunt()
