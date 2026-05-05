# Public Demo Export Checklist

## Files Included

- `README.md`
- `action.yml`
- `entrypoint.sh`
- `Makefile`
- `docs/marketplace_demo.md`
- `docs/product_demo.md`
- `docs/dev_demo.md`
- `docs/fake_agent_demo.md`
- `docs/assets/determa-hero.svg`
- `scripts/run_product_demo.py`
- `scripts/run_adversarial_demo.py`
- `scripts/fake_agent_loop.py`
- `tests/test_public_demo_package.py`

## Files Intentionally Excluded

- `app/orchestrator/app.py`
- `init.sql`
- `app/` authority-core and executor modules
- patent, provisional, and internal strategy documents
- V6 internal roadmap and private architecture materials

## Publish Steps

1. Create new repository `DETERMAai/determa-demo-action`.
2. Copy only the files listed in this package.
3. Verify zero-setup scripts run in mock mode.
4. Verify action default mode uses mock demo.
5. Add release notes describing demo-only scope.
6. Create tag `v0.1.0`.

## Planned Release Tag

- `v0.1.0`
