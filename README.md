# DETERMA Replay

Observe, replay, and explain AI-generated code mutations.

---

## The Problem

AI coding agents can change:

- deployment behavior,
- CI/CD pipelines,
- permissions,
- infrastructure,
- secrets,
- production rollout logic.

Humans usually see the code diff.

But they do not immediately see the operational consequences.

---

## The Solution

DETERMA generates a deterministic Mutation Replay for pull requests.

Before merge, DETERMA explains:

- what changed,
- why it matters,
- which operational surfaces were touched,
- whether the mutation should be trusted,
- what the reviewer should do next.

---

## Example Replay

```text
# DETERMA Mutation Replay

Severity:
CRITICAL

Trust State:
REQUIRES_APPROVAL

Mutation Surface:
CI/CD / Deployment Infrastructure

Potential Consequences:
- Production rollout behavior may be altered.
- Release safety controls may be reduced or bypassed.

Recommended Action:
Human approval required before merge.
```

---

## Why This Exists

The problem is not only that AI writes code.

The real problem is that AI-generated mutations can change operational behavior faster than humans can reconstruct intent.

DETERMA exists to reconstruct operational meaning before trust.

---

## Current MVP Scope

DETERMA Replay v0.1 currently supports:

- GitHub pull request diff parsing
- mutation surface classification
- severity classification
- consequence generation
- trust-state generation
- replay integrity markers
- GitHub PR replay comments

Current surfaces:

- CI/CD
- Deployment Infrastructure
- Runtime Infrastructure
- Infrastructure as Code
- Secret Access
- Authentication / IAM
- Database Migration
- Business Logic
- Tests
- Documentation

---

## Demo Scenarios

Example replay scenarios:

```text
examples/demo_prs/
```

Included demos:

- deployment rollout changed from 10% to 100%
- CI tests removed
- auth middleware bypass
- business logic mutation
- documentation-only change

Expected replay outputs:

```text
examples/expected_replays/
```

---

## Quick Start

### 1. Enable GitHub Actions

The repository includes:

```text
.github/workflows/determa-replay.yml
```

### 2. Open a Pull Request

Create a PR with a deployment, auth, CI/CD, or infrastructure mutation.

### 3. Wait for DETERMA Replay

DETERMA will:

- fetch the PR diff,
- classify mutation surfaces,
- compute severity,
- generate consequences,
- determine trust state,
- post or update a replay comment.

---

## Architecture

Canonical replay pipeline:

```text
Pull Request Event
→ Diff Fetch
→ Diff Parser
→ Mutation Surface Classification
→ Severity Engine
→ Consequence Engine
→ Trust Engine
→ Replay Integrity
→ Markdown Renderer
→ GitHub Replay Comment
```

---

## Design Constraints

DETERMA Replay v0.1 intentionally:

- does not auto-merge,
- does not mutate repositories,
- does not execute arbitrary code,
- does not bypass human approval,
- fails closed on ambiguity.

---

## Category

```text
AI Mutation Replay
```

Core behavioral reflex:

```text
Before trusting AI-generated code,
check the DETERMA Replay.
```

---

## Roadmap

Canonical sequence:

```text
Replay
→ Replay Integrity
→ Approval Gate
→ State Witness
→ Execution Release
→ Governed Code Mutation
→ Global Action Ledger
```

---

## Repository Structure

```text
src/determa_replay/
examples/demo_prs/
examples/expected_replays/
docs/
.github/workflows/
```

---

## Status

Prototype / MVP stage

Replay-first GitHub-native wedge.

---

## Contact

Looking for engineering teams using AI coding agents who want replayable trust before merge.

- GitHub: open an issue
- Email: determa.ai@gmail.com
