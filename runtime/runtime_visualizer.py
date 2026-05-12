from __future__ import annotations

import sqlite3
from pathlib import Path


DEFAULT_DB = Path("runtime.db")


RUNTIME_STATES = {
    "PROPOSAL_CREATED": "AI proposal generated",
    "WAITING_APPROVAL": "Execution paused pending authority",
    "CAPABILITY_GRANTED": "Single-use execution capability issued",
    "EXECUTION_ALLOWED": "Governed execution authorized",
    "EXECUTION_BLOCKED": "Execution blocked fail-closed",
    "EXECUTION_RECEIPT": "Append-only execution receipt persisted",
    "REPLAY_VALIDATED": "Deterministic replay verified",
}


COLORS = {
    "PROPOSAL_CREATED": "\033[94m",
    "WAITING_APPROVAL": "\033[93m",
    "CAPABILITY_GRANTED": "\033[92m",
    "EXECUTION_ALLOWED": "\033[96m",
    "EXECUTION_BLOCKED": "\033[91m",
    "EXECUTION_RECEIPT": "\033[95m",
    "REPLAY_VALIDATED": "\033[92m",
}

RESET = "\033[0m"


def fetch_runtime_events(db_path: str = str(DEFAULT_DB)) -> list[tuple]:
    conn = sqlite3.connect(db_path)

    try:
        return conn.execute(
            "SELECT sequence, event_type, created_at FROM events ORDER BY sequence"
        ).fetchall()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("DETERMA RUNTIME VISUALIZER")
    print("=" * 80)
    print()

    events = fetch_runtime_events()

    for sequence, event_type, created_at in events:
        color = COLORS.get(event_type, "")
        description = RUNTIME_STATES.get(event_type, "Runtime event")

        print(f"{color}[{sequence}] {event_type}{RESET}")
        print(f"  {description}")
        print(f"  timestamp={created_at}")
        print()

    print("Runtime lineage visualization complete.")
