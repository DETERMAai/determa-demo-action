from pathlib import Path

from factory.runtime.approval_queue import ApprovalQueue, ApprovalRequest
from factory.runtime.approval_store import ApprovalStore
from factory.runtime.git_workspace import build_change_set
from factory.runtime.persistence import RuntimeEvent, RuntimeStore
from factory.runtime.recovery import recover_runtime_state, render_recovery_summary, summarize_recovery_state
from factory.runtime.resume import ResumeStatus, build_resume_plan, render_resume_plan
from factory.runtime.session import create_session, with_runtime_result
from factory.runtime.session_store import SessionStore


def test_recovery_reconstructs_persisted_state(tmp_path: Path):
    history_path = tmp_path / "runtime_events.json"
    sessions_path = tmp_path / "sessions.json"
    approvals_path = tmp_path / "approvals.json"

    RuntimeStore(history_path).append(
        RuntimeEvent(
            event_id="evt-1",
            task_id="T-BLOCKED",
            state="BLOCKED",
            outcome="BLOCKED",
            reason="blocked severity: CRITICAL",
        )
    )

    session_store = SessionStore(sessions_path)
    session_store.append(
        create_session(
            task_id="T-ACTIVE",
            task_name="active task",
            change_set=build_change_set(["src/app.py"]),
        )
    )

    approval_queue = ApprovalQueue(store=ApprovalStore(approvals_path))
    approval_queue.add_request(
        ApprovalRequest(
            task_id="T-APPROVAL",
            session_id="session-approval",
            reason="approval required severity: HIGH",
        )
    )

    state = recover_runtime_state(
        history_path=history_path,
        sessions_path=sessions_path,
        approvals_path=approvals_path,
    )
    summary = summarize_recovery_state(state)

    assert summary.total_events == 1
    assert summary.total_sessions == 1
    assert summary.total_approvals == 1
    assert summary.pending_approvals == 1
    assert summary.active_sessions == 1
    assert summary.blocked_events == 1


def test_render_recovery_summary_outputs_markdown():
    summary = summarize_recovery_state(
        recover_runtime_state(
            history_path=Path("/tmp/nonexistent-runtime-events.json"),
            sessions_path=Path("/tmp/nonexistent-sessions.json"),
            approvals_path=Path("/tmp/nonexistent-approvals.json"),
        )
    )

    rendered = render_recovery_summary(summary)

    assert "# DETERMA Factory Runtime Recovery" in rendered
    assert "Total Events: 0" in rendered
    assert "Pending Approvals: 0" in rendered


def test_resume_plan_marks_pending_approval_as_requires_review():
    session = create_session(
        task_id="T-REVIEW",
        task_name="review task",
        change_set=build_change_set(["src/auth.py"]),
    ).to_dict()

    plan = build_resume_plan(
        sessions=[session],
        pending_approvals=[{"task_id": "T-REVIEW", "status": "PENDING"}],
        blocked_events=[],
    )

    assert plan.decisions[0].status == ResumeStatus.REQUIRES_REVIEW
    assert plan.decisions[0].reasons == ("pending approval exists",)


def test_resume_plan_marks_blocked_event_as_blocked():
    session = create_session(
        task_id="T-BLOCKED",
        task_name="blocked task",
        change_set=build_change_set(["src/deploy.py"]),
    ).to_dict()

    plan = build_resume_plan(
        sessions=[session],
        pending_approvals=[],
        blocked_events=[{"task_id": "T-BLOCKED", "outcome": "BLOCKED"}],
    )

    assert plan.decisions[0].status == ResumeStatus.BLOCKED
    assert plan.decisions[0].reasons == ("blocked runtime event exists",)


def test_resume_plan_marks_active_session_as_resumable():
    session = create_session(
        task_id="T-RESUME",
        task_name="resume task",
        change_set=build_change_set(["src/app.py"]),
    ).to_dict()

    plan = build_resume_plan(
        sessions=[session],
        pending_approvals=[],
        blocked_events=[],
    )

    assert plan.decisions[0].status == ResumeStatus.RESUMABLE
    assert plan.decisions[0].reasons == ("resume conditions satisfied",)


def test_resume_plan_marks_terminal_session_as_orphaned():
    session = create_session(
        task_id="T-DONE",
        task_name="done task",
        change_set=build_change_set(["docs/readme.md"]),
    )
    terminal = with_runtime_result(
        session=session,
        replay={"severity": "LOW", "trust_state": "TRUSTED"},
        outcome="PASSED",
        state="COMPLETE",
    ).to_dict()

    plan = build_resume_plan(
        sessions=[terminal],
        pending_approvals=[],
        blocked_events=[],
    )

    assert plan.decisions[0].status == ResumeStatus.ORPHANED
    assert plan.decisions[0].reasons == ("terminal session state: COMPLETE",)


def test_render_resume_plan_outputs_markdown():
    plan = build_resume_plan(
        sessions=[
            create_session(
                task_id="T-RESUME",
                task_name="resume task",
                change_set=build_change_set(["src/app.py"]),
            ).to_dict()
        ],
        pending_approvals=[],
        blocked_events=[],
    )

    rendered = render_resume_plan(plan)

    assert "# DETERMA Factory Resume Plan" in rendered
    assert "## T-RESUME" in rendered
    assert "Status: RESUMABLE" in rendered
