# Crash Recovery Example

## Purpose

This example demonstrates fail-closed runtime recovery.

The runtime validates:

- stale execution lock detection
- interruption recovery
- deterministic lifecycle replay
- single execution continuity after recovery

---

## Execute

```bash
python -m runtime.recovery_runtime
```

---

## Expected Runtime Behavior

```text
STALE EXECUTION DETECTED
RECOVERY APPLIED
REPLAY VERIFIED
EXECUTION CONTINUITY RESTORED
```

---

## What This Proves

The runtime can recover from interruption without violating append-only lineage or replay correctness.
