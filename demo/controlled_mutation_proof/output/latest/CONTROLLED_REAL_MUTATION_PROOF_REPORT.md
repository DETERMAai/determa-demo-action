# Controlled Real Mutation Proof Report

Run ID: proof_20260516_222445

## Proof Claim

Same patch. Same approval structure. Different runtime state. Different execution outcome.

## Path A (Admissible)

- status: EXECUTION_ALLOWED
- reason: authority continuity preserved
- target hash changed by patch: true

## Path B (Denied)

- status: EXECUTION_DENIED
- reason: runtime state diverged after approval
- patch applied: false
- target unchanged by denied attempt: true

## Runtime Difference

- Path A runtime hash == approval hash: true
- Path B runtime hash == approval hash: false

## Evidence Files

- path_a/evidence.json
- path_b/evidence.json
- proof_summary.json
