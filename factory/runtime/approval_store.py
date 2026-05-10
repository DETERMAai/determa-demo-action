"""Factory approval persistence.

Stores approval queue records as append-only JSON so pending and completed
approval decisions survive runtime restarts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from factory.runtime.approval_queue import ApprovalRequest


class ApprovalStore:
    """Append-only JSON store for approval requests."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, request: ApprovalRequest) -> None:
        requests = self.load()
        requests.append(request.to_dict())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(requests, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def pending(self) -> list[dict[str, Any]]:
        return [request for request in self.load() if request.get("status") == "PENDING"]

    def completed(self) -> list[dict[str, Any]]:
        return [request for request in self.load() if request.get("status") != "PENDING"]
