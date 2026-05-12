# DETERMA Releases

## v0.1-governed-runtime-proof

Canonical governed runtime baseline.

### Included Runtime Guarantees

- deterministic replay verification
- append-only lineage enforcement
- crash recovery validation
- replay mutation prevention
- authority enforcement
- distributed coordination validation
- corruption detection
- restoration equivalence verification
- signed release baseline verification

---

## Runtime Proof Status

```text
45 / 45 PASSING
```

---

## Canonical Proof Artifacts

- receipts/runtime_proof_snapshot.json
- receipts/canonical_release_baseline.json
- receipts/release_lineage.jsonl

---

## Release Verification

```bash
python -m runtime.replay
python -m pytest runtime/tests -v
```

---

## Category

```text
Governed Execution Infrastructure
```
