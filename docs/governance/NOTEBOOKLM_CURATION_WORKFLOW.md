# DETERMA NotebookLM Curation Workflow

## Purpose

This document defines the canonical workflow for constructing DETERMA NotebookLM corpora.

The objective is to:

- support guided understanding
- preserve disclosure boundaries
- reduce retrieval leakage
- standardize corpus construction

---

# Canonical Principle

```text
NotebookLM corpora should be curated intentionally, not assembled automatically.
```

---

# Workflow Stages

## Stage 1 — Classification

Classify material as:

- PUBLIC_SAFE
- DILIGENCE
- INTERNAL_CORE
- RESTRICTED

using:

```text
DOCUMENT_CLASSIFICATION_MATRIX.md
```

---

## Stage 2 — Sanitization Review

Verify:

- implementation mechanics removed
- moat-critical semantics abstracted
- runtime philosophy preserved
- conceptual continuity maintained

using:

```text
SANITIZATION_POLICY.md
```

---

## Stage 3 — Corpus Construction

Construct corpora intentionally:

| Corpus | Allowed Material |
|---|---|
| Public | PUBLIC_SAFE only |
| Diligence | PUBLIC_SAFE + approved DILIGENCE |
| Internal | Internal-only |

---

## Stage 4 — Retrieval Leakage Review

Review whether retrieval could unintentionally expose:

- hidden architecture semantics
- restricted governance details
- moat-critical sequencing
- implementation invariants

---

## Stage 5 — Canonical Verification

Verify:

- references point to canonical sources
- deprecated material excluded
- superseded semantics excluded
- sanitized derivatives remain aligned

---

# Forbidden Practices

Do not:

- ingest unrestricted repositories directly
- expose restricted archives to public corpora
- mix public and restricted corpora
- expose deep implementation lineage unintentionally

---

# Canonical Principle

```text
Retrieval systems are architectural exposure surfaces.
```
