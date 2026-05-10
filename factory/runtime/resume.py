"""Factory runtime resume planning.

Classifies recovered sessions into resumable governance states.
This layer does not execute work automatically. It determines whether a
recovered execution context is safe to continue.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResumeStatus(str, Enum):
    RESUMABLE = "RESUMABLE"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    BLOCKED = "BLOCKED"
    ORPHANED = "ORPHANED"


@dataclass(frozen=True)
class ResumeDecision:
    task_id: str
    status: ResumeStatus
    reasons: tuple[str, ...]
    session: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "reasons": list(self.reasons),
            "session": self.session,
        }


@dataclass(frozen=True)
class ResumePlan:
    decisions: tuple[ResumeDecision, ...]

    def resumable(self) -> tuple[ResumeDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.status == ResumeStatus.RESUMABLE)

    def blocked(self) -> tuple[ResumeDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.status == ResumeStatus.BLOCKED)

    def requires_review(self) -> tuple[ResumeDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.status == ResumeStatus.REQUIRES_REVIEW)

    def orphaned(self) -> tuple[ResumeDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.status == ResumeStatus.ORPHANED)


PENDING_STATES = {"RUNNING", "AWAITING_APPROVAL", "IDLE"}
TERMINAL_STATES = {"COMPLETE", "BLOCKED"}


def build_resume_plan(
    sessions: list[dict[str, Any]],
    pending_approvals: list[dict[str, Any]],
    blocked_events: list[dict[str, Any]],
) -> ResumePlan:
    """Classify recovered sessions into governance-safe resume states."""
    blocked_task_ids = {
        str(event.get("task_id"))
        for event in blocked_events
        if event.get("task_id") is not None
    }
    approval_task_ids = {
        str(approval.get("task_id"))
        for approval in pending_approvals
        if approval.get("task_id") is not None
    }

    decisions: list[ResumeDecision] = []

    for session in sessions:
        task_id = str(session.get("task_id", "unknown-task"))
        state = str(session.get("state", "UNKNOWN"))
        branch_name = session.get("branch_name")

        reasons: list[str] = []

        if state in TERMINAL_STATES:
            decisions.append(
                ResumeDecision(
                    task_id=task_id,
                    status=ResumeStatus.ORPHANED,
                    reasons=(f"terminal session state: {state}",),
                    session=session,
                )
            )
            continue

        if task_id in blocked_task_ids:
            decisions.append(
                ResumeDecision(
                    task_id=task_id,
                    status=ResumeStatus.BLOCKED,
                    reasons=("blocked runtime event exists",),
                    session=session,
                )
            )
            continue

        if task_id in approval_task_ids:
            decisions.append(
                ResumeDecision(
                    task_id=task_id,
                    status=ResumeStatus.REQUIRES_REVIEW,
                    reasons=("pending approval exists",),
                    session=session,
                )
            )
            continue

        if not branch_name:
            reasons.append("missing branch name")

        if state not in PENDING_STATES:
            reasons.append(f"unexpected session state: {state}")

        if reasons:
            decisions.append(
                ResumeDecision(
                    task_id=task_id,
                    status=ResumeStatus.ORPHANED,
                    reasons=tuple(reasons),
                    session=session,
                )
            )
            continue

        decisions.append(
            ResumeDecision(
                task_id=task_id,
                status=ResumeStatus.RESUMABLE,
                reasons=("resume conditions satisfied",),
                session=session,
            )
        )

    return ResumePlan(decisions=tuple(decisions))


def render_resume_plan(plan: ResumePlan) -> str:
    """Render deterministic Markdown resume plan."""
    lines: list[str] = []

    lines.append("# DETERMA Factory Resume Plan")
    lines.append("")

    if not plan.decisions:
        lines.append("- no sessions available for recovery")
        lines.append("")
        return "\n".join(lines)

    for decision in plan.decisions:
        lines.append(f"## {decision.task_id}")
        lines.append(f"Status: {decision.status.value}")
        for reason in decision.reasons:
            lines.append(f"- {reason}")
        lines.append("")

    return "\n".join(lines)
