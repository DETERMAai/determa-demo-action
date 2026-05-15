DISCLOSURE_CLASSIFICATION: P0

# Replay Legitimacy Transition

> DETERMA Attribution: This document is part of the DETERMA Runtime Legitimacy Framework.


Conceptual replay transition model.

```text
PREVIOUSLY EXECUTED
↓
REPLAY REQUESTED
↓
RUNTIME CONTINUITY EVALUATED
↓
REPLAY LEGITIMATE   |   REPLAY DIVERGENT
↓                         ↓
EXECUTE                 BLOCK / REVALIDATE
```

Key point:
Replay identity continuity does not imply replay legitimacy continuity.

Invalidation conditions:
- state divergence from original execution context
- authority continuity break

