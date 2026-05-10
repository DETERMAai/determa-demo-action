from pathlib import Path

from factory.runtime.approval_queue import ApprovalQueue, ApprovalRequest
from factory.runtime.approval_store import ApprovalStore
from factory.runtime.cli import main


def test_cli_approvals_handles_empty_store(tmp_path: Path, capsys):
    approvals = tmp_path / "approvals.json"

    exit_code = main(["approvals", "--approvals", str(approvals)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# DETERMA Factory Approvals" in captured.out
    assert "Pending: 0" in captured.out
    assert "Completed: 0" in captured.out
    assert "- none" in captured.out


def test_cli_approvals_renders_pending_and_completed(tmp_path: Path, capsys):
    approvals = tmp_path / "approvals.json"
    store = ApprovalStore(approvals)
    queue = ApprovalQueue(store=store)

    queue.add_request(
        ApprovalRequest(
            task_id="PR-APP-CLI-PENDING",
            session_id="session-pending",
            reason="approval required severity: HIGH",
            replay={"severity": "HIGH", "trust_state": "TRUSTED"},
        )
    )
    queue.add_request(
        ApprovalRequest(
            task_id="PR-APP-CLI-APPROVED",
            session_id="session-approved",
            reason="approval required severity: HIGH",
        )
    )
    queue.approve(
        task_id="PR-APP-CLI-APPROVED",
        decided_by="reviewer",
        reason="approved after review",
    )

    exit_code = main(["approvals", "--approvals", str(approvals)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Pending: 1" in captured.out
    assert "Completed: 1" in captured.out
    assert "PR-APP-CLI-PENDING" in captured.out
    assert "APPROVED — PR-APP-CLI-APPROVED — approved after review" in captured.out


def test_cli_approve_persists_decision(tmp_path: Path, capsys):
    approvals = tmp_path / "approvals.json"
    store = ApprovalStore(approvals)
    queue = ApprovalQueue(store=store)
    queue.add_request(
        ApprovalRequest(
            task_id="PR-APP-CLI-APPROVE",
            session_id="session-approve",
            reason="approval required severity: HIGH",
        )
    )

    exit_code = main([
        "approve",
        "--approvals",
        str(approvals),
        "--task-id",
        "PR-APP-CLI-APPROVE",
        "--decided-by",
        "reviewer",
        "--reason",
        "safe after review",
    ])

    captured = capsys.readouterr()
    records = store.load()
    assert exit_code == 0
    assert "Approved PR-APP-CLI-APPROVE by reviewer (HUMAN_REVIEWER): safe after review" in captured.out
    assert records[-1]["status"] == "APPROVED"
    assert records[-1]["decided_by"] == "reviewer"
    assert records[-1]["decision_reason"] == "safe after review"


def test_cli_approve_supports_security_reviewer_role(tmp_path: Path, capsys):
    approvals = tmp_path / "approvals.json"
    store = ApprovalStore(approvals)
    queue = ApprovalQueue(store=store)
    queue.add_request(
        ApprovalRequest(
            task_id="PR-APP-CLI-SECURITY",
            session_id="session-security",
            reason="approval required severity: HIGH",
        )
    )

    exit_code = main([
        "approve",
        "--approvals",
        str(approvals),
        "--task-id",
        "PR-APP-CLI-SECURITY",
        "--decided-by",
        "security-reviewer",
        "--actor-role",
        "SECURITY_REVIEWER",
        "--reason",
        "security approved",
    ])

    captured = capsys.readouterr()
    records = store.load()
    assert exit_code == 0
    assert "Approved PR-APP-CLI-SECURITY by security-reviewer (SECURITY_REVIEWER): security approved" in captured.out
    assert records[-1]["status"] == "APPROVED"
    assert records[-1]["decided_by"] == "security-reviewer"


def test_cli_reject_persists_decision(tmp_path: Path, capsys):
    approvals = tmp_path / "approvals.json"
    store = ApprovalStore(approvals)
    queue = ApprovalQueue(store=store)
    queue.add_request(
        ApprovalRequest(
            task_id="PR-APP-CLI-REJECT",
            session_id="session-reject",
            reason="approval required severity: HIGH",
        )
    )

    exit_code = main([
        "reject",
        "--approvals",
        str(approvals),
        "--task-id",
        "PR-APP-CLI-REJECT",
        "--decided-by",
        "reviewer",
        "--actor-role",
        "ADMIN",
        "--reason",
        "unsafe after review",
    ])

    captured = capsys.readouterr()
    records = store.load()
    assert exit_code == 0
    assert "Rejected PR-APP-CLI-REJECT by reviewer (ADMIN): unsafe after review" in captured.out
    assert records[-1]["status"] == "REJECTED"
    assert records[-1]["decided_by"] == "reviewer"
    assert records[-1]["decision_reason"] == "unsafe after review"


def test_cli_approve_missing_task_returns_error(tmp_path: Path, capsys):
    approvals = tmp_path / "approvals.json"

    exit_code = main([
        "approve",
        "--approvals",
        str(approvals),
        "--task-id",
        "MISSING-TASK",
    ])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "approval request not found: MISSING-TASK" in captured.out
