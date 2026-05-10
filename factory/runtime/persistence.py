"""Factory runtime persistence.

Stores bounded runtime history as JSON.
No database required for the first implementation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RuntimeEvent:
    event_id: str
    task_id: str
    state: str
    outcome: str
    reason: str
    replay: dict[str, Any] | None = None
    changed_files: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["changed_files"] = list(self.changed_files)
        return data


class RuntimeStore:
    """Append-only JSON store for runtime events."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: RuntimeEvent) -> None:
        events = self.load()
        events.append(event.to_dict())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(events, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))


def build_event_id(task_id: str, state: str, index: int) -> str:
    clean_task = "".join(ch for ch in task_id.lower() if ch.isalnum() or ch == "-")
    clean_state = "".join(ch for ch in state.lower() if ch.isalnum() or ch == "-")
    return f"evt-{clean_task}-{clean_state}-{index + 1}"
