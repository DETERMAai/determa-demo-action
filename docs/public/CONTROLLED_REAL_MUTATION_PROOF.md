# Controlled Real Mutation Proof

This public proof demonstrates Runtime Legitimacy enforcement using real local sandbox state, not pre-scripted outcomes.

## Proof Type

- Category: deterministic sandboxed runtime legitimacy proof
- Scope: operational mutation admissibility demonstration
- Not included: production control plane infrastructure

## What It Demonstrates

The same mutation proposal and same approval structure can produce different outcomes:

- **Path A**: `EXECUTION_ALLOWED`
- **Path B**: `EXECUTION_DENIED`

The difference is runtime state continuity at execution time.

## Proof Structure

The proof runs under `demo/controlled_mutation_proof/` and evaluates two paths:

1. Create sandbox target file.
2. Create one patch proposal.
3. Capture approval snapshot model:
   - target file hash
   - runtime epoch
   - dependency snapshot
   - approval timestamp
4. Issue scoped authority grant.
5. Evaluate runtime witness at execution.
6. Apply or block execution based on admissibility.
7. Generate append-only evidence lineage.

## Path Outcomes

### Path A — Admissible Execution

- runtime hash continuity: preserved
- runtime epoch continuity: preserved
- grant freshness: valid
- scope validity: valid
- outcome: `EXECUTION_ALLOWED`
- reason: `authority continuity preserved`

### Path B — Denied Execution

- same patch proposal used
- same approval model used
- target file changed after approval
- runtime witness hash no longer matches approval hash
- outcome: `EXECUTION_DENIED`
- reason: `runtime state diverged after approval`

Patch application is blocked in the denied path, and the target file remains unchanged by the denied attempt.

## Why This Is Stronger Than a Simulator

The outcome is computed from actual sandbox file state and deterministic checks, not scenario labels.

This means reviewers can inspect evidence and verify:

- the allowed path really applies a mutation
- the denied path really blocks the same mutation after runtime drift
- results are generated from real runtime witness values

## DATP Positioning Support

This proof reinforces DATP framing in public scope:

- Runtime Authority is evaluated at mutation time
- historical approval alone is insufficient
- execution fails closed when authority continuity breaks
- lineage remains append-only and reconstructable

## Public-Safe Boundaries

This proof intentionally does **not** expose:

- internal protocol algebra
- cryptographic internals
- distributed consensus mechanisms
- production credentials
- external infrastructure mutation

## Run

```bash
node demo/controlled_mutation_proof/run_proof.mjs
```

## Evidence Output

- `demo/controlled_mutation_proof/output/proof_<timestamp>/`
- `demo/controlled_mutation_proof/output/latest/`
