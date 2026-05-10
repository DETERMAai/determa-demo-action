from pathlib import Path

from factory.runtime.git_workspace import build_change_set
from factory.runtime.session_lifecycle import SessionLifecycleManager
from factory.runtime.session_store import SessionStore


def test_session_lifecycle_starts_and_persists_session(tmp_path: Path):
    store = SessionStore(tmp_path / "sessions.json")
    lifecycle = SessionLifecycleManager(store=store)

    session = lifecycle.start_session(
        task_id="PR-104-T1",
        task_name="session lifecycle test",
        change_set=build_change_set(["src/app.py"]),
    )

    sessions = store.load()

    assert session.task_id == "PR-104-T1"
    assert session.state == "IDLE"
    assert len(sessions) == 1
    assert sessions[0]["task_id"] == "PR-104-T1"
    assert sessions[0]["branch_name"] == "factory/pr-104-t1-session-lifecycle-test"


def test_session_lifecycle_completes_session(tmp_path: Path):
    store = SessionStore(tmp_path / "sessions.json")
    lifecycle = SessionLifecycleManager(store=store)

    session = lifecycle.start_session(
        task_id="PR-104-T2",
        task_name="complete session",
        change_set=build_change_set(["docs/readme.md"]),
    )

    completed = lifecycle.complete_session(
        session=session,
        replay={"severity": "LOW", "trust_state": "TRUSTED"},
    )

    sessions = store.load()

    assert completed.state == "COMPLETE"
    assert completed.outcome == "PASSED"
    assert completed.replay == {"severity": "LOW", "trust_state": "TRUSTED"}
    assert len(sessions) == 2
    assert sessions[-1]["state"] == "COMPLETE"


def test_session_lifecycle_blocks_session(tmp_path: Path):
    store = SessionStore(tmp_path / "sessions.json")
    lifecycle = SessionLifecycleManager(store=store)

    session = lifecycle.start_session(
        task_id="PR-104-T3",
        task_name="block session",
        change_set=build_change_set(["src/deploy.py"]),
    )

    blocked = lifecycle.block_session(
        session=session,
        replay={"severity": "CRITICAL", "trust_state": "BLOCKED"},
    )

    sessions = store.load()

    assert blocked.state == "BLOCKED"
    assert blocked.outcome == "BLOCKED"
    assert blocked.replay == {"severity": "CRITICAL", "trust_state": "BLOCKED"}
    assert len(sessions) == 2
    assert sessions[-1]["state"] == "BLOCKED"
