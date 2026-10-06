import os
from orchestrator import AJWebnovaMaster

# Using the keys provided in previous turns
# For the ones missing, we will use environment variables from the system
os.environ["NVIDIA_API_KEY"] = "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"
os.environ["SUPABASE_URL"] = "https://cfmfzubrapvrsiceobmd.supabase.co"
os.environ["SUPABASE_KEY"] = "sb_publishable_XKCTLJ1zAV456ms6Cp8y9A_PmTkBHZf"
os.environ["SENDER_EMAIL"] = "ajwebnova@gmail.com"
# SENDER_PASSWORD, TELEGRAM_BOT_TOKEN, and MY_TELEGRAM_CHAT_ID must be set in the environment

def test_notification():
    try:
        orchestrator = AJWebnovaMaster()

        # Test lead
        test_lead = {
            "business_name": "🚀 TEST: Luxury Dental Clinic",
            "website": "www.testclinic.com",
            "job_description": "Looking for a high-end website redesign. Budget is very high.",
            "email": "test@client.com",
            "budget": "50000"
        }

        print("Sending test notification to Telegram...")
        result = orchestrator.process_new_lead(test_lead)
        print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_notification()
