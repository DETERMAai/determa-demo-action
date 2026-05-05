# Product Collapse Demo (30 seconds)

Run one command:

```bash
python3 scripts/run_product_demo.py --operator-token "$OPERATOR_API_TOKEN"
```

Default behavior:

- mock mode only
- no real GitHub execution
- uses existing governed PR demo + replay proof
- writes reports:
  - `reports/governed_pr_demo.md`
  - `reports/governed_pr_demo.json`

Expected success output:

```text
=== DETERMA Governed PR Demo ===

AI Change: demo_patch.diff
Approval: ✅ APPROVED
Capability: ✅ ISSUED
State Witness: ✅ MATCHED
Execution Release: ✅ CONSUMED

Draft PR: <mock_or_real_pr_url>

Replay Attempt: ✅ BLOCKED / IDEMPOTENT
Duplicate Execution: ❌ NONE

Result: GOVERNED EXECUTION ENFORCED
```

Fail-closed witness mismatch demo:

```bash
python3 scripts/run_product_demo.py --operator-token "$OPERATOR_API_TOKEN" --break-witness
```

Expected fail-closed output:

```text
=== DETERMA Governed PR Demo ===

State Witness: ❌ MISMATCH
Execution: BLOCKED
Result: FAIL-CLOSED
```
