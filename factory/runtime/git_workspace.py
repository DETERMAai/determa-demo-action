"""Git workspace adapter for the Factory Runtime.

This module normalizes changed-file inputs from a Git workspace.
It intentionally does not execute shell commands in v0.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class WorkspaceChangeSet:
    """Normalized changed file set for runtime verification."""

    changed_files: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {"changed_files": list(self.changed_files)}


def build_change_set(paths: Iterable[str]) -> WorkspaceChangeSet:
    """Build a deterministic changed-file set from raw path strings."""
    normalized = sorted({_normalize_path(path) for path in paths if _normalize_path(path)})
    return WorkspaceChangeSet(changed_files=tuple(normalized))


def build_change_set_from_file(path: Path) -> WorkspaceChangeSet:
    """Load newline-delimited changed files from a file.

    This lets CI or a future Git adapter provide changed files without letting
    the runtime execute arbitrary shell commands.
    """
    if not path.exists():
        return WorkspaceChangeSet(changed_files=())

    return build_change_set(path.read_text(encoding="utf-8").splitlines())


def _normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/").lstrip("/")
