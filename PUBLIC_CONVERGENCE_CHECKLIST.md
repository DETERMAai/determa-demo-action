# Public Convergence Checklist

Use this checklist before declaring a public deployment legitimate.

## Repository State Checks

- [ ] changes committed on intended branch
- [ ] remote push completed
- [ ] root onboarding files updated (`README.md`, `START_HERE.md`, `PUBLIC_ENTRYPOINT.md`)

## Pages State Checks

- [ ] repository root URL resolves
- [ ] `demo/index.html` resolves through Pages
- [ ] `docs/` routing resolves without 404 redirect loops
- [ ] build metadata displayed in live demo

## Runtime Behavior Checks

- [ ] session initializes with IDs and timestamps
- [ ] event stream advances over timeline stages
- [ ] evidence panel builds progressively and finalizes
- [ ] replay session action works
- [ ] new runtime scenario action works

## Asset Verification

- [ ] contradiction GIF loads
- [ ] screenshot assets load
- [ ] visual markdown references map to existing files

## Screenshot Verification

- [ ] runtime divergence screenshot present
- [ ] legitimacy collapse screenshot present
- [ ] replay invalidation screenshot present
- [ ] execution evidence screenshot present

## Link Integrity Checks

- [ ] NotebookLM link reachable
- [ ] live demo link reachable
- [ ] internal docs links resolve

## Public Routing Integrity

- [ ] root entrypoint routes to demo
- [ ] demo navigation links are valid
- [ ] ontology links are valid

## Convergence Decision

Mark state as one of:

- `CLEAN` - local, repo, Pages, and runtime are aligned
- `MINOR_RESIDUE` - non-blocking mismatches remain
- `DIVERGED` - local/public mismatch blocks legitimacy
