# DETERMA Security Policy

## Public Repository Model

This repository is intentionally public.

DETERMA is designed around:
- deterministic replay,
- append-only lineage,
- governed execution,
- fail-closed runtime semantics,
- verifiable restoration,
- immutable proof receipts.

Security must not depend on hidden source code.

---

## Never Commit

The following material must NEVER be committed:

- production credentials
- GitHub PATs
- cloud credentials
- signing keys
- deployment secrets
- private certificates
- runtime authority keys
- infrastructure topology secrets
- local `.env` files
- live runtime databases
- non-sanitized customer data

Any exposed credential must be considered compromised immediately.

---

## Public-Safe Artifacts

The following artifact classes are intentionally public:

- deterministic replay proofs
- append-only lineage receipts
- canonical restoration baselines
- runtime governance tests
- corruption validation tests
- replay integrity proofs
- release baseline digests

These artifacts are designed for independent verification.

---

## Security Design Principle

DETERMA security is based on:

- authority validation
- deterministic replay
- append-only enforcement
- runtime verification
- corruption detection
- fail-closed execution

NOT on obscurity.

---

## Responsible Disclosure

If you discover:
- credential leakage
- replay inconsistencies
- append-only bypasses
- recovery vulnerabilities
- deterministic divergence
- corruption bypasses
- execution authority flaws

please report privately before public disclosure.

Contact:
- determa.ai@gmail.com
