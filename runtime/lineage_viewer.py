from __future__ import annotations

import json
import sqlite3
from pathlib import Path


DEFAULT_DB = Path("runtime.db")


def load_events(db_path: str = str(DEFAULT_DB)) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute(
            "SELECT sequence, event_type, payload_json, created_at FROM events ORDER BY sequence"
        ).fetchall()

        events = []
        for row in rows:
            payload = {}
            if row["payload_json"]:
                try:
                    payload = json.loads(row["payload_json"])
                except Exception:
                    payload = {"raw": row["payload_json"]}

            events.append(
                {
                    "sequence": row["sequence"],
                    "event_type": row["event_type"],
                    "payload": payload,
                    "created_at": row["created_at"],
                }
            )

        return events
    finally:
        conn.close()


if __name__ == "__main__":
    events = load_events()

    print("=" * 72)
    print("DETERMA LINEAGE VIEWER")
    print("=" * 72)
    print()

    for event in events:
        print(f"[{event['sequence']}] {event['event_type']}")
        print(f"TIME: {event['created_at']}")
        print(json.dumps(event['payload'], indent=2))
        print("-" * 72)
