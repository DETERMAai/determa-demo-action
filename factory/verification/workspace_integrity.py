"""Workspace integrity verification.

Detects drift between expected and current branch workspace snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass

from factory.runtime.branch_workspace import BranchWorkspaceSnapshot


@dataclass(frozen=True)
class WorkspaceIntegrityResult:
    passed: bool
    reasons: tuple[str, ...]


def verify_workspace_integrity(
    expected: BranchWorkspaceSnapshot,
    current: BranchWorkspaceSnapshot,
) -> WorkspaceIntegrityResult:
    """Verify that the current workspace snapshot matches the expected snapshot."""
    reasons: list[str] = []

    if expected.base_branch != current.base_branch:
        reasons.append(
            f"base branch mismatch: expected {expected.base_branch}, got {current.base_branch}"
        )

    if expected.working_branch != current.working_branch:
        reasons.append(
            f"working branch mismatch: expected {expected.working_branch}, got {current.working_branch}"
        )

    if expected.change_set.changed_files != current.change_set.changed_files:
        reasons.append("changed files mismatch")

    if expected.diff_hash != current.diff_hash:
        reasons.append("diff hash mismatch")

    if expected.workspace_hash != current.workspace_hash:
        reasons.append("workspace hash mismatch")

    return WorkspaceIntegrityResult(
        passed=not reasons,
        reasons=tuple(reasons) if reasons else ("workspace integrity verified",),
    )
