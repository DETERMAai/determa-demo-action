# Enterprise Scenario Matrix

| Operational Surface | Contradiction Trigger | Runtime Legitimacy Risk | DATP Outcome |
|---|---|---|---|
| CI/CD deployment | runtime patch after approval | Authority Continuity break | fail-closed deployment mutation |
| Data pipelines | replay under schema/dependency drift | Mutation Admissibility uncertainty | deny replayed mutation until continuity restored |
| Infrastructure automation | sandbox or substrate reallocation | runtime context mismatch | fail-closed infrastructure mutation |
| Agentic execution | capability scope escalation | bounded authority violation | deny execution and record lineage |
| Multi-stage deployment | staging-to-production drift | cross-environment continuity collapse | promotion denied before finalization |
| Async execution queues | delayed retry under runtime drift | freshness and witness decay | retry denied after revalidation |
| Dependency mutation chains | upstream invalidation (`A -> B -> C`) | transitive downstream authority collapse | chain halted with transitive invalidation lineage |

## Positioning Implication

This matrix shows DETERMA as Runtime Authority infrastructure across enterprise operations, not a single workflow tool.
