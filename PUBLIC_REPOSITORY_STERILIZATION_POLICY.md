# Public Repository Sterilization Policy

## Objective
Maintain a zero-operational-leakage public repository by removing implementation-sensitive material and preserving only conceptual/public-safe surfaces.

## Must Never Exist in Public
- runtime enforcement substrate logic
- orchestration mechanics and execution scheduler internals
- replay implementation schemas and invalidation mechanics
- private runtime topology, control loops, worker execution internals
- implementation-bearing proofs/receipts/audit-chain mechanics
- deployment architecture revealing private execution behavior

## Leakage Indicators
Any of the following indicates sterilization failure:
- file paths in `runtime/`, `factory/`, `src/`, `tests/`, `scripts/`, `reports/`
- docs describing runbooks, task contracts, runtime specs, replay internals
- language that explains "how enforcement works" rather than "why legitimacy matters"
- executable artifacts coupled to private runtime mutation flows

## Exposure Risk Classes
- Topology risk: reveals component interconnections and execution graph
- Sequencing risk: reveals stepwise mutation/replay enforcement ordering
- Semantics risk: reveals deterministic enforcement decision rules
- Substrate risk: reveals internal runtime state handling or authority internals

## Forbidden Public Exposure Examples
- replay artifact chain mechanics
- replay schema details
- verification invariants tied to implementation behavior
- factory runtime runbooks
- worker runner specs and task contract templates
- operational output dumps from live/private runtime

## Sterilization Workflow
1. Inventory all files/directories.
2. Classify each artifact by disclosure level.
3. Remove or relocate restricted artifacts to private scope.
4. Verify public tree matches `PUBLIC_REPOSITORY_TOPOLOGY.md`.
5. Re-run leakage audit before every release.

## Acceptance Condition
Public repository is considered sterilized only when:
- no private operational/substrate artifacts remain
- only conceptual public doctrine and public-safe demo surfaces remain
- NotebookLM public ingestion is constrained to curated public surfaces
