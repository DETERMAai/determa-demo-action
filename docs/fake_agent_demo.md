# Controlled Agent Simulation Demo

Run:

```bash
python3 scripts/fake_agent_loop.py
```

What it simulates:

1. Valid governed execution (`make demo`) -> allowed
2. Replay of same execution (`make demo`) -> blocked/idempotent
3. Adversarial bypass attempts (`make demo-attack`) -> blocked
4. Witness tampering (`python3 scripts/run_product_demo.py --operator-token demo-token --break-witness`) -> fail-closed blocked

Expected result:

```text
Result: AGENT CONTAINED BY DETERMA
```

This demo does not use a real LLM and does not add autonomous execution. It only verifies that demo command paths stay contained by DETERMA fail-closed controls.
