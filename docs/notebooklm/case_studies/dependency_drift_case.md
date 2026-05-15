# Dependency Drift Case

A mutation is approved when dependency graph `D44C` is active. Execution occurs when graph `E11X` is active.

The action specification is unchanged. The runtime substrate is not.

Why historical approval fails:
- dependency-linked behavior assumptions no longer match

How legitimacy changes:
- mutation trust decays with dependency evolution
- execution authority requires current-state alignment
