"""Factory session persistence.

Stores reconstructable autonomous execution sessions as append-only JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from factory.runtime.session import FactorySession


class SessionStore:
    """Append-only JSON store for factory sessions."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, session: FactorySession) -> None:
        sessions = self.load()
        sessions.append(session.to_dict())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(sessions, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def find_by_task_id(self, task_id: str) -> list[dict[str, Any]]:
        return [session for session in self.load() if session.get("task_id") == task_id]

    def find_by_branch_name(self, branch_name: str) -> list[dict[str, Any]]:
        return [session for session in self.load() if session.get("branch_name") == branch_name]
