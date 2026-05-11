# SPEC_02 — Runtime Contract

Status: Frozen Draft v1

## Canonical Function

```python
canonicalize(
    rtc,
    capability,
    replay_state
)
```

## Inputs

### RTC

```python
RTC {
    rtc_id: bytes32
    mutation_type: enum
    payload_hash: bytes32
    epoch: uint64
}
```

### Capability

```python
Capability {
    capability_id: bytes32
    rtc_hash: bytes32
    lineage_head: bytes32
    epoch: uint64
}
```

### ReplayState

```python
ReplayState {
    lineage_head: bytes32
    finalized_hashes: list[bytes32]
}
```

## Outputs

### CANONICAL

```json
{
  "admissibility": "CANONICAL",
  "finality": "COMMITTED",
  "replay_hash": "..."
}
```

### NON_CANONICAL

```json
{
  "admissibility": "NON_CANONICAL",
  "reason_code": "...",
  "replay_hash": "..."
}
```

## Invariants

1. Same inputs -> same replay hash.
2. No irreversible merge outside canonicalize().
3. Finalized lineage immutable.
4. Replay verification must remain tractable.
