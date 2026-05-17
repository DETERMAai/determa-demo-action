# Governed Repository Mutation Proof

This demo executes a deterministic runtime legitimacy proof against a real local sandbox git repository with continuous runtime revalidation.

## Scope Classification

- deterministic sandboxed runtime legitimacy proof
- operationally believable governed mutation runtime
- not a production infrastructure control plane

It demonstrates:

- same patch proposal
- same authority model
- different runtime repository state
- different execution outcome

## Run

```bash
node demo/git_runtime_governance/run_git_proof.mjs
```

## Continuous Revalidation Checkpoints

- PRE_EXECUTION
- MID_EXECUTION
- PRE_COMMIT
- FINALIZATION

Legitimacy is recalculated at every checkpoint.

## What Happens

### Path A — Allowed

- repository remains unchanged after approval snapshot
- admissibility evaluates to `ADMISSIBLE`
- patch is applied and committed
- execution status: `EXECUTION_ALLOWED`

### Path B — Denied

- repository is mutated after approval
- runtime witness diverges from approval snapshot
- admissibility evaluates to `DENIED`
- patch is not applied
- execution status: `EXECUTION_DENIED`

### Path C — Mid-Execution Halt

- execution begins and mutation is staged
- runtime state diverges during execution
- mid-execution revalidation fails
- execution halts before commit finalization
- staged mutation is rolled back

### Path D — Concurrent Mutation Conflict

- execution begins under valid continuity
- overlapping concurrent mutation commits first
- revalidation detects conflict
- execution finalization is prevented

## Replay Invalidation

The proof includes a replay attempt using a consumed single-use grant.

Replay is denied with authority continuity invalidation.

## Async Runtime Pressure Scenarios

### Path E — Delayed Execution Legitimacy Decay

- mutation enters queue and waits
- runtime horizon extends while state drifts
- revalidation runs before finalization
- authority continuity collapses
- execution is denied

### Path F — Retry Under Diverged Runtime

- first attempt is deferred
- retry is scheduled under queue pressure
- runtime evolves during retry wait
- retry revalidation fails continuity checks
- retry is denied

### Path G — Staging To Production Divergence

- approval is captured in staging
- promotion is queued for production
- production runtime diverges before promotion
- cross-environment revalidation fails
- promotion is denied

### Path H — Delegated Environment Transfer

- authority is issued under environment A
- execution is delegated to environment B
- delegated runtime witness diverges
- delegated continuity fails revalidation
- execution is denied

### Path I — Cascading Legitimacy Collapse

- mutation graph is initialized as `A -> B -> C`
- A diverges under runtime pressure
- graph revalidation starts
- B and C are transitively invalidated from upstream collapse
- dependent chain finalization is halted

## State Model

Authority Continuity:

`VALID -> WEAKENING -> STALE -> INVALID`

Mutation Admissibility:

`ADMISSIBLE -> REQUIRES_REVALIDATION -> DENIED`

Execution State:

`PROPOSED -> APPROVED -> QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED -> DENIED / FINALIZED`

Runtime Divergence:

`LOW -> MEDIUM -> HIGH -> CRITICAL`

Runtime Horizon:

`SHORT -> EXTENDED -> LONG -> EXCEEDED`

Cross-Environment Legitimacy:

`CONTINUOUS -> WEAKENING -> STALE -> INVALID`

Transitive Graph Legitimacy:

`VALID -> WEAKENING -> INVALID -> TRANSITIVELY_INVALIDATED`

## Outputs

Generated under:

- `demo/git_runtime_governance/output/git_proof_<timestamp>/`
- `demo/git_runtime_governance/output/latest/`

Key artifacts:

- `proof_summary.json`
- `proof_summary.md`
- `proof_summary.txt`
- `path_a_continuous_allowed/evidence.json|md|txt`
- `path_b_denied_pre_execution/evidence.json|md|txt`
- `path_c_mid_execution_halt/evidence.json|md|txt`
- `path_d_concurrent_conflict/evidence.json|md|txt`
- `path_e_delayed_execution_decay/evidence.json|md|txt`
- `path_f_retry_under_diverged_runtime/evidence.json|md|txt`
- `path_g_staging_to_production_divergence/evidence.json|md|txt`
- `path_h_delegated_environment_transfer/evidence.json|md|txt`
- `path_i_cascading_legitimacy_collapse/evidence.json|md|txt`
- `path_*/target_before_attempt.txt`
- `path_*/target_after_attempt.txt`
