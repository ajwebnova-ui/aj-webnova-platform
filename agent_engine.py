import os
from openai import OpenAI

class AJWebnovaAgent:
    def __init__(self, api_key=None):
        # Use provided key or look for environment variable for security
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is missing! Please provide it or set NVIDIA_API_KEY env var.")

        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )
        self.model = "z-ai/glm-5.3-flash"

    def generate_response(self, system_prompt, user_input, temperature=0.7):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=temperature,
            max_tokens=2048
        )
        return completion.choices[0].message.content

    # --- SPECIALIZED AGENT PERSONAS ---

    def run_analyst(self, website_details):
        """Agent: The Auditor. Finds flaws in client websites to create urgency."""
        system_prompt = (
            "You are the Lead Technical Auditor at AJ Webnova. Your goal is to find 3 critical "
            "conversion killers on a client's website. Be professional, blunt, and focus on "
            "how these flaws are losing the client money. Use business terminology (ROI, Bounce Rate, LTV)."
        )
        return self.generate_response(system_prompt, f"Analyze this website/business: {website_details}")

    def run_closer(self, audit_results):
        """Agent: The Sales Closer. Turns the audit into a high-ticket proposal."""
        system_prompt = (
            "You are a High-Ticket Sales Closer for AJ Webnova. You take technical flaws and "
            "turn them into a value proposition. Your goal is to get the client onto a "
            "discovery call. Do NOT sound desperate. Sound like an expert who is doing them a favor."
        )
        return self.generate_response(system_prompt, f"Convert this audit into a winning proposal: {audit_results}")

    def run_hunter(self, job_description):
        """Agent: The Lead Filter. Decides if a job is worth 20k+ or if it's a waste of time."""
        system_prompt = (
            "You are the Strategic Growth Lead for AJ Webnova. Analyze the job post. "
            "If the client mentions 'cheap', 'budget', or 'small task', flag it as LOW VALUE. "
            "If they mention 'growth', 'enterprise', 'scaling', or 'long-term', flag as HIGH VALUE."
        )
        return self.generate_response(system_prompt, f"Analyze this lead: {job_description}")
