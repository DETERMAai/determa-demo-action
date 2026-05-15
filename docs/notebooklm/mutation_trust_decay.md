# Mutation Trust Decay

Trust in a mutation decays as runtime reality changes.

A mutation can be well-formed, policy-consistent, and initially approved, yet become less trustworthy over time due to environmental movement.

## Drivers of Trust Decay

- environment drift
- dependency mutation
- delayed execution windows
- replay mismatch
- capability state changes
- broader system state divergence

## Mutation Trust Decay Curve (Conceptual)

At approval time, trust is highest because decision context and runtime context are aligned.

As time and system change accumulate, trust decreases. The rate is shaped by:
- speed of runtime evolution
- sensitivity of the mutation surface
- duration between approval and execution

The curve is conceptual, but the consequence is operational: stale trust should not be treated as current legitimacy.

## Implication

Authorization continuity without runtime continuity produces decayed trust. Legitimate execution requires revalidation against present state.
