# Controlled Real Mutation Proof

This proof demonstrates a deterministic local runtime legitimacy decision against actual sandbox file state.

It runs two paths with the same patch proposal and same approval model:

- `PATH A`: runtime continuity preserved -> `EXECUTION_ALLOWED`
- `PATH B`: runtime state diverged after approval -> `EXECUTION_DENIED`

## Run

```bash
node demo/controlled_mutation_proof/run_proof.mjs
```

## Output

Each run writes evidence to:

- `demo/controlled_mutation_proof/output/proof_<timestamp>/`
- `demo/controlled_mutation_proof/output/latest/`

Key files:

- `proof_summary.json`
- `CONTROLLED_REAL_MUTATION_PROOF_REPORT.md`
- `path_a_admissible/evidence.json`
- `path_b_denied/evidence.json`

The evidence chain is append-only and includes:

- `proposal_created`
- `approval_snapshot_captured`
- `authority_grant_issued`
- `runtime_witness_captured`
- `admissibility_evaluated`
- `execution_allowed` or `execution_denied`
- `proof_finalized`
