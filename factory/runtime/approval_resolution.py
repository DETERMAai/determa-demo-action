"""Factory approval resolution engine.

Resolves approval decisions for executions waiting in AWAITING_APPROVAL.
Connects authority-bound approval decisions to runtime transitions and session
lifecycle updates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from factory.runtime.approval import ApprovalRecord, approve_execution, reject_execution
from factory.runtime.approval_queue import ApprovalQueue, ApprovalRequest, ApprovalStatus
from factory.runtime.identity import ActorIdentity, human_reviewer
from factory.runtime.session import FactorySession
from factory.runtime.session_lifecycle import SessionLifecycleManager
from factory.runtime.state import RuntimeState, RuntimeTransition


@dataclass(frozen=True)
class ApprovalResolutionResult:
    task_id: str
    request: ApprovalRequest
    transition: RuntimeTransition
    approval_record: ApprovalRecord
    session: FactorySession | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "request": self.request.to_dict(),
            "transition": {
                "previous": self.transition.previous.value,
                "current": self.transition.current.value,
                "reason": self.transition.reason,
            },
            "approval_record": self.approval_record.to_dict(),
            "session": self.session.to_dict() if self.session else None,
        }


def resolve_approval(
    queue: ApprovalQueue,
    lifecycle: SessionLifecycleManager | None,
    task_id: str,
    approved: bool,
    decided_by: str,
    reason: str,
    session: FactorySession | None = None,
    actor: ActorIdentity | None = None,
) -> ApprovalResolutionResult:
    """Resolve a pending approval request.

    If approved, the runtime transition is AWAITING_APPROVAL -> COMPLETE.
    If rejected, the runtime transition is AWAITING_APPROVAL -> BLOCKED.

    The optional actor enables authority-bound decisions. If omitted, the legacy
    decided_by string is converted to a HUMAN_REVIEWER actor for compatibility.
    """
    decision_actor = actor or human_reviewer(decided_by)

    if approved:
        request = queue.approve(
            task_id=task_id,
            decided_by=decision_actor.actor_id,
            reason=reason,
        )
        transition, record = approve_execution(
            task_id=task_id,
            current_state=RuntimeState.AWAITING_APPROVAL,
            actor=decision_actor,
            reason=reason,
        )
        updated_session = (
            lifecycle.complete_session(session, request.replay)
            if lifecycle is not None and session is not None
            else session
        )
    else:
        request = queue.reject(
            task_id=task_id,
            decided_by=decision_actor.actor_id,
            reason=reason,
        )
        transition, record = reject_execution(
            task_id=task_id,
            current_state=RuntimeState.AWAITING_APPROVAL,
            actor=decision_actor,
            reason=reason,
        )
        updated_session = (
            lifecycle.block_session(session, request.replay)
            if lifecycle is not None and session is not None
            else session
        )

    return ApprovalResolutionResult(
        task_id=task_id,
        request=request,
        transition=transition,
        approval_record=record,
        session=updated_session,
    )


def is_pending_approval(request: ApprovalRequest) -> bool:
    """Return whether an approval request is still pending."""
    return request.status == ApprovalStatus.PENDING
