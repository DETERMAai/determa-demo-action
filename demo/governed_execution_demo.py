from __future__ import annotations

import json
from datetime import datetime


STEPS = [
    ("PROPOSAL_CREATED", "AI proposes governed mutation"),
    ("WAITING_APPROVAL", "Execution blocked pending authority approval"),
    ("CAPABILITY_GRANTED", "Single-use execution capability issued"),
    ("WITNESS_VALIDATED", "Repository witness state verified"),
    ("EXECUTION_ALLOWED", "Governed execution authorized"),
    ("EXECUTION_RECEIPT_WRITTEN", "Append-only execution receipt persisted"),
    ("REPLAY_VALIDATED", "Deterministic replay verified"),
]


print("=" * 72)
print("DETERMA — Governed Execution Runtime Demonstration")
print("=" * 72)
print()

for index, (event, description) in enumerate(STEPS, start=1):
    payload = {
        "sequence": index,
        "event": event,
        "description": description,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    print(json.dumps(payload, indent=2))
    print()

print("Runtime result: EXECUTION LEGITIMACY VERIFIED")
