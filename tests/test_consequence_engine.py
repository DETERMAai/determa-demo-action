from src.determa_replay.consequence_engine import generate_consequences
from src.determa_replay.surface_classifier import (
    AUTH_IAM,
    CI_CD,
    DEPLOYMENT,
    DOCUMENTATION,
    SECRET_ACCESS,
    UNKNOWN_OPERATIONAL,
)


def test_docs_consequence_is_low_impact():
    consequences = generate_consequences([DOCUMENTATION])

    assert consequences == ["No direct runtime impact detected from documentation-only paths."]


def test_ci_cd_consequences_explain_pipeline_risk():
    consequences = generate_consequences([CI_CD])

    assert "Build, test, release, or deployment behavior may change." in consequences
    assert "Verification gates may be weakened or bypassed before merge." in consequences


def test_deployment_consequences_explain_production_risk():
    consequences = generate_consequences([DEPLOYMENT])

    assert "Production rollout behavior may be altered." in consequences
    assert "Release safety controls may be reduced or bypassed." in consequences


def test_secret_consequences_explain_credential_risk():
    consequences = generate_consequences([SECRET_ACCESS])

    assert "Credential handling or secret exposure risk may change." in consequences


def test_auth_consequences_explain_access_boundary_risk():
    consequences = generate_consequences([AUTH_IAM])

    assert "Authentication, authorization, or permission behavior may change." in consequences
    assert "Access boundaries may be weakened or expanded." in consequences


def test_unknown_consequences_fail_to_human_review():
    consequences = generate_consequences([UNKNOWN_OPERATIONAL])

    assert "The operational impact could not be classified deterministically." in consequences
    assert "Human review is required before trusting this mutation." in consequences


def test_dedupes_repeated_consequences():
    consequences = generate_consequences([CI_CD, CI_CD, DEPLOYMENT])

    assert consequences.count("Build, test, release, or deployment behavior may change.") == 1
