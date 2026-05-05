# DETERMA Marketplace Demo

This is a **demo package**, not a production deployment path.

## Core Message

AI can propose code changes. DETERMA decides whether execution is allowed.

## What the Demo Shows

- governed Draft PR creation
- replay protection
- fail-closed adversarial blocking
- execution release gate
- state witness verification

## Quick Start

```bash
make demo
make demo-attack
make demo-all
```

## GitHub Action Usage

```yaml
name: DETERMA Demo
on:
  workflow_dispatch:

jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DETERMAai/thefactory@v0.1.0
        with:
          operator-token: demo-token
          real-github: "false"
```

Local action reference:

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: ./
    with:
      operator-token: demo-token
      real-github: "false"
```

## Real GitHub Sandbox Mode (Explicit Opt-In)

Required:

- `DETERMA_DEMO_REAL_GITHUB=1`
- `GITHUB_TOKEN`
- `DETERMA_DEMO_REPO`
- optional: `DETERMA_DEMO_BASE_BRANCH` (default `main`)

Rules:

- default mode uses mock PR behavior
- sandbox repo only
- No auto-merge.
- no production branch writes
- branch must match `determa-demo/*`

## Status

- Demo / design-partner stage
- Not production-ready
