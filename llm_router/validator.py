
"""
SQL validator.
No model is trusted blindly. We gate every SQL string here.

We enforce:
- must start with SELECT
- block destructive keywords
- only allowed tables/columns
- LIMIT presence (soft check here for demo)
"""

import re
from typing import Dict, Any

from .config import ALLOWED_SCHEMA


def validate_sql(sql: str) -> bool:
    """
    Returns True only if the SQL is considered safe.
    """
    s = sql.lower()

    # must begin with SELECT
    if not s.strip().startswith("select "):
        print("❌ not a SELECT")
        return False

    # block destructive tokens
    forbidden = [" delete ", " update ", " insert ", " alter ", " drop ", " truncate ", " create "]
    for token in forbidden:
        if token in s:
            print("❌ forbidden keyword:", token.strip())
            return False

    # table whitelist check
    tables = re.findall(r"(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", s)
    for t in tables:
        if t not in ALLOWED_SCHEMA:
            print("❌ table not allowed:", t)
            return False

    # column whitelist check
    m = re.search(r"select\s+(.*?)\s+from", s, re.DOTALL)
    if m:
        cols_part = m.group(1)
        cols = [c.strip() for c in cols_part.split(",")]
        for c in cols:
            base = c.split()[0]  # remove aliases
            if "." in base:
                tname, cname = base.split(".", 1)
            else:
                tname, cname = None, base

            if tname and tname in ALLOWED_SCHEMA:
                if cname not in ALLOWED_SCHEMA[tname]["columns"]:
                    print(f"❌ column {tname}.{cname} not allowed")
                    return False

    # LIMIT check (soft for demo)
    if " limit " not in s:
        print("⚠️ No LIMIT found (allowing for demo).")

    print("SQL validated ✅")
    return True
