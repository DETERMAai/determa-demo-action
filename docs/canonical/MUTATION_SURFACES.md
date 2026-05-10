# DETERMA Mutation Surfaces

Status: Canonical v0.1 classification map  
Date: 2026-05-10  
Authority: `docs/canonical/DETERMA_REPLAY_MVP_FACTORY_PLAN.md`

---

## 1. Purpose

Define the first deterministic mutation surface taxonomy for DETERMA Replay v0.1.

Mutation surfaces explain what operational area an AI-generated code change may affect.

---

## 2. Canonical Surfaces

### CI/CD

Examples:

- `.github/workflows/*`
- `.gitlab-ci.yml`
- `circleci/*`
- `jenkins/*`
- build/test/release pipeline files

Operational meaning:

The mutation may affect how code is tested, built, released, or deployed.

---

### Deployment Infrastructure

Examples:

- deployment scripts
- rollout configuration
- release gates
- production promotion logic
- deployment workflow files

Operational meaning:

The mutation may affect how changes reach production.

---

### Runtime Infrastructure

Examples:

- `Dockerfile`
- `docker-compose.yml`
- Helm charts
- Kubernetes manifests
- runtime startup scripts

Operational meaning:

The mutation may affect runtime behavior, isolation, resource use, or service availability.

---

### Infrastructure as Code

Examples:

- `terraform/*`
- `opentofu/*`
- `pulumi/*`
- cloud provisioning files
- infrastructure modules

Operational meaning:

The mutation may create, delete, expose, or reconfigure infrastructure.

---

### Secret Access

Examples:

- `.env*`
- secret configuration
- credential references
- token handling
- private key handling

Operational meaning:

The mutation may affect access to secrets or privileged credentials.

---

### Authentication / IAM

Examples:

- `auth/*`
- `iam/*`
- roles
- policies
- permissions
- session validation
- login or authorization middleware

Operational meaning:

The mutation may affect who or what is allowed to access a system.

---

### Database Migration

Examples:

- `migrations/*`
- schema changes
- destructive data operations
- persistence-layer authorization or constraints

Operational meaning:

The mutation may affect stored state, data integrity, or recoverability.

---

### Business Logic

Examples:

- domain service code
- pricing logic
- payment logic
- eligibility logic
- workflow decision code

Operational meaning:

The mutation may affect product behavior, customer outcomes, or business rules.

---

### Tests

Examples:

- test files
- test configuration
- coverage rules
- CI verification rules

Operational meaning:

The mutation may affect verification confidence.

---

### Documentation

Examples:

- `README.md`
- `docs/*`
- comments-only changes
- non-executable guides

Operational meaning:

The mutation likely has no direct runtime impact unless it changes operational instructions.

---

## 3. Initial Classification Rule

A file may map to more than one surface.

Example:

```text
.github/workflows/deploy.yml
```

MAY classify as:

- CI/CD
- Deployment Infrastructure

---

## 4. Fail-Closed Rule

If a file cannot be classified but appears executable or operationally relevant, the implementation SHOULD treat it as requiring human review.

If a file cannot be classified and the diff cannot be parsed, the trust state SHOULD become:

```text
UNEXPLAINABLE
```
