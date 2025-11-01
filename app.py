
"""
Demo entrypoint.

Run this file to see how the assistant behaves for two queries:
1. A data question (should hit sql_lookup_tool)
2. A conceptual question (should hit chitchat_tool)

Usage:
    export OPENAI_API_KEY="sk-..."
    python app.py
"""

from llm_router.service import answer_user_message

if __name__ == "__main__":
    q1 = "Show unpaid invoices for Acme after 2025-09-01 above 200000 rupees."
    q2 = "Explain embeddings like I am new to machine learning."

    print("USER:", q1)
    print("ASSISTANT:", answer_user_message(q1))
    print()
    print("USER:", q2)
    print("ASSISTANT:", answer_user_message(q2))
