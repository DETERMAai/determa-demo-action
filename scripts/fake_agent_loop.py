#!/usr/bin/env python3
from __future__ import annotations

import subprocess


def build_attempts() -> list[dict]:
    return [
        {
            "label": "Valid Governed Change",
            "command": ("make", "demo"),
            "expected_status": "ALLOWED",
        },
        {
            "label": "Replay Same Change",
            "command": ("make", "demo"),
            "expected_status": "BLOCKED",
        },
        {
            "label": "Adversarial Bypass Attempts",
            "command": ("make", "demo-attack"),
            "expected_status": "BLOCKED",
        },
        {
            "label": "State Witness Tampering",
            "command": ("python3", "scripts/run_product_demo.py", "--operator-token", "demo-token", "--break-witness"),
            "expected_status": "BLOCKED",
        },
    ]


def _execute(command: tuple[str, ...]) -> tuple[int, str]:
    try:
        proc = subprocess.run(command, check=False, capture_output=True, text=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, output
    except FileNotFoundError as exc:
        return 127, str(exc)


def _classify(spec: dict, returncode: int, output: str) -> str:
    label = spec["label"]
    if label == "Valid Governed Change":
        if returncode == 0 and "Result: GOVERNED EXECUTION ENFORCED" in output:
            return "ALLOWED"
        return "FAILED"
    if label == "Replay Same Change":
        if returncode == 0 and "Replay Attempt: BLOCKED" in output:
            return "BLOCKED"
        return "FAILED"
    if label == "Adversarial Bypass Attempts":
        if returncode == 0 and "ALL ATTACK PATHS BLOCKED" in output:
            return "BLOCKED"
        return "FAILED"
    if label == "State Witness Tampering":
        if returncode == 0 and "Result: FAIL-CLOSED" in output:
            return "BLOCKED"
        return "FAILED"
    return "FAILED"


def run_simulation() -> tuple[list[dict], bool]:
    results: list[dict] = []
    for spec in build_attempts():
        rc, out = _execute(spec["command"])
        status = _classify(spec, rc, out)
        results.append(
            {
                "label": spec["label"],
                "command": spec["command"],
                "status": status,
                "returncode": rc,
                "output": out,
            }
        )
    contained = all(result["status"] == spec["expected_status"] for result, spec in zip(results, build_attempts()))
    return results, contained


def render_output(results: list[dict], contained: bool) -> str:
    lines = ["=== DETERMA Controlled Agent Simulation ===", ""]
    for idx, item in enumerate(results, start=1):
        lines.append(f"Agent Attempt {idx}: {item['label']} -> {item['status']}")
    lines.append("")
    lines.append("Result: AGENT CONTAINED BY DETERMA" if contained else "Result: CONTAINMENT FAILED")
    return "\n".join(lines)


def main() -> int:
    results, contained = run_simulation()
    print(render_output(results, contained))
    return 0 if contained else 1


if __name__ == "__main__":
    raise SystemExit(main())
