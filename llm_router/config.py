
"""
Shared config:
- OpenAI client
- Allowed schema
- Central model names
- API key handling
"""

import os
from openai import OpenAI

# Load key from environment. DO NOT hardcode secrets.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

# OpenAI client (uses chat.completions.create(...))
client = OpenAI(api_key=OPENAI_API_KEY)

# Allowed schema we expose to the LLM SQL planner.
# Only columns here are allowed to be queried.
ALLOWED_SCHEMA = {
    "invoices": {
        "columns": [
            "id",
            "client_name",
            "status",
            "amount_in_inr",
            "invoice_date"
        ]
    }
}

# Centralize model names so it's easy to swap / version them.
ROUTER_MODEL    = "gpt-4o-mini"
PLANNER_MODEL   = "gpt-4o-mini"
SYNTH_MODEL     = "gpt-4o-mini"
CHITCHAT_MODEL  = "gpt-4o-mini"
