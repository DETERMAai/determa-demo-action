# DETERMA Canonical Release Signing

## Purpose

DETERMA release baselines are cryptographically signed to ensure:

- immutable governed release verification
- tamper detection
- reproducible runtime verification
- append-only release authenticity
- independent third-party validation

---

## Signing Model

DETERMA uses:

```text
Sigstore Cosign Keyless Signing
```

This avoids storing long-lived private signing keys inside the repository.

---

## Signed Artifacts

The following artifacts are signed:

- receipts/runtime_proof_snapshot.json
- receipts/runtime_proof_snapshot.sha256
- receipts/canonical_release_baseline.json
- receipts/canonical_release_baseline.sha256
- receipts/release_lineage.jsonl

---

## Verification

Canonical verification example:

```bash
cosign verify-blob \
  --certificate receipts/canonical_release_baseline.json.pem \
  --signature receipts/canonical_release_baseline.json.sig \
  receipts/canonical_release_baseline.json
```

---

## Security Model

Signing guarantees:

- release authenticity
- immutable baseline integrity
- lineage tamper detection
- reproducible governed restoration verification

Signing does NOT replace:

- append-only enforcement
- replay validation
- authority enforcement
- corruption detection

---

## Threat Model

Signing is specifically intended to detect:

- release artifact rewriting
- GitHub compromise rewriting releases
- baseline substitution attacks
- forged governed runtime snapshots

---

## Design Principle

DETERMA assumes:

```text
trust must be reproducible and externally verifiable
```
