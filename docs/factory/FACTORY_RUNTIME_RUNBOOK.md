# DETERMA Factory Runtime Runbook

Purpose:

Operate the Factory Runtime safely, inspect governance state, recover after restarts, resolve approval decisions, and understand adaptive governance outcomes.

---

## Runtime Principle

The Factory Runtime is not unrestricted autonomous execution.

It is a governed execution control layer.

Current execution path:

```text
Task
→ Scope Validation
→ Replay Gate
→ Risk Assessment
→ Governance Decision
→ Approval Queue / Complete / Block
→ Persistence
→ Recovery
→ Resume Planning
```

---

## Run Factory Tests

```bash
PYTHONPATH=. pytest tests/factory -q
```

Use this before changing runtime, replay gate, risk, policy, approval, recovery, resume, identity, or governance decision logic.

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

Why:

```text
LOW replay severity
+ TRUSTED state
+ low-risk docs surface
→ ALLOW_AUTONOMOUS
```

---

## Trigger Medium-Risk Review Flow

Auth-related change with LOW replay severity:

```bash
python -m factory.runtime.cli run-once \
  --task-id PR-MEDIUM-RISK \
  --task-name "auth docs or code change" \
  --changed-file src/auth.py \
  --allowed-file "src/*" \
  --replay-json '{"severity":"LOW","trust_state":"TRUSTED"}'
```

Expected result:

```text
REQUIRES_APPROVAL
```

Why:

```text
LOW replay severity
+ auth surface
→ MEDIUM risk
→ REQUIRE_REVIEW
```

This creates a persisted approval request.

---

## Trigger Security Review Flow

High-risk execution:

```bash
python -m factory.runtime.cli run-once \
  --task-id PR-SECURITY-REVIEW \
  --task-name "sensitive auth change" \
  --changed-file src/auth.py \
  --allowed-file "src/*" \
  --replay-json '{"severity":"HIGH","trust_state":"TRUSTED"}'
```

Expected result:

```text
REQUIRES_APPROVAL
```

Why:

```text
HIGH replay severity
+ auth surface
→ HIGH risk
→ REQUIRE_SECURITY_REVIEW
```

This creates a persisted approval request.

---

## Trigger Blocked Flow

Critical governance risk:

```bash
python -m factory.runtime.cli run-once \
  --task-id PR-CRITICAL \
  --task-name "critical secret change" \
  --changed-file secrets/prod_key.txt \
  --allowed-file "secrets/*" \
  --replay-json '{"severity":"HIGH","trust_state":"REQUIRES_APPROVAL"}'
```

Expected result:

```text
BLOCKED
```

Why:

```text
secret surface
+ HIGH severity
+ non-TRUSTED state
→ CRITICAL risk
→ DENY
```

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

Human reviewer approval:

```bash
python -m factory.runtime.cli approve \
  --task-id PR-MEDIUM-RISK \
  --decided-by reviewer \
  --actor-role HUMAN_REVIEWER \
  --reason "safe after review"
```

Security reviewer approval:

```bash
python -m factory.runtime.cli approve \
  --task-id PR-SECURITY-REVIEW \
  --decided-by security-reviewer \
  --actor-role SECURITY_REVIEWER \
  --reason "security approved"
```

Supported actor roles:

- HUMAN_REVIEWER
- SECURITY_REVIEWER
- ADMIN

---

## Reject Execution

```bash
python -m factory.runtime.cli reject \
  --task-id PR-SECURITY-REVIEW \
  --decided-by reviewer \
  --actor-role ADMIN \
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

## Risk Levels

The runtime currently classifies governance risk as:

- LOW
- MEDIUM
- HIGH
- CRITICAL

Risk signals include:

- replay severity
- trust state
- auth-related files
- deployment-related files
- secret-related files
- policy/governance files
- pending approvals
- blocked events
- orphaned sessions
- override attempts
- policy violations

---

## Governance Actions

Risk-aware governance decisions currently map to:

```text
LOW
→ ALLOW_AUTONOMOUS
```

```text
MEDIUM
→ REQUIRE_REVIEW
```

```text
HIGH
→ REQUIRE_SECURITY_REVIEW
```

```text
CRITICAL
→ DENY
```

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
→ Risk Assessment
→ Governance Decision
→ Approval Queue
→ Persistence
→ Recovery
→ Resume Planning
```

Actual code-writing workers remain outside this runtime boundary.
