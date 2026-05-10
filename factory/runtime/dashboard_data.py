"""Factory dashboard data layer.

Aggregates runtime events, session records, and metrics into a simple
serializable dashboard payload.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from factory.runtime.metrics import RuntimeMetrics, compute_runtime_metrics


@dataclass(frozen=True)
class FactoryDashboardData:
    total_sessions: int
    completed_sessions: int
    blocked_sessions: int
    runtime_metrics: RuntimeMetrics
    recent_sessions: list[dict[str, Any]]
    recent_events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_sessions": self.total_sessions,
            "completed_sessions": self.completed_sessions,
            "blocked_sessions": self.blocked_sessions,
            "runtime_metrics": self.runtime_metrics.to_dict(),
            "recent_sessions": self.recent_sessions,
            "recent_events": self.recent_events,
        }


def build_dashboard_data(
    sessions: list[dict[str, Any]],
    events: list[dict[str, Any]],
    recent_limit: int = 10,
) -> FactoryDashboardData:
    """Build deterministic dashboard data from persisted runtime records."""
    completed_sessions = sum(1 for session in sessions if session.get("outcome") == "PASSED")
    blocked_sessions = sum(1 for session in sessions if session.get("outcome") == "BLOCKED")

    return FactoryDashboardData(
        total_sessions=len(sessions),
        completed_sessions=completed_sessions,
        blocked_sessions=blocked_sessions,
        runtime_metrics=compute_runtime_metrics(events),
        recent_sessions=list(sessions[-recent_limit:]),
        recent_events=list(events[-recent_limit:]),
    )


def render_dashboard_summary(data: FactoryDashboardData) -> str:
    """Render dashboard data as deterministic Markdown."""
    lines: list[str] = []

    lines.append("# DETERMA Factory Dashboard")
    lines.append("")
    lines.append(f"Total Sessions: {data.total_sessions}")
    lines.append(f"Completed Sessions: {data.completed_sessions}")
    lines.append(f"Blocked Sessions: {data.blocked_sessions}")
    lines.append(f"Runtime Pass Rate: {data.runtime_metrics.pass_rate:.2%}")
    lines.append(f"Runtime Blocked Rate: {data.runtime_metrics.blocked_rate:.2%}")
    lines.append("")

    lines.append("## Recent Sessions")
    if not data.recent_sessions:
        lines.append("- none")
    else:
        for session in data.recent_sessions:
            lines.append(
                f"- {session.get('outcome', 'PENDING')} — "
                f"{session.get('task_id', 'unknown-task')} — "
                f"{session.get('branch_name', 'unknown-branch')}"
            )
    lines.append("")

    lines.append("## Recent Runtime Events")
    if not data.recent_events:
        lines.append("- none")
    else:
        for event in data.recent_events:
            lines.append(
                f"- {event.get('outcome', 'UNKNOWN')} — "
                f"{event.get('task_id', 'unknown-task')} — "
                f"{event.get('reason', 'no reason recorded')}"
            )
    lines.append("")

    return "\n".join(lines).strip() + "\n"
