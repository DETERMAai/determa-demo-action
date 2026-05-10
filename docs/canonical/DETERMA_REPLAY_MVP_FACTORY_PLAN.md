# DETERMA Replay MVP — Canonical Repository Implementation Plan

Status: Canonical execution plan for repository implementation  
Date: 2026-05-10  
Scope: Start autonomous Factory work for the first market-facing DETERMA MVP  
Target path: `docs/canonical/DETERMA_REPLAY_MVP_FACTORY_PLAN.md`

---

## 0. Executive Decision

DETERMA will not begin by building the full authority plane.

The first repository implementation target is:

```text
DETERMA Replay for AI-generated Pull Requests
```

The goal is to ship a small, understandable, demonstrable GitHub-native product that creates a deterministic replay artifact for AI-generated code mutations.

The first product must answer:

1. What changed?
2. Why does it matter?
3. Which mutation surface was touched?
4. Can this mutation be trusted?
5. What should the human reviewer do before merge?

---

## 1. Canonical Product Definition

DETERMA is not, at this stage:

- a generic AI governance platform
- a universal agent orchestration system
- an enterprise dashboard
- an MCP gateway
- a full policy DSL
- a global action ledger
- a constitutional governance product

DETERMA v0.1 is:

```text
A GitHub-native replay layer for AI-generated code mutations.
```

Canonical sentence:

```text
Observe, replay, and explain AI-generated code mutations.
```

Operational sentence:

```text
DETERMA comments on pull requests with a deterministic Mutation Replay that explains what changed, why it matters, whether it should be trusted, and what action the reviewer should take.
```

---

## 2. Category Wedge

The market entry category is:

```text
AI Mutation Replay
```

Not:

- AI security
- AI observability
- AI governance
- AI agent authorization
- AI orchestration

The behavioral goal is:

```text
Before trusting an AI-generated mutation, check the DETERMA Replay.
```

The product should create the same review reflex as:

- check CI
- check logs
- check traces
- check security scan

---

## 3. First MVP Boundary

### 3.1 In Scope for v0.1

The v0.1 repository implementation MUST include:

1. GitHub pull request diff ingestion
2. deterministic diff normalization
3. mutation surface classification
4. severity classification
5. consequence generation
6. trust-state decision
7. replay integrity signals
8. GitHub-ready Markdown rendering
9. PR comment creation or update
10. demo scenarios
11. README oriented around Replay, not architecture

### 3.2 Explicitly Out of Scope for v0.1

The v0.1 implementation MUST NOT include:

- SaaS dashboard
- user accounts
- billing
- enterprise admin UI
- MCP support
- multi-agent orchestration
- cloud/IAM/payment/browser executors
- policy DSL
- full authority core
- full Global Action Ledger
- full Constitutional Governance
- direct repository mutation
- automatic merge
- autonomous production execution

The purpose of v0.1 is to prove replay cognition, not to implement the full authority system.

---

## 4. DETERMA Factory Operating Model

Autonomous work must follow separation of duties.

### 4.1 Worker v1 — Planner

Worker v1 MAY:

- create plans
- create specs
- define schemas
- define acceptance tests
- define task boundaries
- define approval checkpoints

Worker v1 MUST NOT:

- write executable code
- run commands
- mutate repository state
- bypass approvals
- expand scope

### 4.2 Worker v2 — Builder

Worker v2 MAY generate artifacts only:

- code proposals
- tests
- Markdown documentation
- schemas
- config proposals
- GitHub workflow proposals
- demo artifacts

Worker v2 MUST NOT:

- execute generated artifacts
- apply changes directly to protected branches
- perform arbitrary shell execution
- push, merge, deploy, or mutate external systems
- bypass the orchestrator or human gate

### 4.3 Worker v3 — Adversary / QA

Worker v3 MUST attempt to break the implementation.

Worker v3 validates:

- deterministic behavior
- classification correctness
- false-positive boundaries
- false-negative high-risk cases
- renderer stability
- replay integrity
- GitHub comment behavior
- demo correctness

### 4.4 Orchestrator / Authority

The Orchestrator is responsible for:

- job lifecycle
- scope validation
- approval gates
- audit events where available
- state transitions
- enforcing halt conditions

The Orchestrator MUST NOT:

- execute work
- generate artifacts
- bypass approvals
- silently expand scope

### 4.5 Human Gate

The human approves batches, not every tiny file.

Human approval is required at:

1. Scope Lock
2. Spec Approval
3. Implementation Batch Approval
4. QA Pass
5. Demo Approval
6. Public Packaging Approval

---

## 5. Repository Structure

The implementation SHOULD use the following repository layout:

```text
docs/
  canonical/
    DETERMA_REPLAY_MVP_FACTORY_PLAN.md
    DETERMA_REPLAY_MVP_SPEC.md
    REPLAY_SCHEMA.md
    MUTATION_SURFACES.md
  adr/
    ADR-0001-replay-first-wedge.md

src/
  determa_replay/
    __init__.py
    diff_parser.py
    surface_classifier.py
    severity_engine.py
    consequence_engine.py
    trust_engine.py
    replay_model.py
    markdown_renderer.py
    github_comment.py
    integrity.py

tests/
  test_diff_parser.py
  test_surface_classifier.py
  test_severity_engine.py
  test_consequence_engine.py
  test_trust_engine.py
  test_markdown_renderer.py
  test_integrity.py

examples/
  demo_prs/
    deployment_rollout_change.patch
    ci_tests_removed.patch
    auth_middleware_change.patch
    business_logic_change.patch
    docs_only_change.patch
  expected_replays/

.github/
  workflows/
    determa-replay.yml

README.md
```

---

## 6. Canonical Replay Artifact

Every replay MUST follow this structure:

```text
DETERMA Mutation Replay

Replay ID:
<id>

Severity:
LOW | MEDIUM | HIGH | CRITICAL

Trust State:
TRUSTED | REQUIRES_APPROVAL | BLOCKED | UNEXPLAINABLE

Mutation Surface:
<one or more surfaces>

Human Summary:
<plain-language explanation>

What Changed:
<short deterministic summary>

Potential Consequences:
- <consequence 1>
- <consequence 2>

Replay Timeline:
- Diff received
- Files classified
- Risk evaluated
- Trust state determined

Replay Integrity:
✓ diff parsed
✓ mutation surface classified
✓ deterministic replay generated

Recommended Action:
<merge / review / block / approval required>
```

The replay artifact is the product.

---

## 7. Canonical Mutation Surfaces

The first implementation MUST support the following surfaces:

| Surface | Example paths |
|---|---|
| CI/CD | `.github/workflows/*`, `.gitlab-ci.yml`, `circleci/*` |
| Deployment Infrastructure | deploy scripts, rollout configs, release workflows |
| Runtime Infrastructure | `Dockerfile`, `docker-compose.yml`, Helm, Kubernetes manifests |
| Infrastructure as Code | `terraform/*`, `opentofu/*`, `pulumi/*` |
| Secret Access | `.env*`, secret references, credential config |
| Authentication / IAM | `auth/*`, `iam/*`, permissions, roles, policies |
| Database Migration | `migrations/*`, schema changes |
| Business Logic | application domain logic |
| Tests | test files, test config, coverage gates |
| Documentation | `README.md`, docs-only changes |

---

## 8. Severity Rules

The first implementation SHOULD be deterministic and rule-based.

### 8.1 CRITICAL

Classify as CRITICAL when the mutation touches:

- production deployment behavior
- secrets or credentials
- authentication or authorization enforcement
- IAM or permissions
- database destructive migration
- payment or financial business logic
- CI/CD release gates that affect production

### 8.2 HIGH

Classify as HIGH when the mutation touches:

- infrastructure configuration
- Docker/runtime behavior
- Kubernetes deployment behavior
- security configuration
- dependency trust boundaries
- test disabling or reduced verification

### 8.3 MEDIUM

Classify as MEDIUM when the mutation touches:

- normal business logic
- non-critical service behavior
- application configuration with limited operational blast radius

### 8.4 LOW

Classify as LOW when the mutation is limited to:

- documentation
- comments
- formatting
- non-executable metadata

---

## 9. Trust State Rules

The first implementation MUST support:

```text
TRUSTED
REQUIRES_APPROVAL
BLOCKED
UNEXPLAINABLE
```

### TRUSTED

Allowed only when:

- diff is parsed successfully
- mutation surface is low-risk
- no high-risk patterns detected
- replay integrity is complete

### REQUIRES_APPROVAL

Used when:

- mutation touches high-impact surfaces
- operational consequence exists
- human review is required before merge

### BLOCKED

Used when:

- mutation appears to bypass tests
- mutation weakens deployment safety
- mutation touches secrets directly
- mutation weakens auth/IAM controls
- diff cannot be safely interpreted but appears operationally risky

### UNEXPLAINABLE

Used when:

- diff cannot be parsed
- file context is missing
- replay cannot be deterministically reconstructed
- required fields are absent

Fail closed on ambiguity.

---

## 10. Replay Integrity Signals

v0.1 MUST include basic integrity signals:

```text
✓ diff parsed
✓ mutation surface classified
✓ deterministic replay generated
```

v0.2 SHOULD add:

- replay ID
- diff hash
- file hashes
- deterministic reconstruction check
- missing event detection
- authority continuity signal

---

## 11. PR Plan

### PR-1 — Canonical Replay MVP Spec

Create:

- `docs/canonical/DETERMA_REPLAY_MVP_SPEC.md`
- `docs/canonical/REPLAY_SCHEMA.md`
- `docs/canonical/MUTATION_SURFACES.md`
- `docs/adr/ADR-0001-replay-first-wedge.md`

Acceptance:

- v0.1 scope is locked
- out-of-scope list is explicit
- replay schema is stable
- no execution features included

---

### PR-2 — Diff Parser

Create:

- `src/determa_replay/diff_parser.py`
- `tests/test_diff_parser.py`

Acceptance:

- parses modified files
- parses added files
- parses deleted files
- preserves file paths
- deterministic output
- no network access

---

### PR-3 — Mutation Surface Classifier

Create:

- `src/determa_replay/surface_classifier.py`
- `tests/test_surface_classifier.py`

Acceptance:

- classifies CI/CD paths
- classifies deployment paths
- classifies secrets/auth/IAM paths
- classifies docs-only changes
- returns deterministic surfaces

---

### PR-4 — Severity, Consequence, Trust Engines

Create:

- `src/determa_replay/severity_engine.py`
- `src/determa_replay/consequence_engine.py`
- `src/determa_replay/trust_engine.py`
- related tests

Acceptance:

- CRITICAL/HIGH/MEDIUM/LOW computed deterministically
- consequence templates generated
- trust state generated
- high-risk unknowns fail closed

---

### PR-5 — Markdown Replay Renderer

Create:

- `src/determa_replay/replay_model.py`
- `src/determa_replay/markdown_renderer.py`
- `tests/test_markdown_renderer.py`

Acceptance:

- renders canonical GitHub Markdown
- stable output snapshots
- easy to screenshot
- no cryptographic jargon in user-facing output

---

### PR-6 — GitHub Action PR Comment Integration

Create:

- `.github/workflows/determa-replay.yml`
- `src/determa_replay/github_comment.py`

Acceptance:

- runs on pull request opened/synchronize
- posts a DETERMA Replay comment
- updates existing DETERMA comment rather than spamming duplicates
- does not mutate repository code
- fails safely if GitHub token is missing or insufficient

---

### PR-7 — Demo Pack and README

Create:

- demo PR patches
- expected replay outputs
- revised README
- 90-second demo script

Acceptance:

- demo shows deployment rollout risk
- demo shows CI test removal risk
- demo shows docs-only trusted change
- README explains product in under 30 seconds

---

### PR-8 — Replay Integrity Basic

Create:

- `src/determa_replay/integrity.py`
- `tests/test_integrity.py`

Acceptance:

- replay ID generated
- diff hash included
- deterministic replay marker included
- integrity section rendered in PR comment

---

## 12. Definition of Done for v0.1

v0.1 is complete only when:

1. A GitHub pull request triggers DETERMA Replay.
2. DETERMA reads the PR diff.
3. DETERMA classifies mutation surfaces.
4. DETERMA computes severity.
5. DETERMA generates consequences.
6. DETERMA determines trust state.
7. DETERMA posts or updates a single PR comment.
8. The output is deterministic.
9. The demo repository includes at least five scenarios.
10. README explains the product clearly.
11. Tests pass.
12. The demo can be shown in 90 seconds.

---

## 13. Required Demo Scenarios

### Demo 1 — Production rollout changed

Input:

- `.github/workflows/deploy.yml`
- rollout threshold changes from 10% to 100%

Expected:

- Severity: CRITICAL
- Surface: CI/CD, Deployment Infrastructure
- Trust State: BLOCKED or REQUIRES_APPROVAL
- Consequence: production rollout behavior altered

### Demo 2 — CI tests removed

Expected:

- Severity: HIGH
- Surface: CI/CD, Tests
- Trust State: BLOCKED
- Consequence: verification weakened

### Demo 3 — Auth middleware changed

Expected:

- Severity: HIGH
- Surface: Authentication / IAM
- Trust State: REQUIRES_APPROVAL
- Consequence: access behavior may change

### Demo 4 — Business logic changed

Expected:

- Severity: MEDIUM
- Surface: Business Logic
- Trust State: REQUIRES_APPROVAL or TRUSTED depending on path

### Demo 5 — README only

Expected:

- Severity: LOW
- Surface: Documentation
- Trust State: TRUSTED
- Consequence: no operational impact detected

---

## 14. Security and Governance Constraints

The implementation MUST preserve the DETERMA authority model.

Rules:

- Worker v2 may generate artifacts only.
- No worker may execute arbitrary shell commands.
- No worker may mutate protected branches.
- No executor may exist in v0.1.
- No merge automation may exist in v0.1.
- All ambiguity must fail closed.
- User-facing output must be understandable by engineers.
- Internal architecture may be deep, but product output must be simple.

---

## 15. Roadmap After v0.1

### v0.2 — Replay Integrity

Add:

- replay ID
- diff hash
- file hashes
- deterministic reconstruction flag
- missing context detection

### v0.3 — Approval Gate

Add:

- GitHub Check integration
- HIGH/CRITICAL requires human approval
- approval record in replay output

### v0.4 — State Witness

Add:

- branch head witness
- target file hash witness
- approval expiry when repository state changes

Canonical message:

```text
Approval expired because repository state changed.
```

### v0.5 — Execution Release

Add:

- single-use release
- TTL
- executor match
- release consumed marker

No mutation without:

- approval
- valid witness
- valid release

### v1.0 — Governed Code Mutation

Add:

- constrained Git patch executor
- post-execution verification
- immutable action lineage
- enterprise evidence export

---

## 16. Success Metrics

Do not optimize for:

- number of policies
- dashboard complexity
- orchestration sophistication
- abstract governance depth

Optimize for:

```text
Did DETERMA Replay change merge behavior?
```

Track:

- number of PRs replayed
- number of HIGH/CRITICAL replays
- number of BLOCKED recommendations
- number of reviewer interventions
- number of false positives
- number of false negatives
- number of screenshots shared
- number of demo conversions

---

## 17. Canonical Factory Prompt

Use this prompt to start autonomous work:

```text
You are operating as the DETERMA Factory.

Your mission is to implement the first market-facing MVP:
DETERMA Replay for AI-generated Pull Requests.

Do not build the full DETERMA platform.
Do not build a dashboard.
Do not build MCP.
Do not build billing, users, SaaS, or enterprise policy DSL.

Canonical product definition:
DETERMA observes, replays, and explains AI-generated code mutations.

Primary wedge:
GitHub-native replay for AI-generated mutations.

Required output:
A GitHub Action or GitHub-native integration that comments on pull requests with a deterministic DETERMA Mutation Replay.

The replay must include:
- severity
- trust state
- mutation surface
- human summary
- what changed
- potential consequences
- replay integrity
- recommended action

Architecture constraints:
- Core classification must be deterministic and rule-based at first.
- Worker v2 may generate artifacts only and must not execute them.
- No repo mutation may occur without explicit approval.
- No executor logic in Worker v2.
- No direct mutation path.
- Fail closed on ambiguity.
- Every feature must map to one of:
  Mutation, Replay, Trust, Consequence.

Execution plan:
PR-1: Canonical Replay MVP Spec
PR-2: Diff Parser
PR-3: Mutation Surface Classifier
PR-4: Severity, Consequence, Trust Engines
PR-5: Markdown Replay Renderer
PR-6: GitHub Action PR Comment Integration
PR-7: Demo Pack and README
PR-8: Replay Integrity Basic

Definition of Done for v0.1:
When a pull request is opened or updated, DETERMA posts or updates a single replay comment that explains:
what changed, why it matters, whether it is trusted, and what action the reviewer should take.

Demo scenario:
AI modifies a deployment workflow and changes rollout behavior from 10% to 100%.
DETERMA classifies it as CRITICAL, identifies Deployment/CI-CD surface, explains production impact, and recommends blocking or human approval.

Do not expand scope until v0.1 is complete.
```

---

## 18. Final Ruling

The repository must begin with Replay, not Authority.

The correct sequence is:

```text
Replay
→ Replay Integrity
→ Approval Gate
→ State Witness
→ Execution Release
→ Governed Code Mutation
→ Global Action Ledger
```

This is the shortest path from deep architecture to market-visible product.

Any work that does not strengthen the first GitHub-native Replay loop should be deferred.
