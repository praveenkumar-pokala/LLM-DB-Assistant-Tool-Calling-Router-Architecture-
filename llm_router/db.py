
"""
In-memory SQLite setup for demo,
plus read-only query helper.

In production:
- Use a read-only replica
- Enforce tenant scoping / row-level security
"""

import sqlite3
from typing import List, Dict, Any

# Create demo in-memory DB
conn = sqlite3.connect(":memory:")
cur = conn.cursor()

cur.execute(
    "CREATE TABLE invoices ("
    "id INTEGER PRIMARY KEY,"
    "client_name TEXT,"
    "status TEXT,"
    "amount_in_inr REAL,"
    "invoice_date TEXT"
    ")"
)

rows_seed = [
    (1, "Acme Corp",      "unpaid", 375000, "2025-10-12"),
    (2, "Acme Corp",      "unpaid", 210000, "2025-09-20"),
    (3, "Acme Corp",      "paid",   180000, "2025-09-05"),
    (4, "Skyline Motors", "unpaid", 990000, "2025-10-01"),
    (5, "Skyline Motors", "unpaid", 120000, "2025-08-28")
]
cur.executemany("INSERT INTO invoices VALUES (?, ?, ?, ?, ?)", rows_seed)
conn.commit()


def run_readonly(sql: str) -> List[Dict[str, Any]]:
    """
    Execute a validated, read-only SQL SELECT query and
    return list of dict rows.
    """
    c = conn.cursor()
    c.execute(sql)
    cols = [d[0] for d in c.description]
    out = []
    for row in c.fetchall():
        out.append(dict(zip(cols, row)))
    return out
