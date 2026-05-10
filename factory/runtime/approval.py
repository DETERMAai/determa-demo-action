"""Factory runtime approval decision layer.

Handles human approval decisions for executions waiting in AWAITING_APPROVAL.
No merge. No deployment. Only state transition decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from factory.runtime.state import RuntimeState, RuntimeTransition, transition


class ApprovalDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


@dataclass(frozen=True)
class ApprovalRecord:
    task_id: str
    decision: ApprovalDecision
    decided_by: str
    reason: str
    previous_state: RuntimeState
    next_state: RuntimeState
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, str]:
        return {
            "task_id": self.task_id,
            "decision": self.decision.value,
            "decided_by": self.decided_by,
            "reason": self.reason,
            "previous_state": self.previous_state.value,
            "next_state": self.next_state.value,
            "created_at": self.created_at,
        }


def approve_execution(
    task_id: str,
    current_state: RuntimeState,
    decided_by: str,
    reason: str,
) -> tuple[RuntimeTransition, ApprovalRecord]:
    """Approve an execution waiting for human approval."""
    next_state = RuntimeState.COMPLETE
    runtime_transition = transition(current_state, next_state, reason)
    record = ApprovalRecord(
        task_id=task_id,
        decision=ApprovalDecision.APPROVE,
        decided_by=decided_by,
        reason=reason,
        previous_state=current_state,
        next_state=next_state,
    )
    return runtime_transition, record


def reject_execution(
    task_id: str,
    current_state: RuntimeState,
    decided_by: str,
    reason: str,
) -> tuple[RuntimeTransition, ApprovalRecord]:
    """Reject an execution waiting for human approval."""
    next_state = RuntimeState.BLOCKED
    runtime_transition = transition(current_state, next_state, reason)
    record = ApprovalRecord(
        task_id=task_id,
        decision=ApprovalDecision.REJECT,
        decided_by=decided_by,
        reason=reason,
        previous_state=current_state,
        next_state=next_state,
    )
    return runtime_transition, record
