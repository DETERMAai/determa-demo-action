# DETERMA Deprecation and Supersession Policy

## Purpose

This document defines how documents, architectures, doctrines, and runtime semantics should evolve without losing continuity.

The objective is to:

- preserve historical reasoning
- prevent architectural drift
- avoid duplicate truths
- maintain canonical lineage
- support long-term governance continuity

---

# Canonical Principle

```text
Old knowledge should be archived, not erased.
```

---

# Definitions

## Canonical

The current authoritative source.

---

## Superseded

Previously authoritative material that has been replaced by a newer canonical source.

---

## Deprecated

Material that should no longer guide implementation or positioning decisions.

---

## Archived

Historical material preserved for continuity, reasoning lineage, and strategic memory.

---

# Evolution Rules

## Rule 1

Do not silently replace canonical documents.

---

## Rule 2

When superseding a document:

- preserve the historical version
- mark the relationship clearly
- reference the new canonical source

---

## Rule 3

Avoid multiple active canonical sources for the same concept.

---

# Recommended Markers

## Canonical Marker

```text
STATUS: CANONICAL
```

---

## Superseded Marker

```text
STATUS: SUPERSEDED
SUPERSEDED_BY: <document>
```

---

## Deprecated Marker

```text
STATUS: DEPRECATED
```

---

## Archived Marker

```text
STATUS: ARCHIVED
```

---

# Archive Philosophy

Historical material may remain strategically valuable even when no longer canonical.

Reasoning lineage matters.

---

# NotebookLM Rule

NotebookLM corpora should prioritize canonical and sanitized materials.

Deprecated or superseded documents should not appear in public-facing corpora unless intentionally curated.

---

# Canonical Principle

```text
Continuity requires lineage, not just the latest version.
```
