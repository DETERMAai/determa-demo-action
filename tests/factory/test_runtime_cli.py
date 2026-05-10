from pathlib import Path

from factory.runtime.approval_queue import ApprovalQueue, ApprovalRequest
from factory.runtime.approval_store import ApprovalStore
from factory.runtime.cli import main
from factory.runtime.git_workspace import build_change_set
from factory.runtime.persistence import RuntimeEvent, RuntimeStore
from factory.runtime.session import create_session
from factory.runtime.session_store import SessionStore


def test_cli_metrics_handles_empty_history(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"

    exit_code = main(["metrics", "--history", str(history)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# DETERMA Factory Runtime Metrics" in captured.out
    assert "Total Events: 0" in captured.out


def test_cli_timeline_handles_empty_history(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"

    exit_code = main(["timeline", "--history", str(history)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# DETERMA Factory Runtime Timeline" in captured.out
    assert "No runtime events recorded." in captured.out


def test_cli_dashboard_handles_empty_history(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"
    sessions = tmp_path / "sessions.json"
    approvals = tmp_path / "approvals.json"

    exit_code = main([
        "dashboard",
        "--history",
        str(history),
        "--sessions",
        str(sessions),
        "--approvals",
        str(approvals),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# DETERMA Factory Dashboard" in captured.out
    assert "Total Sessions: 0" in captured.out
    assert "Pending Approvals: 0" in captured.out
    assert "Completed Approvals: 0" in captured.out


def test_cli_dashboard_renders_approval_state(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"
    sessions = tmp_path / "sessions.json"
    approvals = tmp_path / "approvals.json"
    store = ApprovalStore(approvals)
    queue = ApprovalQueue(store=store)

    queue.add_request(
        ApprovalRequest(
            task_id="PR-CLI-APPROVAL-PENDING",
            session_id="session-pending",
            reason="approval required severity: HIGH",
        )
    )
    queue.add_request(
        ApprovalRequest(
            task_id="PR-CLI-APPROVAL-APPROVED",
            session_id="session-approved",
            reason="approval required severity: HIGH",
        )
    )
    queue.approve(
        task_id="PR-CLI-APPROVAL-APPROVED",
        decided_by="reviewer",
        reason="safe after review",
    )

    exit_code = main([
        "dashboard",
        "--history",
        str(history),
        "--sessions",
        str(sessions),
        "--approvals",
        str(approvals),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Pending Approvals: 1" in captured.out
    assert "Completed Approvals: 1" in captured.out
    assert "PENDING — PR-CLI-APPROVAL-PENDING — approval required severity: HIGH" in captured.out
    assert "APPROVED — PR-CLI-APPROVAL-APPROVED — approval required severity: HIGH" in captured.out


def test_cli_recovery_outputs_recovered_summary(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"
    sessions = tmp_path / "sessions.json"
    approvals = tmp_path / "approvals.json"

    RuntimeStore(history).append(
        RuntimeEvent(
            event_id="evt-1",
            task_id="REC-BLOCKED",
            state="BLOCKED",
            outcome="BLOCKED",
            reason="blocked severity: CRITICAL",
        )
    )

    SessionStore(sessions).append(
        create_session(
            task_id="REC-ACTIVE",
            task_name="active recovery task",
            change_set=build_change_set(["src/app.py"]),
        )
    )

    ApprovalQueue(store=ApprovalStore(approvals)).add_request(
        ApprovalRequest(
            task_id="REC-APPROVAL",
            session_id="session-rec-approval",
            reason="approval required severity: HIGH",
        )
    )

    exit_code = main([
        "recovery",
        "--history",
        str(history),
        "--sessions",
        str(sessions),
        "--approvals",
        str(approvals),
    ])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "# DETERMA Factory Runtime Recovery" in captured.out
    assert "Total Events: 1" in captured.out
    assert "Total Sessions: 1" in captured.out
    assert "Pending Approvals: 1" in captured.out
    assert "Blocked Events: 1" in captured.out


def test_cli_resume_plan_outputs_resume_classification(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"
    sessions = tmp_path / "sessions.json"
    approvals = tmp_path / "approvals.json"

    SessionStore(sessions).append(
        create_session(
            task_id="RESUME-ACTIVE",
            task_name="active resume task",
            change_set=build_change_set(["src/app.py"]),
        )
    )

    SessionStore(sessions).append(
        create_session(
            task_id="RESUME-REVIEW",
            task_name="review resume task",
            change_set=build_change_set(["src/auth.py"]),
        )
    )

    ApprovalQueue(store=ApprovalStore(approvals)).add_request(
        ApprovalRequest(
            task_id="RESUME-REVIEW",
            session_id="session-review",
            reason="approval required severity: HIGH",
        )
    )

    exit_code = main([
        "resume-plan",
        "--history",
        str(history),
        "--sessions",
        str(sessions),
        "--approvals",
        str(approvals),
    ])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "# DETERMA Factory Resume Plan" in captured.out
    assert "## RESUME-ACTIVE" in captured.out
    assert "Status: RESUMABLE" in captured.out
    assert "## RESUME-REVIEW" in captured.out
    assert "Status: REQUIRES_REVIEW" in captured.out


def test_cli_run_once_passes_safe_task(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"

    exit_code = main([
        "run-once",
        "--history",
        str(history),
        "--task-id",
        "PR-CLI-T1",
        "--task-name",
        "safe cli task",
        "--changed-file",
        "docs/readme.md",
        "--allowed-file",
        "docs/*",
        "--replay-json",
        '{"severity":"LOW","trust_state":"TRUSTED"}',
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Task PR-CLI-T1: PASSED" in captured.out
    assert history.exists()


def test_cli_run_once_blocks_scope_violation(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"

    exit_code = main([
        "run-once",
        "--history",
        str(history),
        "--task-id",
        "PR-CLI-T2",
        "--task-name",
        "blocked cli task",
        "--changed-file",
        "secrets/token.txt",
        "--allowed-file",
        "docs/*",
        "--forbidden-file",
        "secrets/*",
        "--replay-json",
        '{"severity":"LOW","trust_state":"TRUSTED"}',
    ])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Task PR-CLI-T2: BLOCKED" in captured.out
    assert history.exists()


def test_cli_run_once_persists_security_review_approval(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"
    approvals = tmp_path / "approvals.json"

    exit_code = main([
        "run-once",
        "--history",
        str(history),
        "--approvals",
        str(approvals),
        "--task-id",
        "PR-CLI-T3",
        "--task-name",
        "approval cli task",
        "--changed-file",
        "src/auth.py",
        "--allowed-file",
        "src/*",
        "--replay-json",
        '{"severity":"HIGH","trust_state":"TRUSTED"}',
    ])

    captured = capsys.readouterr()
    records = ApprovalStore(approvals).load()

    assert exit_code == 0
    assert "Task PR-CLI-T3: REQUIRES_APPROVAL" in captured.out
    assert "Replay Gate: REQUIRES_APPROVAL" in captured.out
    assert approvals.exists()
    assert len(records) == 1
    assert records[0]["task_id"] == "PR-CLI-T3"
    assert records[0]["status"] == "PENDING"
    assert records[0]["reason"] == "approval required severity: HIGH"


def test_cli_run_once_persists_medium_risk_review_approval(tmp_path: Path, capsys):
    history = tmp_path / "runtime_events.json"
    approvals = tmp_path / "approvals.json"

    exit_code = main([
        "run-once",
        "--history",
        str(history),
        "--approvals",
        str(approvals),
        "--task-id",
        "PR-CLI-T4",
        "--task-name",
        "medium risk cli task",
        "--changed-file",
        "src/auth.py",
        "--allowed-file",
        "src/*",
        "--replay-json",
        '{"severity":"LOW","trust_state":"TRUSTED"}',
    ])

    captured = capsys.readouterr()
    records = ApprovalStore(approvals).load()

    assert exit_code == 0
    assert "Task PR-CLI-T4: REQUIRES_APPROVAL" in captured.out
    assert approvals.exists()
    assert len(records) == 1
    assert records[0]["task_id"] == "PR-CLI-T4"
    assert records[0]["status"] == "PENDING"
    assert records[0]["reason"] == "medium risk execution requires human review"
