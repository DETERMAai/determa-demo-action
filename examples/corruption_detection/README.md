# Corruption Detection Example

## Purpose

This example demonstrates deterministic corruption detection.

The runtime validates:

- physical ledger corruption detection
- replay refusal on integrity violation
- append-only chain integrity
- fail-closed corruption handling

---

## Execute

```bash
python -m pytest runtime/tests/test_full_runtime_proof.py -k corrupted_ledger -v
```

---

## Expected Runtime Behavior

```text
CORRUPTION DETECTED
REPLAY REFUSED
FAIL-CLOSED ENFORCEMENT VERIFIED
```

---

## What This Proves

The runtime refuses replay reconstruction from corrupted lineage state.
