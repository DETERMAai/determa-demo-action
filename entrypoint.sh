#!/usr/bin/env bash
set -euo pipefail

operator_token="${OPERATOR_TOKEN:-demo-token}"
real_github="${REAL_GITHUB:-false}"
demo_repo="${DEMO_REPO:-}"
demo_branch="${DEMO_BRANCH:-determa-demo/github-action-demo}"

echo "=== DETERMA Marketplace Demo Action ==="

product_cmd=(python3 scripts/run_product_demo.py --operator-token "$operator_token")
if [[ "$real_github" == "true" || "$real_github" == "1" ]]; then
  if [[ "${DETERMA_DEMO_REAL_GITHUB:-}" != "1" ]]; then
    echo "BLOCKED: set DETERMA_DEMO_REAL_GITHUB=1 for real GitHub mode"
    exit 1
  fi
  if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "BLOCKED: missing GITHUB_TOKEN"
    exit 1
  fi
  if [[ -z "${DETERMA_DEMO_REPO:-}" ]]; then
    echo "BLOCKED: missing DETERMA_DEMO_REPO"
    exit 1
  fi
  if [[ -n "$demo_repo" ]]; then
    product_cmd+=(--repo "$demo_repo")
  else
    product_cmd+=(--repo "$DETERMA_DEMO_REPO")
  fi
  product_cmd+=(--real-github --branch "$demo_branch")
fi

echo "[1/2] Running governed product demo..."
product_output="$("${product_cmd[@]}" 2>&1)"
echo "$product_output"

echo "[2/2] Running adversarial demo..."
attack_output="$(python3 scripts/run_adversarial_demo.py 2>&1)"
echo "$attack_output"

pr_url="$(echo "$product_output" | sed -n 's/^Draft PR: //p' | tail -n 1)"
if [[ "$product_output" == *"Result: GOVERNED EXECUTION ENFORCED"* && "$attack_output" == *"ALL ATTACK PATHS BLOCKED"* ]]; then
  demo_result="PASS"
else
  demo_result="FAIL"
fi

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "demo_result=$demo_result"
    echo "pr_url=${pr_url:-}"
  } >> "$GITHUB_OUTPUT"
fi

echo "demo-result: $demo_result"
echo "pr-url: ${pr_url:-}"

if [[ "$demo_result" != "PASS" ]]; then
  exit 1
fi
