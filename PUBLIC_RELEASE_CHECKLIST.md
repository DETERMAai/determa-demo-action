# Public Release Checklist

Use this checklist before any public sync or release.

## Disclosure Compliance
- [ ] Public repository contains conceptual/public-safe material only.
- [ ] No operational substrate directories remain in public scope.
- [ ] NotebookLM ingestion is constrained to `docs/notebooklm_public/` only.
- [ ] All public docs pass `DISCLOSURE_DECISION_MATRIX.md`.

## Operational Leakage
- [ ] No runtime enforcement mechanics exposed in docs.
- [ ] No replay implementation semantics exposed.
- [ ] No orchestration logic/runbook content exposed.
- [ ] No private execution sequencing or topology exposed.
- [ ] No runtime databases, logs, or local artifacts present.

## Ontology and Conceptual Hygiene
- [ ] Public terminology aligns with ontology stabilization rules.
- [ ] Conceptual duplication minimized; no conflicting terminology.
- [ ] Public conceptual hierarchy remains coherent and stable.

## Boundary Integrity
- [ ] Public demo remains public-safe and decoupled from private runtime internals.
- [ ] README follows `README_PUBLIC_POSITIONING_POLICY.md`.
- [ ] Restricted content is relocated according to `PRIVATE_RELOCATION_POLICY.md`.

## Final Verification
- [ ] `PUBLIC_OPERATIONAL_LEAKAGE_AUDIT.md` reviewed and updated.
- [ ] `PUBLIC_REPOSITORY_TOPOLOGY.md` matches actual tree.
- [ ] Release reviewer signs off on abstraction boundary integrity.
