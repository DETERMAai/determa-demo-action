# DETERMA Verification Failure Modes

## Replay Mismatch

Condition:

- replay hash differs from authority replay hash

Required Result:

REJECT EXECUTION

---

## Authority Mismatch

Condition:

- authority object differs from approved authority state

Required Result:

FREEZE EXECUTION

---

## Mutation Drift

Condition:

- mutation hash diverges from approved mutation

Required Result:

INVALIDATE GOVERNED RELEASE

---

## Artifact Incompleteness

Condition:

- replay artifact chain incomplete

Required Result:

BLOCK VERIFICATION

---

## Verification Ambiguity

Condition:

- legitimacy ownership cannot be reconstructed deterministically

Required Result:

FAIL CLOSED
