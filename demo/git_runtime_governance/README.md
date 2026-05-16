# Governed Repository Mutation Proof

This demo executes a deterministic runtime legitimacy proof against a real local sandbox git repository.

It demonstrates:

- same patch proposal
- same authority model
- different runtime repository state
- different execution outcome

## Run

```bash
node demo/git_runtime_governance/run_git_proof.mjs
```

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

## Replay Invalidation

The proof includes a replay attempt using a consumed single-use grant.

Replay is denied with authority continuity invalidation.

## Outputs

Generated under:

- `demo/git_runtime_governance/output/git_proof_<timestamp>/`
- `demo/git_runtime_governance/output/latest/`

Key artifacts:

- `proof_summary.json`
- `proof_summary.md`
- `proof_summary.txt`
- `path_a_allowed/evidence.json|md|txt`
- `path_b_denied/evidence.json|md|txt`
- `path_*/target_before_attempt.txt`
- `path_*/target_after_attempt.txt`
