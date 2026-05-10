"""Deterministic unified diff parser for DETERMA Replay v0.1.

Scope:
- Parse unified/git-style diffs into a stable list of changed files.
- Preserve file paths and change status.
- Count additions and deletions from hunks.

Non-goals:
- No network access.
- No GitHub API access.
- No repository mutation.
- No semantic code interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable


@dataclass(frozen=True)
class ParsedFileChange:
    """A deterministic representation of one changed file in a unified diff."""

    path: str
    old_path: str | None
    status: str
    additions: int
    deletions: int
    patch: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation with stable field order."""
        return asdict(self)


def parse_unified_diff(diff_text: str) -> list[ParsedFileChange]:
    """Parse a unified/git diff into deterministic file-change objects.

    Args:
        diff_text: Unified diff text, usually from `git diff` or GitHub PR diff.

    Returns:
        A list of ParsedFileChange objects in the same order as the diff.

    Raises:
        TypeError: if diff_text is not a string.
    """
    if not isinstance(diff_text, str):
        raise TypeError("diff_text must be a string")

    lines = diff_text.splitlines()
    files: list[ParsedFileChange] = []
    current: _MutableFileChange | None = None

    for line in lines:
        if line.startswith("diff --git "):
            if current is not None:
                files.append(current.freeze())
            current = _MutableFileChange.from_diff_header(line)
            continue

        if current is None:
            continue

        current.patch_lines.append(line)

        if line.startswith("new file mode "):
            current.status = "added"
            continue
        if line.startswith("deleted file mode "):
            current.status = "deleted"
            continue
        if line.startswith("rename from "):
            current.old_path = _strip_prefix(line.removeprefix("rename from ").strip())
            current.status = "renamed"
            continue
        if line.startswith("rename to "):
            current.path = _strip_prefix(line.removeprefix("rename to ").strip())
            current.status = "renamed"
            continue

        if _is_hunk_addition(line):
            current.additions += 1
        elif _is_hunk_deletion(line):
            current.deletions += 1

    if current is not None:
        files.append(current.freeze())

    return files


def parsed_changes_to_dicts(changes: Iterable[ParsedFileChange]) -> list[dict[str, Any]]:
    """Convert parsed changes to stable dictionaries."""
    return [change.to_dict() for change in changes]


@dataclass
class _MutableFileChange:
    path: str
    old_path: str | None
    status: str
    additions: int
    deletions: int
    patch_lines: list[str]

    @classmethod
    def from_diff_header(cls, header: str) -> "_MutableFileChange":
        # Expected format: diff --git a/path b/path
        parts = header.split()
        old_path = _strip_prefix(parts[2]) if len(parts) > 2 else None
        path = _strip_prefix(parts[3]) if len(parts) > 3 else (old_path or "")
        return cls(
            path=path,
            old_path=old_path,
            status="modified",
            additions=0,
            deletions=0,
            patch_lines=[header],
        )

    def freeze(self) -> ParsedFileChange:
        return ParsedFileChange(
            path=self.path,
            old_path=self.old_path,
            status=self.status,
            additions=self.additions,
            deletions=self.deletions,
            patch="\n".join(self.patch_lines),
        )


def _strip_prefix(path: str) -> str:
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def _is_hunk_addition(line: str) -> bool:
    return line.startswith("+") and not line.startswith("+++")


def _is_hunk_deletion(line: str) -> bool:
    return line.startswith("-") and not line.startswith("---")
