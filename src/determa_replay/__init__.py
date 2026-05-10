"""DETERMA Replay MVP package.

v0.1 scope: deterministic replay analysis for AI-generated pull request diffs.
No execution. No repository mutation. No network access in core analyzers.
"""

__all__ = ["parse_unified_diff"]

from .diff_parser import parse_unified_diff
