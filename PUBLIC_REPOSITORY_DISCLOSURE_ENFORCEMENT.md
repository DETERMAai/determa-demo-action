# Public Repository Disclosure Enforcement

## Purpose
This policy defines hard disclosure boundaries for the public DETERMA repository.

The public repository exists for:
- legitimacy field doctrine
- conceptual runtime legitimacy reasoning
- category framing
- public-safe demo cognition
- NotebookLM public ingestion materials

The public repository does not exist for:
- runtime enforcement implementation
- orchestration systems
- execution sequencing internals
- replay implementation semantics
- operational execution topology

## Public Eligibility Rules
Material is eligible for public inclusion only if all are true:
1. It explains conceptual legitimacy theory or category framing.
2. It does not reveal implementation mechanics.
3. It cannot be used to reconstruct runtime enforcement behavior.
4. It does not expose operational sequencing, runtime topology, or substrate internals.
5. It remains implementation-agnostic and public-safe under NotebookLM ingestion.

## Operational Leakage Criteria
Material is operational leakage if it contains any of:
- code paths for execution, replay, authority, or mutation runtime behavior
- runtime CLI/tooling that exercises enforcement decisions
- private execution workflows, runbooks, or scheduling mechanics
- enforcement control-plane semantics, proofs, receipts, or audit chain internals
- implementation-specific verification or invalidation logic

## Abstraction Boundary Enforcement
Canonical public boundary:
- conceptual: allowed
- implementation: disallowed

Boundary test:
- If a reader can infer how enforcement is implemented, material fails public boundary.
- If a reader can only infer why runtime legitimacy matters, material passes public boundary.

## Disclosure Escalation Rules
When material appears to cross conceptual-to-operational boundary:
1. Mark as `REVIEW_REQUIRED`.
2. Classify as `R1`, `R2`, or `R3` (see `PRIVATE_RELOCATION_POLICY.md`).
3. Remove from public ingestion surfaces.
4. Relocate to private repository scope.
5. Update manifests/indexes to preserve conceptual continuity without implementation leakage.

## Restricted Material Handling
- Restricted material must not be ingested by public NotebookLM surfaces.
- Restricted material must not remain in public-facing demo or root conceptual paths.
- Restricted material may be retained only in private storage/repository with access control.

## Private Relocation Requirement
Any document, code, or artifact failing eligibility must be relocated out of the public repository into private scope according to `PRIVATE_RELOCATION_POLICY.md`.
