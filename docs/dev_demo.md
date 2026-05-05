# Developer Demo Commands

## Quick Start

Run a zero-setup governed demo:

```bash
make demo
```

## Real GitHub Sandbox Mode

```bash
export DETERMA_DEMO_REAL_GITHUB=1
export GITHUB_TOKEN=ghp_xxx
export DETERMA_DEMO_REPO=org/demo-repo
export DETERMA_DEMO_BRANCH=determa-demo/dev-demo
make demo-real
```

## Other Commands

```bash
make demo-attack
make demo-all
make demo-report
```

## Expected Outputs

- `make demo`: governed execution output with replay blocked.
- `make demo-real`: real sandbox Draft PR output (only with explicit opt-in env).
- `make demo-attack`: adversarial scenarios all blocked.
- `make demo-all`: governed demo, replay proof, adversarial proof in one run.
- `make demo-report`: writes `reports/governed_pr_demo.md` and `reports/governed_pr_demo.json`.

## Troubleshooting

- `Missing DETERMA_DEMO_REAL_GITHUB=1`: set explicit real-mode opt-in env.
- `Missing GITHUB_TOKEN`: export a valid GitHub token.
- `Missing DETERMA_DEMO_REPO`: set sandbox repo as `org/repo`.
- Branch blocked: ensure branch matches `determa-demo/*`.

## Required Env Vars (real mode)

- `DETERMA_DEMO_REAL_GITHUB=1`
- `GITHUB_TOKEN`
- `DETERMA_DEMO_REPO`
- optional: `DETERMA_DEMO_BRANCH` (default `determa-demo/dev-demo`)
- optional: `OPERATOR_API_TOKEN` (default `demo-token`)
