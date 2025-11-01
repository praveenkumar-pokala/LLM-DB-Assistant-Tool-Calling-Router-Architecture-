
"""
Answer synthesizer:
Turns DB rows + executed SQL into a human-friendly answer.

We ask the LLM to summarize, highlight totals/insights,
and avoid dumping raw DB rows unless needed.
"""

import json
from typing import List, Dict, Any

from .config import client, SYNTH_MODEL

ANSWER_SYNTH_PROMPT = """
You are a business assistant.
Given:
1. the user's intent (original question),
2. the executed SQL,
3. the rows returned (JSON array of objects),

Return a short, confident, human-readable answer.
Do not invent data that is not present.
If there are many rows, summarize count and highlights instead of dumping everything.
"""


def synthesize_answer(user_question: str, sql: str, rows: List[Dict[str, Any]]) -> str:
    """
    user_question: what the user was basically asking
    sql:           the final SQL actually executed
    rows:          DB rows we got back (already authorized / filtered)
    """
    resp = client.chat.completions.create(
        model=SYNTH_MODEL,
        messages=[
            {"role": "system", "content": ANSWER_SYNTH_PROMPT},
            {"role": "user", "content": json.dumps({
                "user_question": user_question,
                "sql_executed": sql,
                "rows": rows
            }, indent=2)}
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content
