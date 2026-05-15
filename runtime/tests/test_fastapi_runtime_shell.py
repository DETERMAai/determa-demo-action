from __future__ import annotations

from fastapi.testclient import TestClient

from runtime.api_shell import app


def test_health_endpoint_reports_ledger_counts(tmp_path, monkeypatch):
    db_path = str(tmp_path / "runtime-shell-health.db")
    monkeypatch.setenv("DETERMA_DB_PATH", db_path)

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["db_path"] == db_path
    assert payload["event_count"] == 0
    assert payload["receipt_count"] == 0


def test_replay_endpoint_exposes_existing_runtime_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("DETERMA_DB_PATH", str(tmp_path / "runtime-shell-replay.db"))
    client = TestClient(app)

    response = client.get("/runtime/replay")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["event_count"] == 0
    assert payload["receipt_count"] == 0
    assert payload["errors"] == []


def test_orchestrator_run_once_endpoint_is_thin_passthrough(tmp_path, monkeypatch):
    monkeypatch.setenv("DETERMA_DB_PATH", str(tmp_path / "runtime-shell-run-once.db"))
    client = TestClient(app)

    response = client.post(
        "/runtime/orchestrator/run-once",
        json={"now_timestamp": "2026-01-01T00:00:00.000000"},
    )

    assert response.status_code == 200
    assert response.json() == {"processed": 0}


def test_recovery_endpoint_returns_replay_and_lock_recovery(tmp_path, monkeypatch):
    monkeypatch.setenv("DETERMA_DB_PATH", str(tmp_path / "runtime-shell-recover.db"))
    client = TestClient(app)

    response = client.post(
        "/runtime/recovery/recover",
        json={"now_timestamp": "2026-01-01T00:00:00.000000"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["replay"]["valid"] is True
    assert payload["locks"]["scanned_active_count"] == 0
    assert payload["locks"]["recovered_count"] == 0
    assert payload["locks"]["recovered_mutation_ids"] == []


def test_notebook_cta_rendering(tmp_path, monkeypatch):
    monkeypatch.setenv("DETERMA_DB_PATH", str(tmp_path / "runtime-shell-demo.db"))
    client = TestClient(app)

    response = client.get("/demo")
    autoplay = client.get("/demo/autoplay")

    assert response.status_code == 200
    assert autoplay.status_code == 200
    assert "Runtime Contradiction Demo" in response.text
    assert "Run demonstration" in response.text
    assert "AI proposes mutation" in response.text
    assert "Human approval granted" in response.text
    assert "Execution authorized" in response.text
    assert "AUTHORIZATION CONTEXT" in response.text
    assert "repo_state          A17F" in response.text
    assert "dependency_graph    D44C" in response.text
    assert "runtime_epoch       1021" in response.text
    assert "CURRENT RUNTIME" in response.text
    assert "repo_state          B92K" in response.text
    assert "dependency_graph    E11X" in response.text
    assert "runtime_epoch       1048" in response.text
    assert "Execution resumed using historical authorization" in response.text
    assert "Mutation applied" in response.text
    assert "Authorization context no longer valid for current runtime" in response.text
    assert "The approval remained." in response.text
    assert "The system changed." in response.text
    assert "DETERMA re-evaluates legitimacy at execution time." in response.text


def test_suggested_questions_rendering(tmp_path, monkeypatch):
    monkeypatch.setenv("DETERMA_DB_PATH", str(tmp_path / "runtime-shell-suggested-questions.db"))
    client = TestClient(app)

    response = client.get("/demo")

    assert response.status_code == 200
    assert "Mutation applied" in response.text
    assert "Authorization context no longer valid for current runtime" in response.text


def test_serialization_compatibility(tmp_path, monkeypatch):
    monkeypatch.setenv("DETERMA_DB_PATH", str(tmp_path / "runtime-shell-serialization.db"))
    client = TestClient(app)

    autoplay = client.get("/demo/autoplay")

    assert autoplay.status_code == 200
    payload = autoplay.json()
    assert payload["autoplay"] is False
    assert payload["requires_cta"] is True
    assert payload["run_route"] == "/demo/run"
    assert payload["status_route"] == "/demo/status"
    assert isinstance(payload["stage_delay_ms"], list)
    assert isinstance(payload["overlay_visible_ms"], int)
