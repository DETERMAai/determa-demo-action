# Compromised Agent Case

An agent that previously operated within normal behavior begins producing unsafe mutation proposals.

Historical approvals from prior safe periods still exist in system records.

Why historical approval fails:
- historical authorization cannot be generalized across changed behavior and changed runtime context

How legitimacy changes:
- proposals and mutation authority must remain decoupled
- execution legitimacy is evaluated at mutation time, not inferred from prior trust
