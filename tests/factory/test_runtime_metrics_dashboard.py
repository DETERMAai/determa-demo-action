from factory.runtime.dashboard_data import build_dashboard_data, render_dashboard_summary
from factory.runtime.metrics import compute_runtime_metrics, render_runtime_metrics


def test_runtime_metrics_computes_pass_and_block_rates():
    events = [
        {
            "task_id": "T1",
            "outcome": "PASSED",
            "replay": {"severity": "LOW", "trust_state": "TRUSTED"},
        },
        {
            "task_id": "T2",
            "outcome": "BLOCKED",
            "replay": {"severity": "CRITICAL", "trust_state": "BLOCKED"},
        },
    ]

    metrics = compute_runtime_metrics(events)

    assert metrics.total_events == 2
    assert metrics.passed_events == 1
    assert metrics.blocked_events == 1
    assert metrics.pass_rate == 0.5
    assert metrics.blocked_rate == 0.5
    assert metrics.severity_distribution == {"CRITICAL": 1, "LOW": 1}
    assert metrics.trust_state_distribution == {"BLOCKED": 1, "TRUSTED": 1}


def test_runtime_metrics_handles_empty_events():
    metrics = compute_runtime_metrics([])

    assert metrics.total_events == 0
    assert metrics.pass_rate == 0.0
    assert metrics.blocked_rate == 0.0
    assert metrics.severity_distribution == {}
    assert metrics.trust_state_distribution == {}


def test_render_runtime_metrics_outputs_markdown():
    metrics = compute_runtime_metrics([
        {
            "task_id": "T1",
            "outcome": "PASSED",
            "replay": {"severity": "LOW", "trust_state": "TRUSTED"},
        }
    ])

    rendered = render_runtime_metrics(metrics)

    assert "# DETERMA Factory Runtime Metrics" in rendered
    assert "Total Events: 1" in rendered
    assert "Pass Rate: 100.00%" in rendered
    assert "- LOW: 1" in rendered


def test_dashboard_data_aggregates_sessions_and_events():
    sessions = [
        {"task_id": "T1", "outcome": "PASSED", "branch_name": "factory/t1"},
        {"task_id": "T2", "outcome": "BLOCKED", "branch_name": "factory/t2"},
    ]
    events = [
        {
            "task_id": "T1",
            "outcome": "PASSED",
            "reason": "ok",
            "replay": {"severity": "LOW", "trust_state": "TRUSTED"},
        },
        {
            "task_id": "T2",
            "outcome": "BLOCKED",
            "reason": "blocked severity: CRITICAL",
            "replay": {"severity": "CRITICAL", "trust_state": "BLOCKED"},
        },
    ]

    dashboard = build_dashboard_data(sessions=sessions, events=events)

    assert dashboard.total_sessions == 2
    assert dashboard.completed_sessions == 1
    assert dashboard.blocked_sessions == 1
    assert dashboard.runtime_metrics.blocked_rate == 0.5
    assert len(dashboard.recent_sessions) == 2
    assert len(dashboard.recent_events) == 2


def test_render_dashboard_summary_outputs_operational_overview():
    dashboard = build_dashboard_data(
        sessions=[{"task_id": "T1", "outcome": "PASSED", "branch_name": "factory/t1"}],
        events=[{"task_id": "T1", "outcome": "PASSED", "reason": "ok"}],
    )

    rendered = render_dashboard_summary(dashboard)

    assert "# DETERMA Factory Dashboard" in rendered
    assert "Total Sessions: 1" in rendered
    assert "Completed Sessions: 1" in rendered
    assert "Runtime Pass Rate: 100.00%" in rendered
    assert "PASSED — T1 — factory/t1" in rendered
