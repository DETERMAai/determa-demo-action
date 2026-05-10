# DETERMA Replay Schema

Status: Canonical v0.1 schema  
Date: 2026-05-10  
Authority: `docs/canonical/DETERMA_REPLAY_MVP_FACTORY_PLAN.md`

---

## 1. Purpose

Define the canonical replay object for DETERMA Replay v0.1.

This schema is intentionally small and user-facing. It exists to make AI-generated code mutations understandable before merge.

---

## 2. Canonical Replay Object

```json
{
  "replay_id": "string",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "trust_state": "TRUSTED|REQUIRES_APPROVAL|BLOCKED|UNEXPLAINABLE",
  "mutation_surfaces": ["string"],
  "human_summary": "string",
  "what_changed": ["string"],
  "potential_consequences": ["string"],
  "replay_timeline": ["string"],
  "replay_integrity": {
    "diff_parsed": true,
    "mutation_surface_classified": true,
    "deterministic_replay_generated": true
  },
  "recommended_action": "string"
}
```

---

## 3. Field Requirements

### replay_id

Required string.

v0.1 may generate a deterministic or stable local identifier.

v0.2 should bind replay ID to a diff hash.

### severity

Required enum:

- LOW
- MEDIUM
- HIGH
- CRITICAL

### trust_state

Required enum:

- TRUSTED
- REQUIRES_APPROVAL
- BLOCKED
- UNEXPLAINABLE

### mutation_surfaces

Required array of one or more strings.

Values SHOULD come from `MUTATION_SURFACES.md`.

### human_summary

Required string.

Must be plain operational language.

Must not expose protocol jargon.

### what_changed

Required array.

Each item should describe a concrete observed change.

### potential_consequences

Required array.

Each item should explain why the change may matter operationally.

### replay_timeline

Required array.

v0.1 timeline SHOULD include:

- Diff received
- Files classified
- Risk evaluated
- Trust state determined

### replay_integrity

Required object.

v0.1 required booleans:

- diff_parsed
- mutation_surface_classified
- deterministic_replay_generated

### recommended_action

Required string.

Examples:

- Safe to review normally.
- Human approval required before merge.
- Do not merge until the change is explicitly reviewed.
- Replay could not be reconstructed. Treat as untrusted.

---

## 4. Rendering Rule

The Markdown renderer MUST render the replay object without losing any required field.

---

## 5. Determinism Rule

Given the same replay object, the renderer MUST produce byte-stable Markdown output.
