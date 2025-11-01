
"""
LLM tool-calling style router.

The LLM returns which tool to call and structured arguments.
We don't do giant if/else. We dispatch via a registry instead.
"""

import json
from typing import Dict, Any

from .config import client, ROUTER_MODEL

TOOL_ROUTER_PROMPT = """
You are a tool router for an enterprise assistant.

Return STRICT JSON with the shape:
{
  "tool": "<one of: chitchat_tool, sql_lookup_tool>",
  "arguments": { ... },
  "explanation": "short reason for choosing this tool"
}

Rules:
1. Use "chitchat_tool" when the user is asking for general explanations,
   brainstorming, opinions, strategy, or conceptual answers that do NOT
   require data from the invoices table.

2. Use "sql_lookup_tool" ONLY if the user clearly asks for factual business
   data from the invoices table. For example:
   - unpaid invoices
   - outstanding amounts
   - invoices above some threshold
   - date filters like "after 2025-09-01"

3. When you choose "sql_lookup_tool", include arguments:
   - client (string or null)
   - status (string like "unpaid" or null)
   - amount_gt (number or null)
   - date_after (ISO date string like "2025-09-01" or null)
   - limit (integer, default 20)

Return ONLY valid JSON. No commentary outside JSON.
"""


def route_to_tool(user_msg: str) -> Dict[str, Any]:
    """
    Ask LLM which tool should handle this user message.
    The result drives the dispatcher.
    """
    resp = client.chat.completions.create(
        model=ROUTER_MODEL,
        messages=[
            {"role": "system", "content": TOOL_ROUTER_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.0,
    )
    raw = resp.choices[0].message.content
    return json.loads(raw)
