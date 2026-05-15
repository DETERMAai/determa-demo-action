# Disclosure Decision Matrix

## Decision Question
Does this material help a reader:

`A)` understand legitimacy theory and category framing  
or  
`B)` reconstruct operational implementation behavior?

If answer includes `B`, material must not remain public.

## Matrix

| Material Type | A: Conceptual Understanding | B: Implementation Reconstruction | Public Decision |
|---|---|---|---|
| Conceptual legitimacy essays | Yes | No | Keep Public |
| Category comparisons (IAM vs runtime legitimacy) | Yes | No | Keep Public |
| Public contradiction demo narrative | Yes | No | Keep Public |
| Runtime specs/runbooks | Partial | Yes | Relocate Private |
| Replay schema internals | Partial | Yes | Relocate Private |
| Verification invariant mechanics | Partial | Yes | Relocate Private |
| Execution scripts/CLI runtime tooling | Low | Yes | Relocate Private |
| Runtime substrate source code | No | Yes | Relocate Private |

## Classification Examples
- `docs/notebooklm_public/foundational/*.md` -> Public (`P0/P1`)
- `docs/canonical/REPLAY_SCHEMA.md` -> Private (`R2/R3`)
- `docs/factory/FACTORY_RUNTIME_RUNBOOK.md` -> Private (`R2`)
- `runtime/*.py`, `factory/runtime/*.py` -> Private (`R3`)
- `tests/factory/*.py` -> Private (`R2`)

## Decision Rule
When uncertain, classify toward private and require explicit disclosure review to re-introduce public-safe abstractions.
