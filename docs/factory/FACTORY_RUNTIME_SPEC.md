# Factory Runtime Specification

Purpose:

Run the DETERMA Factory continuously and safely.

---

## Runtime Responsibilities

The runtime must:

1. load backlog items
2. prioritize executable tasks
3. generate worker tasks
4. dispatch workers
5. monitor execution
6. trigger replay verification
7. update task status
8. stop unsafe execution

---

## Runtime Flow

```text
Backlog
→ Task Selection
→ Task Generation
→ Worker Dispatch
→ Test Execution
→ Replay Verification
→ PR Creation
→ Status Update
```

---

## Runtime States

### IDLE

No executable tasks available.

---

### DISPATCHING

Generating and assigning worker tasks.

---

### EXECUTING

Worker actively modifying code.

---

### VERIFYING

Running tests and Replay validation.

---

### BLOCKED

Execution halted due to:

- failed tests
- replay block
- scope violation
- runtime error

---

### COMPLETE

Task finished successfully.

---

## Execution Constraints

The runtime must enforce:

- max concurrent workers
- task isolation
- branch isolation
- replay verification before merge
- rollback capability

---

## Failure Rules

Immediately stop execution if:

- forbidden files changed
- replay severity exceeds allowed threshold
- tests fail
- task scope expands unexpectedly
- worker crashes repeatedly

---

## Runtime Logging

Track:

- task duration
- replay latency
- worker success rate
- false positive rate
- replay usefulness
- blocked executions

---

## Core Principle

The Factory Runtime optimizes for:

```text
stable continuous execution
```

Never:

```text
unbounded autonomous behavior
```
