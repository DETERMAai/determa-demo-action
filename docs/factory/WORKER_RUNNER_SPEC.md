# Worker Runner Specification

Purpose:

Execute bounded factory tasks safely and automatically.

---

## Responsibilities

The Worker Runner must:

1. receive a task contract
2. create an isolated branch
3. modify only allowed files
4. execute required tests
5. generate replay verification
6. create a pull request

---

## Execution Flow

```text
Task Contract
→ Branch Creation
→ Scoped Execution
→ Tests
→ Replay Verification
→ PR Creation
```

---

## Required Inputs

```yaml
task_id:
allowed_files:
forbidden_files:
acceptance_criteria:
tests_required:
```

---

## Hard Constraints

The runner must NOT:

- edit forbidden files
- bypass failing tests
- modify unrelated files
- expand task scope
- add dependencies without approval

---

## Branch Naming

```text
factory/<task-id>-<task-name>
```

Example:

```text
factory/pr-47-t1-add-noise-filter
```

---

## PR Requirements

Every PR must include:

- task id
- replay summary
- changed files summary
- test results
- rollback safety

---

## Replay Verification

Before PR creation:

1. run DETERMA Replay
2. detect risky mutations
3. validate scope boundaries
4. validate replay stability

---

## Failure Handling

If:

- tests fail
- scope expands
- replay detects unsafe mutation

Then:

```text
STOP EXECUTION
```

and mark task as BLOCKED.

---

## Factory Principle

Worker autonomy is allowed only inside:

```text
strict bounded execution
```

Not:

```text
open-ended autonomous development
```
