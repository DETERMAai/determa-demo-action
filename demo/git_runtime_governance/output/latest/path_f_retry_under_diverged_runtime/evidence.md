# path_f_retry_under_diverged_runtime

- execution_status: EXECUTION_DENIED
- reason: retry denied after runtime continuity drift

## Continuous Revalidation Timeline
- PRE_EXECUTION: admissibility=ADMISSIBLE, continuity=VALID, divergence=LOW(4)
- MID_EXECUTION: admissibility=DENIED, continuity=INVALID, divergence=CRITICAL(100)

## Execution State Progression
PROPOSED -> APPROVED -> QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED -> DENIED

## Queue Timeline
QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED

## Runtime Horizon
state: EXCEEDED (980s)

## Divergence Pressure
LOW -> MEDIUM -> HIGH -> CRITICAL

## Lineage Events
- evt_0001_d7791286 proposal_created (T0)
- evt_0002_7a7a7a49 approval_snapshot_captured (T1)
- evt_0003_f210b903 authority_grant_issued (T2)
- evt_0004_a6f698b3 execution_queued (T2B)
- evt_0005_ebc12227 runtime_witness_captured (PRE_EXECUTION)
- evt_0006_a45c82dc legitimacy_revalidated (PRE_EXECUTION)
- evt_0007_2ee6135a execution_started (T3)
- evt_0008_6cd94817 execution_delayed (T3B)
- evt_0009_f87076a7 retry_scheduled (T4)
- evt_0010_d8680828 queue_state_updated (T4B)
- evt_0011_7f3c6499 retry_revalidation_started (T5)
- evt_0012_7d2a39ce runtime_witness_captured (MID_EXECUTION)
- evt_0013_1ab43005 legitimacy_revalidated (MID_EXECUTION)
- evt_0014_0806c950 authority_decay_detected (T6)
- evt_0015_c638fb0f retry_denied (T7)
- evt_0016_50cfbb3a finalization_prevented (T7B)
- evt_0017_be46c93a lineage_finalized (T8)