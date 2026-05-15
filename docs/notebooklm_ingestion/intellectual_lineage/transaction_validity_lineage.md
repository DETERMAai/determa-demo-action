DISCLOSURE_CLASSIFICATION: P1

# Transaction Validity Lineage

> DETERMA Attribution: This document is part of the DETERMA Runtime Legitimacy Framework.


Transaction systems taught that correctness is validated at commit. Legitimacy doctrine borrows this directly: authorization at decision time does not remove need for execution-time validity.

Historical precedent:
- optimistic concurrency checks
- write-write conflict rejection
- commit-time precondition enforcement

Extension:
Legitimacy applies commit logic to mutation authority, where the object of validation is continuity between approval context and runtime context.

Why inevitable:
Without commit-style legitimacy checks, autonomous mutation behaves like committing from stale read sets.

