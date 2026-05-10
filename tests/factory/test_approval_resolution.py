import pytest

from factory.runtime.approval_queue import ApprovalQueue, ApprovalRequest, ApprovalStatus
from factory.runtime.approval_resolution import resolve_approval
from factory.runtime.identity import GovernanceRole, DecisionAuthority, human_reviewer, system_actor
from factory.runtime.state import RuntimeState


def test_resolve_approval_marks_request_approved():
    queue = ApprovalQueue()
    queue.add_request(
        ApprovalRequest(
            task_id="PR-102-T1",
            session_id=None,
            reason="approval required severity: HIGH",
            replay={"severity": "HIGH", "trust_state": "TRUSTED"},
        )
    )

    result = resolve_approval(
        queue=queue,
        lifecycle=None,
        task_id="PR-102-T1",
        approved=True,
        decided_by="human-reviewer",
        reason="approved after manual review",
    )

    assert result.request.status == ApprovalStatus.APPROVED
    assert result.transition.previous == RuntimeState.AWAITING_APPROVAL
    assert result.transition.current == RuntimeState.COMPLETE
    assert result.approval_record.decided_by == "human-reviewer"
    assert result.approval_record.actor.role == GovernanceRole.HUMAN_REVIEWER
    assert result.approval_record.actor.authority == DecisionAuthority.REVIEW
    assert queue.list_pending() == []


def test_resolve_approval_marks_request_rejected():
    queue = ApprovalQueue()
    queue.add_request(
        ApprovalRequest(
            task_id="PR-102-T2",
            session_id=None,
            reason="approval required severity: HIGH",
            replay={"severity": "HIGH", "trust_state": "TRUSTED"},
        )
    )

    result = resolve_approval(
        queue=queue,
        lifecycle=None,
        task_id="PR-102-T2",
        approved=False,
        decided_by="human-reviewer",
        reason="rejected after manual review",
    )

    assert result.request.status == ApprovalStatus.REJECTED
    assert result.transition.previous == RuntimeState.AWAITING_APPROVAL
    assert result.transition.current == RuntimeState.BLOCKED
    assert result.approval_record.reason == "rejected after manual review"
    assert result.approval_record.actor.role == GovernanceRole.HUMAN_REVIEWER
    assert queue.list_pending() == []


def test_resolve_approval_accepts_explicit_actor_identity():
    queue = ApprovalQueue()
    queue.add_request(
        ApprovalRequest(
            task_id="PR-102-T3",
            session_id=None,
            reason="approval required severity: HIGH",
        )
    )
    actor = human_reviewer("reviewer-123", display_name="Reviewer 123")

    result = resolve_approval(
        queue=queue,
        lifecycle=None,
        task_id="PR-102-T3",
        approved=True,
        decided_by="legacy-reviewer",
        reason="approved with explicit actor",
        actor=actor,
    )

    assert result.approval_record.actor.actor_id == "reviewer-123"
    assert result.approval_record.actor.display_name == "Reviewer 123"
    assert result.request.decided_by == "reviewer-123"


def test_resolve_approval_rejects_actor_without_authority():
    queue = ApprovalQueue()
    queue.add_request(
        ApprovalRequest(
            task_id="PR-102-T4",
            session_id=None,
            reason="approval required severity: HIGH",
        )
    )

    with pytest.raises(PermissionError, match="actor lacks approval authority"):
        resolve_approval(
            queue=queue,
            lifecycle=None,
            task_id="PR-102-T4",
            approved=True,
            decided_by="system",
            reason="system cannot approve",
            actor=system_actor(),
        )
