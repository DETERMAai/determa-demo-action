# Banned Runtime Surfaces

The replay kernel must remain deterministic.

The following runtime surfaces are forbidden inside the replay path:

- Date.now()
- new Date()
- Math.random()
- process.env access
- locale-dependent formatting
- floating point arithmetic
- filesystem metadata
- network access
- non-canonical JSON serialization

Replay functions must remain pure:

pure(input) -> output

No hidden state.
No ambient runtime dependence.
