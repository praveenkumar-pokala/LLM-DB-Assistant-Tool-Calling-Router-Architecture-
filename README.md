
# LLM DB Assistant (Tool-Calling Router Architecture)

## What this repo shows

This repo demonstrates a production-style pattern for an LLM assistant that:
1. Talks like a normal helpful assistant for general questions.
2. Can query a database (read-only, guarded) when the user asks for factual business data.
3. Chooses which behavior to run using a **tool-calling router** instead of a big `if/else` chain.

The pipeline is built for enterprise safety:
- Router model picks a tool (`chitchat_tool`, `sql_lookup_tool`, ...).
- SQL Planner model drafts a SELECT query using only allowed schema.
- SQL Validator (pure code) enforces safety. No UPDATE/DELETE/etc.
- Query executes only on a read-only replica (here we simulate SQLite).
- Answer Synthesizer model turns raw rows into a human-quality summary.
- We never hallucinate numbers. We always ground data to DB results.

This is the step from "demo bot" to "governed AI assistant".


## High-level flow

User message → `router.route_to_tool()`  
→ returns `{ "tool": "...", "arguments": {...} }`  
→ we dispatch to that tool via `tools.TOOLS[tool]`  
→ for `sql_lookup_tool`: plan SQL → validate → execute → summarize


## Repo structure

```text
llm_db_assistant_toolrouter_repo/
├── README.md                  <-- this file
├── app.py                     <-- main entry point demo
└── llm_router/
    ├── config.py              <-- OpenAI client + allowed schema
    ├── db.py                  <-- in-memory demo DB + read-only query helper
    ├── router.py              <-- tool-calling router (LLM picks tool + args)
    ├── planner.py             <-- SQL planner LLM prompt
    ├── validator.py           <-- SQL validator (code-only safety checks)
    ├── synthesizer.py         <-- Answer synthesizer LLM prompt
    ├── tools.py               <-- chitchat_tool, sql_lookup_tool, TOOLS registry
    └── service.py             <-- answer_user_message() glue
```


## How to run

1. Install deps (Python 3.10+ recommended):
```bash
pip install openai
```

2. Export your key (do not hardcode it in code):
```bash
export OPENAI_API_KEY="sk-..."
```

3. Run the demo:
```bash
python app.py
```

You should see two calls:
- A SQL-style business request
- A chitchat-style conceptual request


## Security notes

- `validator.py` prevents destructive SQL and enforces schema whitelisting.
- We only expose a SAFE `ALLOWED_SCHEMA` to the LLM planner, not full prod DB.
- In production you must also add:
  - role-based authorization before running `sql_lookup_tool`
  - PII masking before passing rows to the LLM
  - audit logs (user question, generated SQL, etc.)

This pattern is designed so you can look a compliance/legal team in the eye and say:
"We never run arbitrary model output. We always vet, enforce, and explain."
