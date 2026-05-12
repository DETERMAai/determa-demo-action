# Replay Validation Example

## Purpose

This example demonstrates deterministic replay validation.

The runtime verifies:

- append-only lineage continuity
- deterministic replay equivalence
- replay digest consistency
- immutable execution reconstruction

---

## Execute

```bash
python -m runtime.replay
```

---

## Expected Runtime Behavior

```text
REPLAY VALID
LEDGER DIGEST VERIFIED
APPEND-ONLY LINEAGE VERIFIED
```

---

## What This Proves

The runtime can reconstruct governed execution deterministically from persisted lineage.
