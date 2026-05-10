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
