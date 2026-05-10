# DETERMA Factory Runtime Runbook

Purpose:

Operate the Factory Runtime safely, inspect governance state, recover after restarts, and resolve approval decisions.

---

## Run Factory Tests

```bash
PYTHONPATH=. pytest tests/factory -q
```

Use this before changing runtime, replay gate, approval, recovery, or resume logic.

---

## Run One Governed Task

Safe execution:

```bash
python -m factory.runtime.cli run-once \
  --task-id PR-EXAMPLE \
  --task-name "safe docs change" \
  --changed-file docs/example.md \
  --allowed-file "docs/*" \
  --replay-json '{"severity":"LOW","trust_state":"TRUSTED"}'
```

Expected result:

```text
PASSED
```

---

## Trigger Approval Flow

Sensitive execution:

```bash
python -m factory.runtime.cli run-once \
  --task-id PR-APPROVAL \
  --task-name "auth change" \
  --changed-file src/auth.py \
  --allowed-file "src/*" \
  --replay-json '{"severity":"HIGH","trust_state":"TRUSTED"}'
```

Expected result:

```text
REQUIRES_APPROVAL
```

This creates a persisted approval request.

---

## List Approvals

```bash
python -m factory.runtime.cli approvals
```

Shows:

- pending approvals
- completed approvals
- decision reasons

---

## Approve Execution

```bash
python -m factory.runtime.cli approve \
  --task-id PR-APPROVAL \
  --decided-by reviewer \
  --reason "safe after review"
```

---

## Reject Execution

```bash
python -m factory.runtime.cli reject \
  --task-id PR-APPROVAL \
  --decided-by reviewer \
  --reason "unsafe after review"
```

---

## View Runtime Timeline

```bash
python -m factory.runtime.cli timeline
```

Shows persisted runtime events.

---

## View Metrics

```bash
python -m factory.runtime.cli metrics
```

Shows:

- pass rate
- blocked rate
- severity distribution
- trust-state distribution

---

## View Governance Dashboard

```bash
python -m factory.runtime.cli dashboard
```

Shows unified governance state:

- sessions
- runtime events
- approvals
- pass/block rates
- recent activity

---

## Recover After Restart

```bash
python -m factory.runtime.cli recovery
```

Shows reconstructed persisted state:

- runtime events
- sessions
- approvals
- pending approvals
- active sessions
- blocked events

---

## Build Resume Plan

```bash
python -m factory.runtime.cli resume-plan
```

Classifies sessions as:

- RESUMABLE
- REQUIRES_REVIEW
- BLOCKED
- ORPHANED

---

## Operating Rule

Do not resume execution automatically from recovered state.

Recovery must first produce a resume plan.

Only RESUMABLE sessions may continue automatically.

REQUIRES_REVIEW must go through approval.

BLOCKED and ORPHANED sessions must not continue without explicit manual handling.

---

## Current Runtime Boundary

The current Factory Runtime does not execute arbitrary shell commands.

It coordinates:

```text
Task
→ Scope Validation
→ Replay Gate
→ Approval Queue
→ Persistence
→ Recovery
→ Resume Planning
```

Actual code-writing workers remain outside this runtime boundary.
