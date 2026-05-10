"""Factory session timeline renderer.

Renders persisted factory sessions into a human-readable execution narrative.
"""

from __future__ import annotations

from typing import Any


def render_session_timeline(sessions: list[dict[str, Any]]) -> str:
    """Render persisted sessions as deterministic Markdown."""
    lines: list[str] = []

    lines.append("# DETERMA Factory Session Timeline")
    lines.append("")

    if not sessions:
        lines.append("No sessions recorded.")
        return "\n".join(lines).strip() + "\n"

    for session in sessions:
        session_id = session.get("session_id", "unknown-session")
        task_id = session.get("task_id", "unknown-task")
        branch_name = session.get("branch_name", "unknown-branch")
        state = session.get("state", "UNKNOWN")
        outcome = session.get("outcome", "PENDING")
        created_at = session.get("created_at", "unknown-time")
        change_set = session.get("change_set", {}) or {}
        changed_files = change_set.get("changed_files", [])
        replay = session.get("replay") or {}

        lines.append(f"## {outcome} — {task_id}")
        lines.append("")
        lines.append(f"- Session: {session_id}")
        lines.append(f"- Branch: {branch_name}")
        lines.append(f"- State: {state}")
        lines.append(f"- Created: {created_at}")

        if replay:
            lines.append(f"- Replay Severity: {replay.get('severity', 'unknown')}")
            lines.append(f"- Replay Trust State: {replay.get('trust_state', 'unknown')}")
            lines.append(f"- Recommended Action: {replay.get('recommended_action', 'unknown')}")

        lines.append("- Changed Files:")
        if changed_files:
            for path in changed_files:
                lines.append(f"  - {path}")
        else:
            lines.append("  - none")

        lines.append("")

    return "\n".join(lines).strip() + "\n"
