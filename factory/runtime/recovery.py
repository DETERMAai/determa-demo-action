"""Factory runtime recovery.

Reconstructs persisted factory state after a runtime restart.
This module does not resume execution automatically; it reconstructs the
operational state required for safe resume decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from factory.runtime.approval_store import ApprovalStore
from factory.runtime.persistence import RuntimeStore
from factory.runtime.session_store import SessionStore


@dataclass(frozen=True)
class RuntimeRecoveryState:
    runtime_events: list[dict[str, Any]]
    sessions: list[dict[str, Any]]
    approvals: list[dict[str, Any]]
    pending_approvals: list[dict[str, Any]]
    active_sessions: list[dict[str, Any]]
    blocked_events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_events": self.runtime_events,
            "sessions": self.sessions,
            "approvals": self.approvals,
            "pending_approvals": self.pending_approvals,
            "active_sessions": self.active_sessions,
            "blocked_events": self.blocked_events,
        }


@dataclass(frozen=True)
class RuntimeRecoverySummary:
    total_events: int
    total_sessions: int
    total_approvals: int
    pending_approvals: int
    active_sessions: int
    blocked_events: int

    def to_dict(self) -> dict[str, int]:
        return {
            "total_events": self.total_events,
            "total_sessions": self.total_sessions,
            "total_approvals": self.total_approvals,
            "pending_approvals": self.pending_approvals,
            "active_sessions": self.active_sessions,
            "blocked_events": self.blocked_events,
        }


def recover_runtime_state(
    history_path: Path,
    sessions_path: Path,
    approvals_path: Path,
) -> RuntimeRecoveryState:
    """Load persisted runtime state into a reconstructable recovery object."""
    runtime_events = RuntimeStore(history_path).load()
    sessions = SessionStore(sessions_path).load()
    approval_store = ApprovalStore(approvals_path)
    approvals = approval_store.load()
    pending_approvals = approval_store.pending()

    active_sessions = [
        session
        for session in sessions
        if session.get("state") not in {"COMPLETE", "BLOCKED"}
    ]
    blocked_events = [event for event in runtime_events if event.get("outcome") == "BLOCKED"]

    return RuntimeRecoveryState(
        runtime_events=runtime_events,
        sessions=sessions,
        approvals=approvals,
        pending_approvals=pending_approvals,
        active_sessions=active_sessions,
        blocked_events=blocked_events,
    )


def summarize_recovery_state(state: RuntimeRecoveryState) -> RuntimeRecoverySummary:
    """Build a compact recovery summary."""
    return RuntimeRecoverySummary(
        total_events=len(state.runtime_events),
        total_sessions=len(state.sessions),
        total_approvals=len(state.approvals),
        pending_approvals=len(state.pending_approvals),
        active_sessions=len(state.active_sessions),
        blocked_events=len(state.blocked_events),
    )


def render_recovery_summary(summary: RuntimeRecoverySummary) -> str:
    """Render recovery summary as deterministic Markdown."""
    lines = [
        "# DETERMA Factory Runtime Recovery",
        "",
        f"Total Events: {summary.total_events}",
        f"Total Sessions: {summary.total_sessions}",
        f"Total Approvals: {summary.total_approvals}",
        f"Pending Approvals: {summary.pending_approvals}",
        f"Active Sessions: {summary.active_sessions}",
        f"Blocked Events: {summary.blocked_events}",
        "",
    ]
    return "\n".join(lines)
