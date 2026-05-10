# Factory Task Generator

Purpose:

Convert backlog epics into small bounded executable worker tasks.

---

## Input

Example:

```yaml
Epic:
  name: Replay Reliability
  goal: Reduce replay noise and improve trust
```

---

## Output

Example:

```yaml
- task_id: PR-47-T1
  name: add-noise-filter

- task_id: PR-47-T2
  name: stabilize-replay-format

- task_id: PR-47-T3
  name: add-replay-consistency-tests
```

---

## Task Generation Rules

Every generated task must be:

- small
- testable
- reversible
- single-purpose
- scoped to limited files

---

## Hard Limits

A task must NOT:

- modify architecture
- add dependencies
- exceed intended scope
- modify unrelated files
- bypass tests

---

## Preferred Task Size

Ideal task:

- 1 feature
- 1 responsibility
- under ~200 LOC changed
- understandable in under 5 minutes

---

## Task Categories

### Replay UI

- replay cards
- badges
- focus mode
- replay formatting

### Replay Rules

- auth detection
- deployment detection
- secrets detection
- rollout escalation

### Replay Evaluation

- false positive tracking
- replay scoring
- replay timing

### Distribution

- screenshots
- GIFs
- demos
- replay gallery

---

## Verification Requirements

Every generated task must include:

- tests required
- replay validation
- acceptance criteria
- rollback strategy

---

## Factory Principle

The Factory should optimize for:

```text
continuous stable execution
```

Not:

```text
large intelligent autonomous leaps
```
