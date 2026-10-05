import os
from agent_engine import AJWebnovaAgent

# 1. Configuration
# Replace with your actual key or set it in your environment variables
API_KEY = "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"

def main():
    print("🚀 AJ Webnova AI Growth Engine Starting...\n")

    try:
        agent = AJWebnovaAgent(api_key=API_KEY)
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return

    # --- TEST CASE: A POTENTIAL HIGH-TICKET CLIENT ---
    client_lead = {
        "business_name": "Elite Dental Clinic",
        "website": "www.elitedental.com",
        "job_description": "Looking for a professional redesign of our clinic website to attract more high-end patients. We have a budget for quality work."
    }

    print(f"🔍 Processing Lead: {client_lead['business_name']}...")

    # STEP 1: The Hunter - Is this lead worth 20k+?
    print("\n--- [1] HUNTER AGENT FILTERING ---")
    is_worthy = agent.run_hunter(client_lead['job_description'])
    print(f"Decision: {is_worthy}")

    if "HIGH VALUE" in is_worthy.upper():
        # STEP 2: The Analyst - Find the "Money Leaks"
        print("\n--- [2] ANALYST AGENT AUDITING ---")
        audit = agent.run_analyst(f"Business: {client_lead['business_name']}, URL: {client_lead['website']}")
        print(f"Audit Findings:\n{audit}")

        # STEP 3: The Closer - Create the 20k+ Proposal
        print("\n--- [3] CLOSER AGENT PROPOSING ---")
        proposal = agent.run_closer(audit)
        print(f"Final Proposal:\n{proposal}")

        print("\n✅ Workflow Complete. Send this proposal to the client immediately!")
    else:
        print("\n❌ Lead flagged as LOW VALUE. Skipping to save time.")

if __name__ == "__main__":
    main()
