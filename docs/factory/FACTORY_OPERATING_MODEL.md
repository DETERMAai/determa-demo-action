# DETERMA Factory Operating Model

Status: Canonical  
Purpose: Keep autonomous development fast, bounded, and verifiable.

---

## Core Rule

The Factory does not build vision.

The Factory converts approved backlog items into small, testable, reversible pull requests.

---

## Execution Loop

```text
Backlog
→ Task Contract
→ Worker Implementation
→ Tests
→ DETERMA Replay
→ Review
→ Merge
→ Evaluation
→ Backlog Update
```

---

## Roles

### Orchestrator

Owns:

- backlog ordering
- task breakdown
- scope control
- acceptance criteria
- merge readiness

Must not:

- silently expand scope
- change core architecture without explicit approval
- merge unverified work

---

### Worker

Owns one small task.

May:

- edit allowed files
- add tests
- update docs within scope

Must not:

- touch files outside allowed scope
- change public contracts unless task says so
- add new dependencies without approval
- bypass tests

---

### Verifier

Checks:

- tests pass
- replay behavior is stable
- scope was respected
- no unrelated changes were added
- output matches acceptance criteria

---

## Autonomy Rules

Allowed autonomous work:

- replay UI improvements
- rule additions
- test additions
- corpus expansion
- demo artifacts
- docs updates
- renderer improvements

Requires explicit approval:

- architecture changes
- authority or enforcement logic
- permission model changes
- secrets handling
- external service integration
- dependency additions
- production deployment changes

---

## PR Rules

Every PR should be:

- small
- single-purpose
- test-backed
- reversible
- understandable in under 5 minutes

Large PRs should be split.

---

## Definition of Done

A task is done only when:

1. Required files were changed.
2. Tests were added or updated when relevant.
3. Replay behavior did not regress.
4. Acceptance criteria are satisfied.
5. No out-of-scope changes were made.

---

## Factory Metric

Primary metric:

```text
quality PRs completed per day without increasing system chaos
```

Not primary:

- lines of code
- number of documents
- feature count
