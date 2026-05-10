"""Branch workspace session model.

Captures branch-level execution context for reconstructable factory work.
No shell execution. Hashes are computed from supplied snapshots.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from factory.runtime.git_workspace import WorkspaceChangeSet


@dataclass(frozen=True)
class BranchWorkspaceSnapshot:
    """Reconstructable branch workspace snapshot."""

    base_branch: str
    working_branch: str
    change_set: WorkspaceChangeSet
    diff_snapshot: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def diff_hash(self) -> str:
        return _hash_text(self.diff_snapshot)

    @property
    def workspace_hash(self) -> str:
        payload = "\n".join(
            [
                self.base_branch,
                self.working_branch,
                *self.change_set.changed_files,
                self.diff_hash,
            ]
        )
        return _hash_text(payload)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["change_set"] = self.change_set.to_dict()
        data["diff_hash"] = self.diff_hash
        data["workspace_hash"] = self.workspace_hash
        return data


def create_branch_workspace_snapshot(
    base_branch: str,
    working_branch: str,
    change_set: WorkspaceChangeSet,
    diff_snapshot: str = "",
) -> BranchWorkspaceSnapshot:
    """Create a deterministic branch workspace snapshot."""
    return BranchWorkspaceSnapshot(
        base_branch=base_branch.strip() or "main",
        working_branch=working_branch.strip() or "factory/unknown",
        change_set=change_set,
        diff_snapshot=diff_snapshot,
    )


def _hash_text(value: str) -> str:
    normalized = value.replace("\r\n", "\n").strip() + "\n"
    return sha256(normalized.encode("utf-8")).hexdigest()
