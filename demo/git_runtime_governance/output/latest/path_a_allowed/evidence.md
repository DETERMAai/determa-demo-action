# path_a_allowed

- execution_status: EXECUTION_ALLOWED
- reason: authority continuity preserved
- admissibility: ADMISSIBLE
- authority_continuity: VALID
- divergence_level: LOW
- divergence_score: 0

## Checks
- head_continuity: true
- target_hash_continuity: true
- freshness: true
- replay_status: false
- scope_continuity: true
- dependency_continuity: true
- runtime_epoch_continuity: true
- queue_continuity: true

## Lineage Events
- evt_0001_a2042941 proposal_created (prev=null)
- evt_0002_7296a5d3 approval_snapshot_captured (prev=evt_0001_a2042941)
- evt_0003_fb03aabc authority_grant_issued (prev=evt_0002_7296a5d3)
- evt_0004_74c9a35e runtime_witness_captured (prev=evt_0003_fb03aabc)
- evt_0005_023997d8 admissibility_evaluated (prev=evt_0004_74c9a35e)
- evt_0006_88d884ce execution_allowed (prev=evt_0005_023997d8)
- evt_0007_3bf5bf26 runtime_witness_captured (prev=evt_0006_88d884ce)
- evt_0008_127984f1 admissibility_evaluated (prev=evt_0007_3bf5bf26)
- evt_0009_3a00ab11 execution_denied (prev=evt_0008_127984f1)
- evt_0010_62a9fe2b lineage_finalized (prev=evt_0009_3a00ab11)