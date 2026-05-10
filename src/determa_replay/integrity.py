"""Replay integrity helpers for DETERMA Replay v0.1.

Integrity answers:
- can this replay be deterministically reconstructed?
- does the replay correspond to the same diff?
- is the replay stable across executions?

No repository mutation. No execution authority.
"""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

from .replay_model import MutationReplay

INTEGRITY_VERSION = "DETERMA-INTEGRITY-V0"


def canonical_diff_hash(diff_text: str) -> str:
    """Return a deterministic SHA-256 hash for a normalized diff."""
    normalized = normalize_diff(diff_text)
    return sha256(normalized.encode("utf-8")).hexdigest()


def normalize_diff(diff_text: str) -> str:
    """Normalize diff text for deterministic hashing.

    v0.1 normalization:
    - normalize line endings
    - trim trailing whitespace
    - preserve line order
    """
    lines = [line.rstrip() for line in diff_text.replace("\r\n", "\n").split("\n")]
    return "\n".join(lines).strip() + "\n"


def replay_fingerprint(replay: MutationReplay) -> str:
    """Return a deterministic replay fingerprint."""
    payload = json.dumps(replay.to_dict(), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def build_integrity_metadata(diff_text: str, replay: MutationReplay) -> dict[str, Any]:
    """Build canonical integrity metadata for a replay artifact."""
    return {
        "integrity_version": INTEGRITY_VERSION,
        "diff_hash": canonical_diff_hash(diff_text),
        "replay_fingerprint": replay_fingerprint(replay),
        "deterministic_replay": replay.replay_integrity.is_complete(),
    }


def verify_replay_integrity(
    diff_text: str,
    replay: MutationReplay,
    expected_diff_hash: str,
    expected_replay_fingerprint: str,
) -> bool:
    """Verify replay integrity against expected hashes."""
    return (
        canonical_diff_hash(diff_text) == expected_diff_hash
        and replay_fingerprint(replay) == expected_replay_fingerprint
    )
