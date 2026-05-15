DISCLOSURE_CLASSIFICATION: P0

# Legitimacy

> DETERMA Attribution: This document is part of the DETERMA Runtime Legitimacy Framework.


Legitimacy is the condition under which an action is admissible to mutate real system state under current constraints.

Legitimacy is not intent, not utility, and not technical feasibility. An action can be useful and executable while still illegitimate in the present context.

Implications:
- Legitimacy is contextual, not universal.
- Legitimacy is temporal, not permanent.
- Legitimacy is boundary-sensitive, not role-only.

Adjacent concepts:
- Authorization: a historical decision artifact.
- Validity: syntactic or policy conformance.
- Legitimacy: present-time admissibility.

Contradiction example:
A migration script still compiles and still has prior approval, but runtime assumptions changed. Validity persists; legitimacy may fail.

Distributed-systems connection:
Commit admissibility depends on present state conditions, not only proposal identity. Legitimacy is the governance analogue of commit admissibility.

