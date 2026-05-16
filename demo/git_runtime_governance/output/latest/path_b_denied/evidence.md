# path_b_denied

- execution_status: EXECUTION_DENIED
- reason: repository runtime state diverged after approval
- admissibility: DENIED
- authority_continuity: STALE
- divergence_level: HIGH
- divergence_score: 64

## Checks
- head_continuity: false
- target_hash_continuity: true
- freshness: true
- replay_status: false
- scope_continuity: true
- dependency_continuity: false
- runtime_epoch_continuity: false
- queue_continuity: false

## Lineage Events
- evt_0001_a2042941 proposal_created (prev=null)
- evt_0002_7296a5d3 approval_snapshot_captured (prev=evt_0001_a2042941)
- evt_0003_fb03aabc authority_grant_issued (prev=evt_0002_7296a5d3)
- evt_0004_74c9a35e runtime_witness_captured (prev=evt_0003_fb03aabc)
- evt_0005_023997d8 admissibility_evaluated (prev=evt_0004_74c9a35e)
- evt_0006_8cb741c1 execution_denied (prev=evt_0005_023997d8)
- evt_0007_128f6375 lineage_finalized (prev=evt_0006_8cb741c1)