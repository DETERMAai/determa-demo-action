# DETERMA

> Deterministic governed execution infrastructure for AI systems.

DETERMA verifies whether AI-driven execution is authorized, replayable, recoverable, append-only traceable, and deterministically reproducible.

---

## Status

```text
Local validation: 213 passed, 1 skipped
Runtime validation: 52 passed, 1 skipped
Container runtime validation: 52 passed, 1 skipped
```

The single skipped test is the credential-gated remote GitHub API governance validation.

---

## What is implemented

This repository contains an executable governed runtime baseline:

```text
runtime/
  replay.py
  recovery_runtime.py
  orchestrator_loop.py
  api_shell.py
  proof_inspector.py
  lineage_viewer.py
  runtime_visualizer.py
  tests/

receipts/
  runtime_proof_snapshot.json
  canonical_release_baseline.json
  release_lineage.jsonl

scripts/
  validate_runtime.sh

Dockerfile
docker-compose.runtime.yml
```

---

## Runtime guarantees verified

| Guarantee | Status |
|---|---|
| Deterministic replay | Verified |
| Append-only lineage | Verified |
| Replay prevention | Verified |
| Fail-closed authority checks | Verified |
| Crash recovery | Verified |
| Cross-process coordination | Verified |
| Corruption detection | Verified |
| Restoration equivalence | Verified |
| Container parity | Verified |

---

## Quickstart

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run runtime validation:

```bash
python -m pytest runtime/tests -v
```

Run the API shell:

```bash
uvicorn runtime.api_shell:app --host 0.0.0.0 --port 8000
```

Run container validation:

```bash
docker build -t determa-runtime-shell:test .
docker run --rm determa-runtime-shell:test ./scripts/validate_runtime.sh
```

---

## Runtime API shell

The FastAPI shell is intentionally thin. It delegates to the existing runtime functions and does not reimplement governance semantics.

Available endpoints:

```text
GET  /health
GET  /runtime/replay
GET  /runtime/lifecycle/replay
POST /runtime/orchestrator/run-once
POST /runtime/recovery/recover
```

---

## Runtime model

```text
VERIFY -> AUTHORIZE -> EXECUTE -> PERSIST -> REPLAY -> RESTORE
```

DETERMA intentionally avoids hidden governance, in-memory trust assumptions, fake replay semantics, mutable audit history, and approval-only security theater.

---

## Public scope

This repository demonstrates a governed execution runtime kernel.

It does not yet claim:

- production-scale infrastructure guarantees
- universal agent orchestration
- full distributed authority federation
- complete multi-system governance coverage

The current focus is a strict, executable governed runtime baseline.

---

## Documentation

- [Quickstart](docs/QUICKSTART.md)
- [Release signing](docs/RELEASE_SIGNING.md)
- [Live runtime outputs](docs/LIVE_RUNTIME_OUTPUTS.md)
- [Roadmap](ROADMAP.md)
- [Security](SECURITY.md)

---

## Category

```text
Governed Execution Infrastructure
```

Core reflex:

```text
Before trusting AI execution, verify the runtime lineage.
```
