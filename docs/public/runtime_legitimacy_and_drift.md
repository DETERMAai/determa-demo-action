# Runtime Legitimacy and Runtime Drift

Runtime drift is ordinary infrastructure change over time, such as:
- repository state updates
- dependency graph evolution
- environment state shifts

A key execution-boundary risk appears when:
- an approval remains historically valid
- but the runtime state has changed materially

DETERMA addresses this by re-evaluating legitimacy at execution time rather than treating approval as permanently valid.
