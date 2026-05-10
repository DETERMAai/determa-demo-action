from src.determa_replay.integrity import (
    INTEGRITY_VERSION,
    build_integrity_metadata,
    canonical_diff_hash,
    normalize_diff,
    replay_fingerprint,
    verify_replay_integrity,
)
from src.determa_replay.replay_model import MutationReplay, ReplayIntegrity


SAMPLE_DIFF = """diff --git a/app.py b/app.py
index 1111111..2222222 100644
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-x = 1
+x = 2
"""


def _sample_replay() -> MutationReplay:
    return MutationReplay(
        replay_id="REPLAY-test123",
        severity="MEDIUM",
        trust_state="REQUIRES_APPROVAL",
        mutation_surfaces=["Business Logic"],
        human_summary="Business logic changed.",
        what_changed=["modified: app.py (+1/-1)"],
        potential_consequences=["Product behavior or business rules may change."],
        replay_timeline=[
            "Diff received",
            "Files classified",
            "Risk evaluated",
            "Trust state determined",
        ],
        replay_integrity=ReplayIntegrity(
            diff_parsed=True,
            mutation_surface_classified=True,
            deterministic_replay_generated=True,
        ),
        recommended_action="Human approval required before merge.",
    )


def test_normalize_diff_is_stable():
    normalized = normalize_diff(SAMPLE_DIFF)

    assert normalized.endswith("\n")
    assert "\r" not in normalized


def test_canonical_diff_hash_is_deterministic():
    first = canonical_diff_hash(SAMPLE_DIFF)
    second = canonical_diff_hash(SAMPLE_DIFF)

    assert first == second
    assert len(first) == 64


def test_replay_fingerprint_is_deterministic():
    replay = _sample_replay()

    first = replay_fingerprint(replay)
    second = replay_fingerprint(replay)

    assert first == second
    assert len(first) == 64


def test_build_integrity_metadata_contains_required_fields():
    replay = _sample_replay()

    metadata = build_integrity_metadata(SAMPLE_DIFF, replay)

    assert metadata["integrity_version"] == INTEGRITY_VERSION
    assert "diff_hash" in metadata
    assert "replay_fingerprint" in metadata
    assert metadata["deterministic_replay"] is True


def test_verify_replay_integrity_success():
    replay = _sample_replay()

    diff_hash = canonical_diff_hash(SAMPLE_DIFF)
    fingerprint = replay_fingerprint(replay)

    assert verify_replay_integrity(
        SAMPLE_DIFF,
        replay,
        expected_diff_hash=diff_hash,
        expected_replay_fingerprint=fingerprint,
    ) is True


def test_verify_replay_integrity_failure():
    replay = _sample_replay()

    assert verify_replay_integrity(
        SAMPLE_DIFF,
        replay,
        expected_diff_hash="invalid",
        expected_replay_fingerprint="invalid",
    ) is False
