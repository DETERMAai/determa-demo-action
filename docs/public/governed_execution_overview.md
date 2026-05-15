# Governed Execution Overview

DETERMA governs whether AI-generated actions are allowed to mutate external systems at execution time.

Core idea:
- approval and execution are separate decisions
- approval can become stale when runtime conditions change
- legitimacy must be checked against current runtime reality

Why this matters:
- enterprise systems change continuously
- delayed execution can inherit outdated assumptions
- mutation authority must be evaluated at the boundary where mutation is applied
