# DETERMA Replay — GitHub App Architecture

## Purpose

Define the canonical architecture for the DETERMA GitHub App.

This document bridges:

```text
GitHub Action MVP
→ GitHub-native Replay Platform
→ Governed Mutation Authority
```

---

# Architectural Principle

The GitHub App is:

```text
an operational trust observer
```

not:

```text
an autonomous execution agent
```

v0.x must remain replay-first.

---

# Initial GitHub App Responsibilities

The app should:

1. subscribe to pull request events
2. fetch pull request diffs
3. generate deterministic replay artifacts
4. classify operational mutation surfaces
5. compute trust states
6. publish replay comments
7. update replay comments on synchronization
8. maintain replay integrity metadata

---

# Explicit Non-Goals

The GitHub App must NOT:

- auto-merge pull requests
- execute repository code
- approve pull requests automatically
- mutate infrastructure
- issue runtime credentials
- bypass branch protections
- execute deployment workflows

---

# Event Model

## Initial Events

```text
pull_request.opened
pull_request.synchronize
pull_request.reopened
```

---

## Future Events

```text
pull_request_review.submitted
push
workflow_run.completed
check_suite.completed
issue_comment.created
```

---

# Core Replay Pipeline

```text
GitHub Event
→ Diff Fetch
→ Diff Parse
→ Surface Classification
→ Severity Evaluation
→ Consequence Generation
→ Trust-State Determination
→ Replay Integrity
→ Markdown Rendering
→ Replay Publication
```

---

# Core Replay Components

## Diff Parser

Purpose:

Deterministic extraction of changed operational surfaces.

---

## Surface Classifier

Purpose:

Map repository mutations into operational meaning.

---

## Severity Engine

Purpose:

Estimate operational risk.

---

## Consequence Engine

Purpose:

Explain why mutations matter.

---

## Trust Engine

Purpose:

Determine reviewer trust posture.

---

## Integrity Layer

Purpose:

Ensure replay determinism and replay reconstruction.

---

# GitHub Permissions

## Required v0.x Permissions

### Pull Requests

```text
Read & Write
```

Reason:

Replay comments.

---

### Issues

```text
Read & Write
```

Reason:

PR comments are issue comments.

---

### Contents

```text
Read-only
```

Reason:

Repository metadata and optional future context.

---

# Replay Persistence

Initial persistence:

```text
GitHub comment only
```

Future persistence:

```text
Replay database
Replay lineage
Mutation history
Replay analytics
Replay audit trail
```

---

# Multi-Repository Model

Future architecture should support:

```text
Organization
→ Repository
→ Pull Request
→ Replay Artifact
→ Mutation Lineage
```

---

# Trust-State Philosophy

The app should optimize for:

```text
operational trust reconstruction
```

not:

```text
developer productivity theater
```

---

# Replay Determinism Rules

Replay output must:

- remain stable across executions,
- avoid hallucinated claims,
- derive only from observable evidence,
- fail closed on ambiguity.

---

# Future Evolution Path

## Stage 1

```text
Replay Layer
```

## Stage 2

```text
Replay + Approval Gates
```

## Stage 3

```text
Replay + State Witness
```

## Stage 4

```text
Governed Mutation Authority
```

## Stage 5

```text
Global Mutation Ledger
```

---

# Canonical Strategic Position

Externally:

```text
GitHub-native AI Mutation Replay
```

Internally:

```text
Deterministic Operational Trust Infrastructure
```
