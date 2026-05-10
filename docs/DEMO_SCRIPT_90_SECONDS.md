# DETERMA Replay — 90 Second Demo Script

## Goal

Show that DETERMA can replay and explain AI-generated code mutations before merge.

The audience should understand the product in under 90 seconds.

---

## Demo Setup

Open a pull request containing:

```text
examples/demo_prs/deployment_rollout_change.patch
```

The PR changes deployment rollout behavior from:

```text
10%
```

to:

```text
100%
```

---

## Demo Flow

### Step 1 — Show the PR

Explain:

```text
An AI coding assistant generated this pull request.
```

Show the deployment workflow diff.

---

### Step 2 — Wait for DETERMA Replay

Show the DETERMA Replay comment.

Point to:

- Severity
- Trust State
- Mutation Surfaces
- Potential Consequences

---

### Step 3 — Explain the Insight

Explain:

```text
The problem is not just that code changed.
The problem is that deployment behavior changed.
```

Then explain:

```text
DETERMA reconstructs operational meaning before humans trust the mutation.
```

---

### Step 4 — Show Human Action

Point to:

```text
Recommended Action:
Human approval required before merge.
```

Explain:

```text
DETERMA does not auto-merge.
It creates replayable trust before merge.
```

---

## Optional Follow-up Demos

1. CI tests removed
2. Auth middleware changed
3. Documentation-only change

---

## Closing Sentence

```text
Before trusting AI-generated code, replay the mutation.
```
