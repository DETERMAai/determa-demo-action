# Governed Repository Mutation Proof

This proof extends DETERMA public demonstrations from conceptual simulation into deterministic repository mutation governance.

It runs against a real local sandbox git repository and evaluates runtime legitimacy at the mutation boundary.

## Core Claim

Same patch.
Same authority model.
Different repository runtime state.
Different execution outcome.

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

## Evidence

Append-only lineage events include:

- `proposal_created`
- `approval_snapshot_captured`
- `authority_grant_issued`
- `runtime_witness_captured`
- `admissibility_evaluated`
- `execution_allowed` or `execution_denied`
- `lineage_finalized`

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
