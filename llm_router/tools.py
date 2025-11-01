
"""
Tool implementations.
Each tool = a governed capability.

The router LLM chooses which tool to call and gives arguments.
We then execute that tool in a controlled way.
"""

import json
from typing import Dict, Any

from .config import client, CHITCHAT_MODEL
from .planner import plan_sql
from .validator import validate_sql
from .db import run_readonly
from .synthesizer import synthesize_answer


def run_chitchat_tool(arguments: Dict[str, Any]) -> str:
    """
    Handle general conceptual / explanatory questions
    that do NOT require hitting the database.
    """
    user_q = arguments.get("question", "") or arguments.get("raw_user_input", "")
    if not user_q:
        user_q = "Answer helpfully and clearly."

    resp = client.chat.completions.create(
        model=CHITCHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful, precise assistant."},
            {"role": "user", "content": user_q}
        ],
        temperature=0.4
    )
    return resp.choices[0].message.content


def run_sql_lookup_tool(arguments: Dict[str, Any]) -> str:
    """
    Example arguments from the router:
    {
      "client": "Acme",
      "status": "unpaid",
      "amount_gt": 200000,
      "date_after": "2025-09-01",
      "limit": 20
    }

    Steps:
    1. LLM SQL planner proposes a candidate SQL (read-only SELECT).
    2. validator.py enforces safety / whitelist.
    3. db.run_readonly executes that SQL.
    4. synthesizer.synthesize_answer generates a clean business summary.
    """
    # 1. plan SQL from arguments
    plan = plan_sql(arguments)
    sql = plan["sql"]

    # 2. validate
    if not validate_sql(sql):
        return "I understand the request but I am not allowed to run that query safely."

    # 3. execute
    result_rows = run_readonly(sql)

    # 4. synthesize
    user_q = json.dumps(arguments)
    return synthesize_answer(user_q, sql, result_rows)


# registry of capabilities
TOOLS = {
    "chitchat_tool": run_chitchat_tool,
    "sql_lookup_tool": run_sql_lookup_tool
}
