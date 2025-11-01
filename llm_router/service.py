
"""
Service layer:
- answer_user_message() is what your app calls.

It asks the router LLM which tool should run,
then dispatches to that tool's function from TOOLS.

In production:
- Add authorization checks here (who is allowed to see what data)
- Add PII masking
- Add audit logging (question, SQL, response)
"""

from typing import Dict, Any

from .router import route_to_tool
from .tools import TOOLS, run_chitchat_tool


def answer_user_message(user_message: str) -> str:
    """
    Orchestration entry point (like your chat endpoint).
    1. router.route_to_tool() asks the LLM which tool to run
    2. pick that tool function from TOOLS
    3. execute tool logic (with validation, etc.)
    """
    decision: Dict[str, Any] = route_to_tool(user_message)

    tool_name = decision.get("tool", "chitchat_tool")
    args = decision.get("arguments", {})
    tool_fn = TOOLS.get(tool_name, run_chitchat_tool)

    # Authorization / audit / masking would go here in real life.
    return tool_fn(args)
