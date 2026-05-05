>>> Looking for design partners using AI coding agents in GitHub workflows.

# DETERMA Public Demo Action

This is a public demo package. The production DETERMA authority core is not included.

## What this package demonstrates

- governed demo execution path
- draft PR output (mock by default)
- replay blocked / idempotent behavior
- adversarial attempts blocked fail-closed

## Zero-setup demo

```bash
python3 scripts/run_product_demo.py --operator-token demo-token
python3 scripts/run_adversarial_demo.py
python3 scripts/fake_agent_loop.py
```

## GitHub Action demo usage

```yaml
name: DETERMA Demo
on:
  workflow_dispatch:

jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./
        with:
          operator-token: demo-token
          real-github: "false"
```

## Real GitHub sandbox mode (explicit opt-in)

Required:

- `DETERMA_DEMO_REAL_GITHUB=1`
- `GITHUB_TOKEN`
- `DETERMA_DEMO_REPO`

Optional:

- `DETERMA_DEMO_BASE_BRANCH` (default: `main`)
- `branch` input (`determa-demo/*` only)

## Safety notes

- demo package only
- no auto-merge
- no production branch writes
- no production authority core included


## Contact

Interested in governed AI execution for your engineering team?

Contact:
- Email: determa.ai@gmail.com
- GitHub Issues: open an issue with the label `design-partner`
