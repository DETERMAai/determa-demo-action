from src.determa_replay.diff_parser import ParsedFileChange
from src.determa_replay.surface_classifier import (
    AUTH_IAM,
    BUSINESS_LOGIC,
    CI_CD,
    DATABASE_MIGRATION,
    DEPLOYMENT,
    DOCUMENTATION,
    INFRA_AS_CODE,
    RUNTIME_INFRA,
    SECRET_ACCESS,
    TESTS,
    UNKNOWN_OPERATIONAL,
    aggregate_surfaces,
    classify_changes,
    classify_path,
)


def _change(path: str) -> ParsedFileChange:
    return ParsedFileChange(
        path=path,
        old_path=path,
        status="modified",
        additions=1,
        deletions=1,
        patch="",
    )


def test_classifies_github_workflow_as_ci_cd():
    assert CI_CD in classify_path(".github/workflows/test.yml")


def test_classifies_deploy_workflow_as_ci_cd_and_deployment():
    surfaces = classify_path(".github/workflows/deploy.yml")

    assert CI_CD in surfaces
    assert DEPLOYMENT in surfaces


def test_classifies_dockerfile_as_runtime_infrastructure():
    assert classify_path("Dockerfile") == [RUNTIME_INFRA]


def test_classifies_terraform_as_infrastructure_as_code():
    assert INFRA_AS_CODE in classify_path("terraform/main.tf")


def test_classifies_secret_paths():
    assert SECRET_ACCESS in classify_path("config/secrets.yml")
    assert SECRET_ACCESS in classify_path(".env.production")


def test_classifies_auth_paths():
    assert AUTH_IAM in classify_path("auth/middleware.py")
    assert AUTH_IAM in classify_path("iam/roles.yml")


def test_classifies_database_migrations():
    assert DATABASE_MIGRATION in classify_path("db/migrations/001_create_users.sql")


def test_classifies_tests():
    assert TESTS in classify_path("tests/test_api.py")
    assert TESTS in classify_path("service.test.js")


def test_classifies_docs():
    assert classify_path("README.md") == [DOCUMENTATION]
    assert DOCUMENTATION in classify_path("docs/guide.md")


def test_defaults_code_to_business_logic():
    assert classify_path("src/payments/service.py") == [BUSINESS_LOGIC]


def test_unknown_non_code_surface_fails_to_unknown_operational():
    assert classify_path("unknown.binary") == [UNKNOWN_OPERATIONAL]


def test_classify_changes_returns_path_map():
    changes = [_change("README.md"), _change("auth/login.py")]

    result = classify_changes(changes)

    assert result["README.md"] == [DOCUMENTATION]
    assert AUTH_IAM in result["auth/login.py"]


def test_aggregate_surfaces_dedupes_and_preserves_order():
    changes = [
        _change(".github/workflows/deploy.yml"),
        _change("Dockerfile"),
        _change("README.md"),
    ]

    result = aggregate_surfaces(changes)

    assert result == [CI_CD, DEPLOYMENT, RUNTIME_INFRA, DOCUMENTATION]
