"""Factory autonomous branch session model.

A session is the reconstructable unit of governed autonomous work.
It binds task identity, branch identity, workspace changes, replay artifact,
and runtime outcome.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from factory.runtime.git_workspace import WorkspaceChangeSet


@dataclass(frozen=True)
class FactorySession:
    session_id: str
    task_id: str
    branch_name: str
    change_set: WorkspaceChangeSet
    replay: dict[str, Any] | None = None
    outcome: str | None = None
    state: str = "IDLE"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["change_set"] = self.change_set.to_dict()
        return data


def build_branch_name(task_id: str, task_name: str) -> str:
    """Build deterministic factory branch name."""
    clean_task_id = _slug(task_id)
    clean_task_name = _slug(task_name)
    return f"factory/{clean_task_id}-{clean_task_name}"


def build_session_id(task_id: str, branch_name: str) -> str:
    """Build readable deterministic session id."""
    clean_task_id = _slug(task_id)
    clean_branch = _slug(branch_name.replace("/", "-"))
    return f"session-{clean_task_id}-{clean_branch}"


def create_session(task_id: str, task_name: str, change_set: WorkspaceChangeSet) -> FactorySession:
    """Create a new deterministic factory session object."""
    branch_name = build_branch_name(task_id, task_name)
    return FactorySession(
        session_id=build_session_id(task_id, branch_name),
        task_id=task_id,
        branch_name=branch_name,
        change_set=change_set,
    )


def with_runtime_result(
    session: FactorySession,
    replay: dict[str, Any] | None,
    outcome: str,
    state: str,
) -> FactorySession:
    """Return an updated immutable session with runtime result attached."""
    return FactorySession(
        session_id=session.session_id,
        task_id=session.task_id,
        branch_name=session.branch_name,
        change_set=session.change_set,
        replay=replay,
        outcome=outcome,
        state=state,
        created_at=session.created_at,
    )


def _slug(value: str) -> str:
    chars: list[str] = []
    previous_dash = False

    for char in value.lower().strip():
        if char.isalnum():
            chars.append(char)
            previous_dash = False
        elif not previous_dash:
            chars.append("-")
            previous_dash = True

    return "".join(chars).strip("-") or "unnamed"
