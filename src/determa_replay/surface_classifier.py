"""Deterministic mutation surface classifier for DETERMA Replay v0.1.

The classifier maps changed file paths to operational mutation surfaces.
It is intentionally rule-based and deterministic.

No network access. No repository mutation. No LLM dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Iterable

from .diff_parser import ParsedFileChange


CI_CD = "CI/CD"
DEPLOYMENT = "Deployment Infrastructure"
RUNTIME_INFRA = "Runtime Infrastructure"
INFRA_AS_CODE = "Infrastructure as Code"
SECRET_ACCESS = "Secret Access"
AUTH_IAM = "Authentication / IAM"
DATABASE_MIGRATION = "Database Migration"
BUSINESS_LOGIC = "Business Logic"
TESTS = "Tests"
DOCUMENTATION = "Documentation"
UNKNOWN_OPERATIONAL = "Unknown Operational Surface"


@dataclass(frozen=True)
class SurfaceRule:
    surface: str
    patterns: tuple[str, ...]


SURFACE_RULES: tuple[SurfaceRule, ...] = (
    SurfaceRule(CI_CD, (
        ".github/workflows/*",
        ".gitlab-ci.yml",
        "circleci/*",
        ".circleci/*",
        "jenkins/*",
        "Jenkinsfile",
    )),
    SurfaceRule(DEPLOYMENT, (
        "deploy/*",
        "deployment/*",
        "deployments/*",
        "release/*",
        "releases/*",
        "rollout/*",
        "rollouts/*",
        "scripts/deploy*",
        ".github/workflows/deploy*",
        ".github/workflows/*deploy*",
        ".github/workflows/release*",
    )),
    SurfaceRule(RUNTIME_INFRA, (
        "Dockerfile",
        "**/Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "helm/*",
        "charts/*",
        "k8s/*",
        "kubernetes/*",
        "manifests/*",
    )),
    SurfaceRule(INFRA_AS_CODE, (
        "terraform/*",
        "infra/*",
        "infrastructure/*",
        "opentofu/*",
        "pulumi/*",
        "*.tf",
        "*.tfvars",
    )),
    SurfaceRule(SECRET_ACCESS, (
        ".env",
        ".env.*",
        "**/.env",
        "**/.env.*",
        "secrets/*",
        "secret/*",
        "credentials/*",
        "config/secrets*",
        "*secret*",
        "*credential*",
        "*private_key*",
    )),
    SurfaceRule(AUTH_IAM, (
        "auth/*",
        "authentication/*",
        "authorization/*",
        "iam/*",
        "permissions/*",
        "policies/*",
        "policy/*",
        "roles/*",
        "rbac/*",
        "middleware/auth*",
        "**/auth/*",
    )),
    SurfaceRule(DATABASE_MIGRATION, (
        "migrations/*",
        "db/migrations/*",
        "database/migrations/*",
        "schema/*",
        "*.migration.sql",
    )),
    SurfaceRule(TESTS, (
        "tests/*",
        "test/*",
        "spec/*",
        "__tests__/*",
        "*_test.py",
        "test_*.py",
        "*.test.js",
        "*.spec.js",
    )),
    SurfaceRule(DOCUMENTATION, (
        "README.md",
        "docs/*",
        "*.md",
        "*.rst",
        "*.txt",
    )),
)


OPERATIONAL_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".cs",
    ".sql",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
)


def classify_path(path: str) -> list[str]:
    """Classify a repository path into one or more mutation surfaces."""
    normalized = _normalize_path(path)
    surfaces: list[str] = []

    for rule in SURFACE_RULES:
        if any(_matches(normalized, pattern) for pattern in rule.patterns):
            surfaces.append(rule.surface)

    if not surfaces:
        if normalized.endswith(OPERATIONAL_EXTENSIONS):
            surfaces.append(BUSINESS_LOGIC)
        else:
            surfaces.append(UNKNOWN_OPERATIONAL)

    return _dedupe_preserve_order(surfaces)


def classify_changes(changes: Iterable[ParsedFileChange]) -> dict[str, list[str]]:
    """Return path -> surfaces for parsed file changes."""
    return {change.path: classify_path(change.path) for change in changes}


def aggregate_surfaces(changes: Iterable[ParsedFileChange]) -> list[str]:
    """Return all surfaces touched by a set of parsed changes."""
    surfaces: list[str] = []
    for change in changes:
        surfaces.extend(classify_path(change.path))
    return _dedupe_preserve_order(surfaces)


def _normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/").lstrip("/")


def _matches(path: str, pattern: str) -> bool:
    return fnmatch(path, pattern) or fnmatch(path.lower(), pattern.lower())


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
