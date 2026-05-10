"""Factory runtime timeline renderer.

Turns persisted runtime events into a deterministic audit timeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from factory.runtime.persistence import RuntimeStore


def render_runtime_timeline(events: list[dict[str, Any]]) -> str:
    """Render runtime events as a deterministic Markdown timeline."""
    lines: list[str] = []

    lines.append("# DETERMA Factory Runtime Timeline")
    lines.append("")

    if not events:
        lines.append("No runtime events recorded.")
        return "\n".join(lines).strip() + "\n"

    for event in events:
        outcome = event.get("outcome", "UNKNOWN")
        task_id = event.get("task_id", "unknown-task")
        state = event.get("state", "UNKNOWN")
        created_at = event.get("created_at", "unknown-time")
        reason = event.get("reason", "no reason recorded")
        changed_files = event.get("changed_files", [])
        replay = event.get("replay") or {}

        lines.append(f"## {outcome} — {task_id}")
        lines.append("")
        lines.append(f"- Time: {created_at}")
        lines.append(f"- Final State: {state}")
        lines.append(f"- Reason: {reason}")

        if replay:
            lines.append(f"- Replay Severity: {replay.get('severity', 'unknown')}")
            lines.append(f"- Replay Trust State: {replay.get('trust_state', 'unknown')}")

        lines.append("- Changed Files:")
        if changed_files:
            for path in changed_files:
                lines.append(f"  - {path}")
        else:
            lines.append("  - none")

        lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_timeline_from_store(path: Path) -> str:
    """Load runtime events from a store path and render a timeline."""
    store = RuntimeStore(path)
    return render_runtime_timeline(store.load())
