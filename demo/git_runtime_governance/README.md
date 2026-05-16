# Governed Repository Mutation Proof

This demo executes a deterministic runtime legitimacy proof against a real local sandbox git repository with continuous runtime revalidation.

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

## State Model

Authority Continuity:

`VALID -> WEAKENING -> STALE -> INVALID`

Mutation Admissibility:

`ADMISSIBLE -> REQUIRES_REVALIDATION -> DENIED`

Execution State:

`PROPOSED -> STAGED -> EXECUTING -> HALTED -> ROLLED_BACK / FINALIZED`

Runtime Divergence:

`LOW -> MEDIUM -> HIGH -> CRITICAL`

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
- `path_*/target_before_attempt.txt`
- `path_*/target_after_attempt.txt`
