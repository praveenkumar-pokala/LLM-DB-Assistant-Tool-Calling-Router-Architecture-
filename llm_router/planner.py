
"""
SQL planner LLM:
- Takes structured filter args from router output
- Produces candidate SQL + purpose
- Sees only a whitelisted schema
"""

import json
from typing import Dict, Any

from .config import client, PLANNER_MODEL, ALLOWED_SCHEMA

SQL_PLANNER_PROMPT = """
You are a SQL planner for a reporting assistant.

Return STRICT JSON:
{
  "sql": "...",
  "purpose": "short english reason for the query"
}

Rules:
1. ONLY use this allowed schema:
   invoices(id, client_name, status, amount_in_inr, invoice_date)

2. ONLY generate SELECT statements.
3. NEVER use INSERT/UPDATE/DELETE/ALTER/DROP/TRUNCATE/CREATE.
4. Do NOT use SELECT *.
5. Include ORDER BY invoice_date DESC if a date filter is relevant.
6. Include LIMIT (e.g. LIMIT 20) unless the user explicitly said "all".
"""


def plan_sql(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    arguments example:
    {
      "client": "Acme",
      "status": "unpaid",
      "amount_gt": 200000,
      "date_after": "2025-09-01",
      "limit": 20
    }

    We pass these arguments + whitelist schema to the planner LLM.
    The LLM responds with a JSON { "sql": "...", "purpose": "..." }.
    """
    payload = {
        "allowed_schema": ALLOWED_SCHEMA,
        "requested_filter": arguments
    }

    resp = client.chat.completions.create(
        model=PLANNER_MODEL,
        messages=[
            {"role": "system", "content": SQL_PLANNER_PROMPT},
            {"role": "user", "content": json.dumps(payload, indent=2)}
        ],
        temperature=0.0,
    )

    raw = resp.choices[0].message.content
    return json.loads(raw)
