from pathlib import Path

from factory.runtime.cli import main


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

    exit_code = main([
        "dashboard",
        "--history",
        str(history),
        "--sessions",
        str(sessions),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# DETERMA Factory Dashboard" in captured.out
    assert "Total Sessions: 0" in captured.out


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
