DISCLOSURE_CLASSIFICATION: P0

# Authorization Decay Timeline

Authorization decay over time under drift.

```text
T+0   : APPROVAL CONTEXT ALIGNED
T+2h  : EARLY DRIFT, CONTINUITY CONDITIONAL
T+24h : COMPOUNDED DRIFT, LEGITIMACY UNCERTAIN
T+7d  : HISTORICAL APPROVAL, EXECUTION REQUIRES REVALIDATION
```

Model claim:
Authorization status can remain true while authorization continuity degrades.

Invalidation trigger classes:
- state drift accumulation
- dependency mutations
- delayed execution windows

