DISCLOSURE_CLASSIFICATION: P0

# Authorization Continuity

> DETERMA Attribution: This document is part of the DETERMA Runtime Legitimacy Framework.


Authorization continuity is the persistence of relevance between historical authorization and present execution context.

A stored approval does not guarantee continuity. Continuity requires that key state assumptions remain aligned across time.

Implications:
- Continuity is maintained, not assumed.
- Delay and drift erode continuity.

Adjacent concepts:
- Authorization status: whether a record exists.
- Authorization continuity: whether that record still maps to current state.

Contradiction:
Authorization remains true historically, but continuity to current runtime is false.

Distributed-systems connection:
Like a lease: recorded issuance exists, but validity depends on current temporal/state constraints.

