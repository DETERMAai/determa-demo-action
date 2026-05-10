from factory.runtime.approval_queue import ApprovalQueue, ApprovalRequest, ApprovalStatus
from factory.runtime.approval_resolution import resolve_approval
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
    assert queue.list_pending() == []
