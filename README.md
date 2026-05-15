# DETERMA

Governed execution infrastructure for runtime legitimacy.

## NotebookLM (Public Architecture Layer)

All public, NotebookLM-safe architecture and conceptual documents are curated in:

- `docs/notebooklm/`

Notebook link:

- https://notebooklm.google.com/notebook/1c7fd705-9634-48e7-9249-4b06a0a6a2ef?authuser=8

Suggested questions:

- How does deterministic replay work?
- Why are capabilities single-use?
- How does DETERMA prevent replay attacks?
- What happens if runtime state changes?
- How does append-only lineage work?
- Why govern execution instead of prompts?
- How does DETERMA differ from approval workflows?

## Public Scope

This public repository explains:

- governed execution
- runtime legitimacy
- runtime drift
- mutation legitimacy
- replay-aware execution
- execution-boundary consistency

Certain operational enforcement details are intentionally excluded from the public materials.

The public repository focuses on runtime legitimacy concepts, governed execution architecture, and the execution-boundary problem category.

## One-Command Demo

Run the governed execution demo flow:

```bash
python scripts/demo_governed_flow.py
```

Launch the runtime shell:

```bash
uvicorn runtime.api_shell:app --host 127.0.0.1 --port 8001
```

Open the demo:

- `http://127.0.0.1:8001/demo`

## Public Documentation Map

### Public Conceptual Docs

- `docs/public/governed_execution_overview.md`
- `docs/public/runtime_legitimacy_and_drift.md`
- `docs/public/mutation_legitimacy_walkthrough.md`
- `docs/public/replay_aware_execution_consequences.md`
- `docs/public/high_level_architecture_semantics.md`
- `docs/public/market_category_framing.md`

### NotebookLM Source Set

- `docs/notebooklm/README.md`
- `docs/notebooklm/faq.md`
- `docs/notebooklm/runtime_legitimacy_primer.md`
- `docs/notebooklm/governed_execution_walkthrough.md`
- `docs/notebooklm/replay_aware_category_note.md`

## Public/Private Separation

Public materials are designed for:

- investor exploration
- design partner onboarding
- architectural understanding
- category positioning

Private operational materials (enforcement internals, implementation details, and security-sensitive mechanics) are staged in `docs/private_archive/` for relocation to private storage/repository.

## Category Statement

DETERMA addresses a specific infrastructure problem:

approval and execution can diverge when runtime reality changes.

The runtime legitimacy boundary exists at execution time, not approval time.
