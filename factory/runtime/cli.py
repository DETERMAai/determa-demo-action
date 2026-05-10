"""Factory runtime CLI.

Small CLI for reading runtime history, timeline, and metrics.
No worker execution in this first version.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from factory.runtime.metrics import compute_runtime_metrics, render_runtime_metrics
from factory.runtime.persistence import RuntimeStore
from factory.runtime.timeline import render_runtime_timeline

DEFAULT_HISTORY_PATH = Path("factory/runtime/history/runtime_events.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DETERMA Factory Runtime CLI")
    parser.add_argument(
        "command",
        choices=("timeline", "metrics"),
        help="Command to run",
    )
    parser.add_argument(
        "--history",
        default=str(DEFAULT_HISTORY_PATH),
        help="Path to runtime history JSON",
    )

    args = parser.parse_args(argv)
    store = RuntimeStore(Path(args.history))
    events = store.load()

    if args.command == "timeline":
        print(render_runtime_timeline(events), end="")
        return 0

    if args.command == "metrics":
        metrics = compute_runtime_metrics(events)
        print(render_runtime_metrics(metrics), end="")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
