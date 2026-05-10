from pathlib import Path

from factory.runtime.approval_queue import ApprovalQueue, ApprovalRequest, ApprovalStatus
from factory.runtime.approval_store import ApprovalStore


def test_approval_queue_persists_pending_request(tmp_path: Path):
    store = ApprovalStore(tmp_path / "approvals.json")
    queue = ApprovalQueue(store=store)

    queue.add_request(
        ApprovalRequest(
            task_id="PR-APP-T1",
            session_id="session-1",
            reason="approval required severity: HIGH",
            replay={"severity": "HIGH", "trust_state": "TRUSTED"},
        )
    )

    records = store.load()

    assert len(records) == 1
    assert records[0]["task_id"] == "PR-APP-T1"
    assert records[0]["status"] == "PENDING"
    assert records[0]["reason"] == "approval required severity: HIGH"


def test_approval_queue_persists_approved_request(tmp_path: Path):
    store = ApprovalStore(tmp_path / "approvals.json")
    queue = ApprovalQueue(store=store)

    queue.add_request(
        ApprovalRequest(
            task_id="PR-APP-T2",
            session_id="session-2",
            reason="approval required severity: HIGH",
        )
    )
    request = queue.approve(
        task_id="PR-APP-T2",
        decided_by="reviewer",
        reason="safe after review",
    )

    records = store.load()

    assert request.status == ApprovalStatus.APPROVED
    assert len(records) == 2
    assert records[-1]["status"] == "APPROVED"
    assert records[-1]["decided_by"] == "reviewer"
    assert records[-1]["decision_reason"] == "safe after review"


def test_approval_queue_persists_rejected_request(tmp_path: Path):
    store = ApprovalStore(tmp_path / "approvals.json")
    queue = ApprovalQueue(store=store)

    queue.add_request(
        ApprovalRequest(
            task_id="PR-APP-T3",
            session_id="session-3",
            reason="approval required severity: HIGH",
        )
    )
    request = queue.reject(
        task_id="PR-APP-T3",
        decided_by="reviewer",
        reason="unsafe after review",
    )

    records = store.load()

    assert request.status == ApprovalStatus.REJECTED
    assert len(records) == 2
    assert records[-1]["status"] == "REJECTED"
    assert records[-1]["decided_by"] == "reviewer"
    assert records[-1]["decision_reason"] == "unsafe after review"


def test_approval_store_filters_pending_and_completed(tmp_path: Path):
    store = ApprovalStore(tmp_path / "approvals.json")
    queue = ApprovalQueue(store=store)

    queue.add_request(ApprovalRequest(task_id="PENDING-TASK", session_id=None, reason="pending"))
    queue.add_request(ApprovalRequest(task_id="APPROVED-TASK", session_id=None, reason="pending"))
    queue.approve(task_id="APPROVED-TASK", decided_by="reviewer", reason="ok")

    pending = store.pending()
    completed = store.completed()

    assert any(record["task_id"] == "PENDING-TASK" for record in pending)
    assert any(record["task_id"] == "APPROVED-TASK" for record in completed)
