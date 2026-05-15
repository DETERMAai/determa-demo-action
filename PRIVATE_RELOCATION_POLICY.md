# Private Relocation Policy

## Purpose
Define what must be relocated from public scope to private repositories when operational sensitivity is detected.

## Relocation Triggers
Relocation is required when material includes:
- implementation-bearing runtime behavior
- enforcement decision logic
- replay invalidation internals
- execution or orchestration topology
- mutation sequencing mechanics
- substrate state transition internals

## Canonical Relocation Classes
- `R1 — Restricted Conceptual`
  - advanced conceptual content that could materially reveal enforcement approach
  - remove from public ingestion surfaces; may remain private doctrine
- `R2 — Private Operational`
  - runbooks, scripts, runtime operations, execution flow mechanics
  - move to private repository immediately
- `R3 — Sensitive Runtime Substrate`
  - direct enforcement substrate code/semantics/topology
  - private-only, strict access control, never public mirrored

## Relocation Rules
1. Classify candidate artifact (`R1`, `R2`, or `R3`).
2. Remove from public-facing paths.
3. Relocate to private repository preserving lineage/traceability metadata.
4. Replace public references with conceptual-safe placeholders when needed.
5. Re-audit NotebookLM ingestion boundaries after relocation.

## Operational Exposure Threshold
If a reasonable technical evaluator can infer implementation behavior from a document or code artifact, relocation is mandatory.

## Isolation Requirements
- `R2` and `R3` must not be present in public repository history for future public baselines.
- Public docs may reference category-level existence of private controls, but not mechanics.
