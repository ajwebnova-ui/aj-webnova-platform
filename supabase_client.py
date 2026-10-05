import os
from supabase import create_client, Client

class AJWebnovaDB:
    def __init__(self, url=None, key=None):
        # Use provided keys or environment variables
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError("Supabase URL and Key are required! Set SUPABASE_URL and SUPABASE_KEY env vars.")

        self.supabase: Client = create_client(self.url, self.key)

    def save_lead(self, lead_data):
        """Saves a new lead identified by the Hunter Agent."""
        # Table 'leads' should have columns: business_name, website, status, value_est
        return self.supabase.table("leads").insert(lead_data).execute()

    def update_lead_status(self, lead_id, status):
        """Updates lead status (e.g., 'Audited', 'Proposed', 'Closed')."""
        return self.supabase.table("leads").update({"status": status}).eq("id", lead_id).execute()

    def get_high_value_leads(self):
        """Retrieves leads flagged as HIGH VALUE."""
        return self.supabase.table("leads").select("*").eq("status", "HIGH_VALUE").execute()
