"""Factory runtime approval decision layer.

Handles human approval decisions for executions waiting in AWAITING_APPROVAL.
No merge. No deployment. Only authority-bound state transition decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from factory.runtime.identity import ActorIdentity, can_make_approval_decision
from factory.runtime.state import RuntimeState, RuntimeTransition, transition


class ApprovalDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


@dataclass(frozen=True)
class ApprovalRecord:
    task_id: str
    decision: ApprovalDecision
    actor: ActorIdentity
    reason: str
    previous_state: RuntimeState
    next_state: RuntimeState
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def decided_by(self) -> str:
        return self.actor.actor_id

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "decision": self.decision.value,
            "actor": self.actor.to_dict(),
            "decided_by": self.actor.actor_id,
            "reason": self.reason,
            "previous_state": self.previous_state.value,
            "next_state": self.next_state.value,
            "created_at": self.created_at,
        }


def approve_execution(
    task_id: str,
    current_state: RuntimeState,
    actor: ActorIdentity,
    reason: str,
) -> tuple[RuntimeTransition, ApprovalRecord]:
    """Approve an execution waiting for human approval."""
    _require_approval_authority(actor)
    next_state = RuntimeState.COMPLETE
    runtime_transition = transition(current_state, next_state, reason)
    record = ApprovalRecord(
        task_id=task_id,
        decision=ApprovalDecision.APPROVE,
        actor=actor,
        reason=reason,
        previous_state=current_state,
        next_state=next_state,
    )
    return runtime_transition, record


def reject_execution(
    task_id: str,
    current_state: RuntimeState,
    actor: ActorIdentity,
    reason: str,
) -> tuple[RuntimeTransition, ApprovalRecord]:
    """Reject an execution waiting for human approval."""
    _require_approval_authority(actor)
    next_state = RuntimeState.BLOCKED
    runtime_transition = transition(current_state, next_state, reason)
    record = ApprovalRecord(
        task_id=task_id,
        decision=ApprovalDecision.REJECT,
        actor=actor,
        reason=reason,
        previous_state=current_state,
        next_state=next_state,
    )
    return runtime_transition, record


def _require_approval_authority(actor: ActorIdentity) -> None:
    if not can_make_approval_decision(actor):
        raise PermissionError(f"actor lacks approval authority: {actor.actor_id}")
