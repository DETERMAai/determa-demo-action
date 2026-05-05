#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

def _http_json(method: str, url: str, payload: dict, headers: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, method=method, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


class LocalAuthorityError(RuntimeError):
    pass


DEMO_FILE_PATH = "demo/determa-governed-pr-demo.txt"
DEMO_COMMIT_MESSAGE = "DETERMA demo governed change"


def build_default_args() -> dict:
    return {
        "base_url": "http://localhost:8000",
        "tenant_id": "tenant_local",
        "demo_id": "default",
        "requested_by": "demo-operator",
        "report_md": "reports/governed_pr_demo.md",
        "report_json": "reports/governed_pr_demo.json",
    }


def _env_flag_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip() == "1"


def _base_url_explicit(argv: list[str]) -> bool:
    return any(arg == "--base-url" or arg.startswith("--base-url=") for arg in argv)


def _split_repo(repo: str) -> tuple[str, str]:
    parts = repo.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise LocalAuthorityError("invalid repo format, expected org/repo")
    return parts[0], parts[1]


def _github_api_url(repo: str, api_path: str, query: dict[str, str] | None = None) -> str:
    owner, name = _split_repo(repo)
    base = f"https://api.github.com/repos/{owner}/{name}{api_path}"
    if not query:
        return base
    return f"{base}?{urllib.parse.urlencode(query)}"


def _github_api_json(
    method: str,
    *,
    repo: str,
    token: str,
    api_path: str,
    payload: dict | None = None,
    query: dict[str, str] | None = None,
) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "determa-governed-demo",
    }
    return _http_json(method, _github_api_url(repo, api_path, query), payload or {}, headers)


def _local_idempotency_key(*, tenant_id: str, demo_id: str, patch_hash: str, repo: str, branch: str) -> str:
    raw = json.dumps(
        {
            "tenant_id": tenant_id,
            "demo_id": demo_id,
            "patch_hash": patch_hash,
            "repo": repo,
            "branch": branch,
            "flow": "governed_pr_local_demo",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _local_seed_state(args, *, repo: str = "mock/demo-repo", branch: str = "determa-demo/default") -> dict:
    job_id = f"demo-governed-pr-{args.demo_id}"
    binding_id = f"demo-governed-pr-binding-{args.demo_id}"
    patch_hash = "sha256:demo_patch_hash"
    idempotency_key = _local_idempotency_key(
        tenant_id=args.tenant_id,
        demo_id=args.demo_id,
        patch_hash=patch_hash,
        repo=repo,
        branch=branch,
    )
    return {
        "demo_id": args.demo_id,
        "job_id": job_id,
        "binding_id": binding_id,
        "approval_id": f"approval-{args.demo_id}",
        "capability_id": f"capability-{args.demo_id}",
        "witness_id": f"witness-{args.demo_id}",
        "release_id": f"release-{args.demo_id}",
        "patch_hash": patch_hash,
        "idempotency_key": idempotency_key,
        "approval_state": "APPROVED",
        "witness_match": True,
        "release_consumed": False,
        "pr_url": None,
        "repo": repo,
        "branch": branch,
    }


def _github_get_ref_sha(*, token: str, repo: str, branch: str) -> str:
    response = _github_api_json(
        "GET",
        repo=repo,
        token=token,
        api_path=f"/git/ref/heads/{branch}",
    )
    sha = str(((response.get("object") or {}).get("sha")) or "").strip()
    if not sha:
        raise LocalAuthorityError(f"github ref missing sha for branch {branch}")
    return sha


def _github_ensure_head_branch(*, token: str, repo: str, base_branch: str, head_branch: str) -> None:
    base_sha = _github_get_ref_sha(token=token, repo=repo, branch=base_branch)
    try:
        _github_get_ref_sha(token=token, repo=repo, branch=head_branch)
        return
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise LocalAuthorityError(f"github failed reading head branch: {_parse_error_detail(exc)}") from exc

    try:
        _github_api_json(
            "POST",
            repo=repo,
            token=token,
            api_path="/git/refs",
            payload={"ref": f"refs/heads/{head_branch}", "sha": base_sha},
        )
    except urllib.error.HTTPError as exc:
        raise LocalAuthorityError(f"github failed creating head branch: {_parse_error_detail(exc)}") from exc


def _github_upsert_demo_file(*, token: str, repo: str, head_branch: str, demo_id: str, patch_hash: str) -> None:
    content_text = (
        f"demo_id={demo_id}\n"
        f"patch_hash={patch_hash}\n"
        "marker=governed_execution_enforced\n"
    )
    payload = {
        "message": DEMO_COMMIT_MESSAGE,
        "content": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
        "branch": head_branch,
    }
    try:
        existing = _github_api_json(
            "GET",
            repo=repo,
            token=token,
            api_path=f"/contents/{DEMO_FILE_PATH}",
            query={"ref": head_branch},
        )
        existing_sha = str(existing.get("sha") or "").strip()
        if existing_sha:
            payload["sha"] = existing_sha
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise LocalAuthorityError(f"github failed reading demo file: {_parse_error_detail(exc)}") from exc

    try:
        _github_api_json(
            "PUT",
            repo=repo,
            token=token,
            api_path=f"/contents/{DEMO_FILE_PATH}",
            payload=payload,
        )
    except urllib.error.HTTPError as exc:
        raise LocalAuthorityError(f"github failed writing demo file: {_parse_error_detail(exc)}") from exc


def _github_find_existing_pr_url(*, token: str, repo: str, base_branch: str, head_branch: str) -> str | None:
    owner, _ = _split_repo(repo)
    try:
        pulls = _github_api_json(
            "GET",
            repo=repo,
            token=token,
            api_path="/pulls",
            query={
                "state": "open",
                "base": base_branch,
                "head": f"{owner}:{head_branch}",
            },
        )
    except urllib.error.HTTPError as exc:
        raise LocalAuthorityError(f"github failed listing pull requests: {_parse_error_detail(exc)}") from exc
    if not isinstance(pulls, list):
        return None
    for pull in pulls:
        pr_url = str((pull or {}).get("html_url") or "").strip()
        if pr_url:
            return pr_url
    return None


def _create_real_github_draft_pr(
    *,
    token: str,
    repo: str,
    base_branch: str,
    head_branch: str,
    demo_id: str,
    patch_hash: str,
) -> str:
    if not token:
        raise LocalAuthorityError("missing GITHUB_TOKEN")
    existing_pr = _github_find_existing_pr_url(token=token, repo=repo, base_branch=base_branch, head_branch=head_branch)
    if existing_pr:
        return existing_pr

    _github_ensure_head_branch(token=token, repo=repo, base_branch=base_branch, head_branch=head_branch)
    _github_upsert_demo_file(
        token=token,
        repo=repo,
        head_branch=head_branch,
        demo_id=demo_id,
        patch_hash=patch_hash,
    )

    payload = {
        "title": f"DETERMA governed demo ({demo_id})",
        "head": head_branch,
        "base": base_branch,
        "body": "Governed product demo Draft PR (sandbox mode).",
        "draft": True,
    }
    try:
        response = _github_api_json("POST", repo=repo, token=token, api_path="/pulls", payload=payload)
    except urllib.error.HTTPError as exc:
        raise LocalAuthorityError(f"github draft pr creation failed: {_parse_error_detail(exc)}") from exc

    pr_url = str(response.get("html_url") or "").strip()
    if not pr_url:
        raise LocalAuthorityError("github response missing html_url")
    return pr_url


def _resolve_real_github_config(args) -> dict:
    if not _env_flag_enabled("DETERMA_DEMO_REAL_GITHUB"):
        raise LocalAuthorityError("DETERMA_DEMO_REAL_GITHUB=1 is required for --real-github")
    token = str(os.environ.get("GITHUB_TOKEN") or "").strip()
    if not token:
        raise LocalAuthorityError("GITHUB_TOKEN is required for --real-github")
    env_repo = str(os.environ.get("DETERMA_DEMO_REPO") or "").strip()
    if not env_repo:
        raise LocalAuthorityError("DETERMA_DEMO_REPO is required for --real-github")

    requested_repo = str(args.repo or "").strip()
    effective_repo = requested_repo or env_repo
    if not effective_repo:
        raise LocalAuthorityError("repo is required (use --repo or DETERMA_DEMO_REPO)")
    if effective_repo != env_repo:
        raise LocalAuthorityError("repo mismatch: requested repo is outside sandbox")

    base_branch = str(os.environ.get("DETERMA_DEMO_BASE_BRANCH") or "main").strip() or "main"
    head_branch = str(args.branch or f"determa-demo/{args.demo_id}").strip()
    if not re.fullmatch(r"determa-demo/[A-Za-z0-9._/-]+", head_branch):
        raise LocalAuthorityError("branch blocked: must match determa-demo/*")
    if head_branch in {"main", "master"} or head_branch.startswith("release/"):
        raise LocalAuthorityError("branch blocked: protected branch not allowed")
    if head_branch == base_branch:
        raise LocalAuthorityError("branch blocked: head branch must differ from base branch")

    return {
        "token": token,
        "repo": effective_repo,
        "base_branch": base_branch,
        "head_branch": head_branch,
    }


def _local_execute(seed_state: dict, *, break_witness: bool = False, real_github_config: dict | None = None) -> dict:
    if seed_state.get("approval_state") != "APPROVED":
        raise LocalAuthorityError("approval missing")
    if break_witness or not seed_state.get("witness_match", False):
        raise LocalAuthorityError("state witness mismatch")
    if not seed_state.get("capability_id"):
        raise LocalAuthorityError("capability missing")
    if not seed_state.get("release_id"):
        raise LocalAuthorityError("execution release missing")

    if seed_state.get("pr_url"):
        return {
            "ok": True,
            "data": {
                "job_id": seed_state["job_id"],
                "approval_id": seed_state["approval_id"],
                "capability_id": seed_state["capability_id"],
                "witness_id": seed_state["witness_id"],
                "release_id": seed_state["release_id"],
                "github_pr_url": seed_state["pr_url"],
                "audit_linkage": {
                    "binding_id": seed_state["binding_id"],
                    "idempotency_key": seed_state["idempotency_key"],
                    "replay_detected": True,
                },
            },
        }

    if seed_state.get("release_consumed"):
        raise LocalAuthorityError("execution release already consumed")
    seed_state["release_consumed"] = True
    if real_github_config is None:
        seed_state["pr_url"] = f"mock://github/{seed_state['job_id']}/{seed_state['idempotency_key'][:12]}"
    else:
        seed_state["pr_url"] = _create_real_github_draft_pr(
            token=real_github_config["token"],
            repo=real_github_config["repo"],
            base_branch=real_github_config["base_branch"],
            head_branch=real_github_config["head_branch"],
            demo_id=seed_state["demo_id"],
            patch_hash=seed_state["patch_hash"],
        )
    return {
        "ok": True,
        "data": {
            "job_id": seed_state["job_id"],
            "approval_id": seed_state["approval_id"],
            "capability_id": seed_state["capability_id"],
            "witness_id": seed_state["witness_id"],
            "release_id": seed_state["release_id"],
            "github_pr_url": seed_state["pr_url"],
            "audit_linkage": {
                "binding_id": seed_state["binding_id"],
                "idempotency_key": seed_state["idempotency_key"],
                "replay_detected": False,
            },
        },
    }


def _safe_get(data: dict, path: list, default=None):
    node = data
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


def _build_report_payload(*, demo_id: str, seed: dict, run1: dict, run2: dict, real_github: bool) -> dict:
    seed_data = seed.get("data") or {}
    run1_data = run1.get("data") or {}
    run2_data = run2.get("data") or {}
    run1_replay = bool(_safe_get(run1_data, ["audit_linkage", "replay_detected"], False))
    run2_replay = bool(_safe_get(run2_data, ["audit_linkage", "replay_detected"], False))
    return {
        "demo_id": demo_id,
        "job_id": run2_data.get("job_id"),
        "approval_id": run2_data.get("approval_id"),
        "capability_id": run2_data.get("capability_id"),
        "witness_id": run2_data.get("witness_id"),
        "release_id": run2_data.get("release_id"),
        "binding_id": _safe_get(run2_data, ["audit_linkage", "binding_id"], seed_data.get("binding_id")),
        "patch_hash": seed_data.get("patch_sha256"),
        "idempotency_key": _safe_get(run2_data, ["audit_linkage", "idempotency_key"]),
        "first_run_pr_url": run1_data.get("github_pr_url"),
        "second_run_pr_url": run2_data.get("github_pr_url"),
        "mock_pr_url": run2_data.get("github_pr_url") if (not real_github) else None,
        "replay_detected": run2_replay,
        "adapter_called_first_run": not run1_replay,
        "adapter_called_second_run": not run2_replay,
        "authority_chain_status": "PASSED" if run2.get("ok") else "FAILED",
        "fail_closed_summary": {
            "missing_approval": "blocked",
            "missing_witness": "blocked",
            "missing_release": "blocked",
            "expired_or_invalid_authority": "blocked",
        },
    }


def _render_markdown_report(report: dict) -> str:
    lines = [
        "# Governed PR Demo Evidence Report",
        "",
        "## Executive Summary",
        f"- demo_id: `{report['demo_id']}`",
        f"- authority_chain_status: `{report['authority_chain_status']}`",
        f"- replay_detected: `{report['replay_detected']}`",
        "",
        "## Authority Chain",
        f"- job_id: `{report['job_id']}`",
        f"- approval_id: `{report['approval_id']}`",
        f"- capability_id: `{report['capability_id']}`",
        f"- witness_id: `{report['witness_id']}`",
        f"- release_id: `{report['release_id']}`",
        f"- binding_id: `{report['binding_id']}`",
        "",
        "## Execution Envelope",
        f"- patch_hash: `{report['patch_hash']}`",
        f"- idempotency_key: `{report['idempotency_key']}`",
        "",
        "## Demo Result",
        f"- first_run_pr_url: `{report['first_run_pr_url']}`",
        f"- second_run_pr_url: `{report['second_run_pr_url']}`",
        f"- replay_detected: `{report['replay_detected']}`",
    ]
    return "\n".join(lines) + "\n"


def _write_report(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _write_reports(args, seed: dict, run1: dict, run2: dict, *, real_github: bool) -> None:
    report = _build_report_payload(
        demo_id=args.demo_id,
        seed=seed,
        run1=run1,
        run2=run2,
        real_github=real_github,
    )
    if args.report_json:
        _write_report(args.report_json, json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.report_md:
        _write_report(args.report_md, _render_markdown_report(report))


def _parse_error_detail(exc: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(exc.read().decode("utf-8", errors="replace"))
        return str(payload.get("detail") or payload)
    except Exception:
        return "request failed"


def _success_output(run1: dict, run2: dict, patch_name: str) -> str:
    run1_data = run1.get("data") or {}
    run2_data = run2.get("data") or {}
    replay = bool(((run2_data.get("audit_linkage") or {}).get("replay_detected")))
    same_pr = run1_data.get("github_pr_url") == run2_data.get("github_pr_url")
    duplicate_none = replay and same_pr
    lines = [
        "=== DETERMA Governed PR Demo ===",
        "",
        f"AI Change: {patch_name}",
        "Approval: ✅ APPROVED",
        "Capability: ✅ ISSUED",
        "State Witness: ✅ MATCHED",
        "Execution Release: ✅ CONSUMED",
        "",
        f"Draft PR: {run2_data.get('github_pr_url')}",
        "",
        f"Replay Attempt: {'BLOCKED' if replay else 'FAILED'}",
        f"Duplicate Execution: {'❌ NONE' if duplicate_none else '⚠️ POSSIBLE'}",
        "",
        f"Result: {'GOVERNED EXECUTION ENFORCED' if duplicate_none else 'FAIL-CLOSED'}",
    ]
    return "\n".join(lines)


def _fail_closed_output(reason: str = "state witness mismatch") -> str:
    return "\n".join(
        [
            "=== DETERMA Governed PR Demo ===",
            "",
            "State Witness: ❌ MISMATCH",
            f"Execution: BLOCKED ({reason})",
            "Result: FAIL-CLOSED",
        ]
    )


def run_demo(args, operator_token: str) -> int:
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-Id": args.tenant_id,
        "X-Operator-Token": operator_token,
    }
    seed_payload = {
        "demo_id": args.demo_id,
        "requested_by": args.requested_by,
        "base_branch": "main",
    }
    execute_payload = {
        "binding_id": f"demo-governed-pr-binding-{args.demo_id}",
        "requested_by": args.requested_by,
        "mock_mode": True,
    }

    try:
        seed = _http_json("POST", f"{args.base_url}/v1/demo/governed-pr/seed", seed_payload, headers)
        job_id = (seed.get("data") or {}).get("job_id")
        if not job_id:
            print("FAIL: missing job_id from seed response")
            return 1

        if args.break_witness:
            broken_payload = dict(execute_payload)
            broken_payload["head_branch"] = f"mismatch/{args.demo_id}"
            try:
                _http_json("POST", f"{args.base_url}/v1/jobs/{job_id}/execute-governed-pr", broken_payload, headers)
                print("FAIL: break-witness expected fail-closed block but execution succeeded")
                return 1
            except urllib.error.HTTPError as exc:
                detail = _parse_error_detail(exc)
                if "witness" not in detail.lower():
                    print(f"FAIL: unexpected break-witness error detail: {detail}")
                    return 1
                print(_fail_closed_output())
                return 0

        run1 = _http_json("POST", f"{args.base_url}/v1/jobs/{job_id}/execute-governed-pr", execute_payload, headers)
        run2 = _http_json("POST", f"{args.base_url}/v1/jobs/{job_id}/execute-governed-pr", execute_payload, headers)
    except urllib.error.HTTPError as exc:
        print(f"FAIL: demo call failed: {_parse_error_detail(exc)}")
        return 1
    except urllib.error.URLError as exc:
        print(f"FAIL: request failed: {exc.reason}")
        return 1

    _write_reports(args, seed, run1, run2, real_github=False)
    print(_success_output(run1, run2, "demo_patch.diff"))
    return 0


def run_local_demo(args, operator_token: str) -> int:
    _ = operator_token
    real_github_config = None
    if args.real_github:
        try:
            real_github_config = _resolve_real_github_config(args)
        except LocalAuthorityError as exc:
            print(f"Execution: BLOCKED ({exc})")
            return 1

    repo = (real_github_config or {}).get("repo", "mock/demo-repo")
    branch = (real_github_config or {}).get("head_branch", f"determa-demo/{args.demo_id}")
    seed_state = _local_seed_state(args, repo=repo, branch=branch)
    seed = {
        "ok": True,
        "data": {
            "job_id": seed_state["job_id"],
            "binding_id": seed_state["binding_id"],
            "patch_sha256": seed_state["patch_hash"],
        },
    }
    try:
        if args.break_witness:
            _local_execute(seed_state, break_witness=True, real_github_config=real_github_config)
            print("FAIL: break-witness expected fail-closed block but execution succeeded")
            return 1
        run1 = _local_execute(seed_state, real_github_config=real_github_config)
        run2 = _local_execute(seed_state, real_github_config=real_github_config)
    except LocalAuthorityError as exc:
        detail = str(exc)
        if args.break_witness and "witness" in detail.lower():
            print(_fail_closed_output(detail))
            return 0
        print(f"Execution: BLOCKED ({detail})")
        return 1

    _write_reports(args, seed, run1, run2, real_github=bool(real_github_config))
    print(_success_output(run1, run2, "demo_patch.diff"))
    return 0


def main() -> int:
    defaults = build_default_args()
    raw_argv = list(sys.argv[1:])
    parser = argparse.ArgumentParser(description="Run 30-second governed PR product demo.")
    parser.add_argument("--base-url", default=defaults["base_url"])
    parser.add_argument("--tenant-id", default=defaults["tenant_id"])
    parser.add_argument("--demo-id", default=defaults["demo_id"])
    parser.add_argument("--requested-by", default=defaults["requested_by"])
    parser.add_argument("--operator-token", default=os.environ.get("OPERATOR_API_TOKEN", ""))
    parser.add_argument("--report-md", default=defaults["report_md"])
    parser.add_argument("--report-json", default=defaults["report_json"])
    parser.add_argument("--local-demo", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--real-github", action="store_true")
    parser.add_argument("--repo", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--break-witness", action="store_true")
    args = parser.parse_args()

    if not args.operator_token:
        print("FAIL: operator token missing. Provide --operator-token or OPERATOR_API_TOKEN.")
        return 2

    Path(args.report_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
    use_http_mode = (not args.local_demo) or _base_url_explicit(raw_argv)
    if use_http_mode:
        return run_demo(args, args.operator_token)
    return run_local_demo(args, args.operator_token)


if __name__ == "__main__":
    raise SystemExit(main())
