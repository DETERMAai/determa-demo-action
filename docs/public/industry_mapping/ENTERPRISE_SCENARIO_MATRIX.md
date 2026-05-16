# Enterprise Scenario Matrix

| Operational Surface | Contradiction Trigger | Runtime Legitimacy Risk | DATP Outcome |
|---|---|---|---|
| CI/CD deployment | runtime patch after approval | Authority Continuity break | fail-closed deployment mutation |
| Data pipelines | replay under schema/dependency drift | Mutation Admissibility uncertainty | deny replayed mutation until continuity restored |
| Infrastructure automation | sandbox or substrate reallocation | runtime context mismatch | fail-closed infrastructure mutation |
| Agentic execution | capability scope escalation | bounded authority violation | deny execution and record lineage |

## Positioning Implication

This matrix shows DETERMA as Runtime Authority infrastructure across enterprise operations, not a single workflow tool.
