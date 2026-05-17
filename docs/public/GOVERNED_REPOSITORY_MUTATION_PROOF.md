# Governed Repository Mutation Proof

This proof extends DETERMA public demonstrations from conceptual simulation into deterministic repository mutation governance with continuous runtime revalidation.

It runs against a real local sandbox git repository and evaluates runtime legitimacy at execution checkpoints, not only before execution starts.
Deferred execution requires continuous legitimacy continuity, not historical approval persistence.

## Core Claim

Same patch.
Same authority model.
Different repository runtime state.
Different execution outcome.

## Continuous Runtime Revalidation

Runtime legitimacy is continuously revalidated throughout mutation execution:

- PRE_EXECUTION
- MID_EXECUTION
- PRE_COMMIT
- FINALIZATION

Execution authority may collapse during execution if runtime continuity diverges.
Execution authority may also decay during asynchronous queue delay before execution finalization.
Runtime legitimacy must also survive environment transition before promotion finalization.
Runtime legitimacy also propagates through dependent mutation chains.

## Execution Paths

### Path A — Patch Allowed

1. Sandbox repository is initialized.
2. Patch proposal is created.
3. Approval snapshot is captured:
   - approval `HEAD`
   - target file hash
   - dependency hash
   - runtime epoch
4. Scoped single-use authority grant is issued.
5. Runtime witness is captured without repository drift.
6. Admissibility evaluates to `ADMISSIBLE`.
7. Patch is applied and committed.

Outcome:

`EXECUTION_ALLOWED`

Reason:

`authority continuity preserved`

### Path B — Patch Denied

1. Same patch proposal is reused.
2. Same approval model is reused.
3. Repository is mutated after approval (dependency and queue state drift).
4. Runtime witness is recaptured.
5. Admissibility evaluates to `DENIED`.
6. Patch application is blocked.

Outcome:

`EXECUTION_DENIED`

Reason:

`repository runtime state diverged after approval`

### Path C — Mid-Execution Runtime Divergence

1. Execution starts under legitimate continuity.
2. Mutation is staged.
3. Runtime state diverges during execution.
4. Mid-execution revalidation fails.
5. Execution halts before commit finalization.
6. Staged mutation is rolled back.

Outcome:

`EXECUTION_DENIED`

Reason:

`execution halted before final commit due to runtime divergence`

### Path D — Concurrent Mutation Conflict

1. Execution starts under valid continuity.
2. A concurrent overlapping mutation commits first.
3. Revalidation detects conflict and continuity collapse.
4. Finalization is prevented.

Outcome:

`EXECUTION_DENIED`

Reason:

`concurrent mutation conflict`

### Path E — Delayed Execution Legitimacy Decay

1. Mutation is approved and queued.
2. Execution is delayed under queue pressure.
3. Runtime state drifts while waiting.
4. Revalidation runs on resume.
5. Authority continuity decays past admissible bounds.
6. Finalization is prevented.

Outcome:

`EXECUTION_DENIED`

Reason:

`runtime continuity decayed during async execution delay`

### Path F — Retry Under Diverged Runtime

1. Initial attempt enters queue and is deferred.
2. Retry is scheduled.
3. Runtime evolves during retry wait.
4. Retry revalidation detects stale continuity.
5. Retry execution is denied.

Outcome:

`EXECUTION_DENIED`

Reason:

`retry denied after runtime continuity drift`

### Path G — Staging To Production Divergence

1. Approval is captured in staging.
2. Promotion is queued.
3. Production runtime diverges before promotion.
4. Cross-environment revalidation starts.
5. Environment continuity mismatch is detected.
6. Promotion is denied.

Outcome:

`EXECUTION_DENIED`

Reason:

`runtime continuity diverged across environment transition`

### Path H — Delegated Environment Transfer

1. Authority is issued under source environment A.
2. Execution is delegated to environment B.
3. Delegated runtime witness evolves under different assumptions.
4. Cross-context admissibility fails continuity checks.
5. Delegated execution is denied.

Outcome:

`EXECUTION_DENIED`

Reason:

`delegated runtime continuity mismatch`

### Path I — Cascading Legitimacy Collapse

1. Mutation graph is initialized: `A -> B -> C`.
2. B is conditionally approved on A continuity.
3. C is conditionally approved on B continuity.
4. Runtime divergence invalidates A.
5. Dependency graph revalidation propagates collapse.
6. B and C become `TRANSITIVELY_INVALIDATED`.
7. Chain execution halts before dependent finalization.

Outcome:

`EXECUTION_DENIED`

Reason:

`downstream legitimacy collapsed transitively from upstream mutation A`

## Admissibility Checks

Deterministic evaluator checks:

- HEAD continuity
- target hash continuity
- grant freshness
- replay status
- scope continuity
- dependency continuity
- runtime epoch continuity
- queue continuity
- queue witness continuity
- retry continuity
- authority aging across runtime horizon
- configuration continuity across environments
- branch continuity across environments
- delegated authority continuity
- upstream continuity inheritance
- dependency continuity inheritance

Outcomes:

- `ADMISSIBLE`
- `REQUIRES_REVALIDATION`
- `DENIED`

## Replay Invalidation

The proof includes a replay attempt with a consumed single-use grant.

Replay result:

- authority continuity: `INVALID`
- execution: `DENIED`

## Divergence Visualization

Runtime divergence is computed and classified:

`LOW -> MEDIUM -> HIGH -> CRITICAL`

Authority continuity transitions:

`VALID -> WEAKENING -> STALE -> INVALID`

Mutation admissibility transitions:

`ADMISSIBLE -> REQUIRES_REVALIDATION -> DENIED`

Execution state transitions:

`PROPOSED -> APPROVED -> QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED -> DENIED / FINALIZED`

Runtime horizon transitions:

`SHORT -> EXTENDED -> LONG -> EXCEEDED`

Cross-environment legitimacy transitions:

`CONTINUOUS -> WEAKENING -> STALE -> INVALID`

Transitive dependency legitimacy transitions:

`VALID -> WEAKENING -> INVALID -> TRANSITIVELY_INVALIDATED`

## Evidence

Append-only lineage events include:

- `proposal_created`
- `approval_snapshot_captured`
- `authority_grant_issued`
- `runtime_witness_captured`
- `legitimacy_revalidated`
- `execution_started`
- `mutation_staged`
- `runtime_divergence_detected`
- `execution_halted`
- `rollback_completed` or `finalization_prevented`
- `execution_allowed` or `execution_denied`
- `lineage_finalized`
- `execution_queued`
- `queue_state_updated`
- `execution_delayed`
- `retry_scheduled`
- `authority_decay_detected`
- `runtime_horizon_exceeded`
- `retry_revalidation_started`
- `retry_denied`
- `environment_snapshot_captured`
- `promotion_queued`
- `promotion_revalidation_started`
- `environment_divergence_detected`
- `delegated_execution_started`
- `delegated_continuity_failed`
- `promotion_denied`
- `cross_environment_lineage_finalized`
- `dependency_graph_initialized`
- `dependency_chain_approved`
- `upstream_divergence_detected`
- `graph_revalidation_started`
- `transitive_invalidation_triggered`
- `downstream_authority_invalidated`
- `chain_execution_halted`
- `cascading_lineage_finalized`

Evidence is exported as:

- JSON
- Markdown
- TXT

## Why This Is Stronger Than Simulator-Only Proofs

This proof performs real git operations:

- repository initialization
- commit generation
- patch diff generation
- patch apply + commit on admissible path
- patch block on denied path

Outcomes are computed from repository state continuity, not scenario labels.

## Public-Safe Boundary

This proof intentionally excludes:

- internal protocol semantics
- cryptographic internals
- distributed consensus logic
- external system mutation
- privileged deployment access

It is a deterministic public runtime legitimacy proof, not a production control plane.

## Run

```bash
node demo/git_runtime_governance/run_git_proof.mjs
```
