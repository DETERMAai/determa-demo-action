# path_g_staging_to_production_divergence

- execution_status: EXECUTION_DENIED
- reason: runtime continuity diverged across environment transition

## Continuous Revalidation Timeline
- GRAPH_NODE: admissibility=DENIED, continuity=INVALID, divergence=CRITICAL(100)

## Execution State Progression
PROPOSED -> APPROVED_IN_STAGING -> QUEUED_FOR_PROMOTION -> REVALIDATING_IN_PRODUCTION -> PROMOTION_DENIED

## Queue Timeline
QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED

## Runtime Horizon
state: N/A (N/A)

## Divergence Pressure
LOW -> MEDIUM -> HIGH -> CRITICAL

## Lineage Events
- evt_0001_d7791286 proposal_created (T0)
- evt_0002_7a7a7a49 approval_snapshot_captured (T1)
- evt_0003_e8ded68b environment_snapshot_captured (T1B)
- evt_0004_13405ff5 authority_grant_issued (T2)
- evt_0005_334d7de7 promotion_queued (T3)
- evt_0006_dd9de2c9 promotion_revalidation_started (T6)
- evt_0007_ee724dea environment_divergence_detected (T7)
- evt_0008_df2fe585 promotion_denied (T8)
- evt_0009_c6aa0e73 cross_environment_lineage_finalized (T9)