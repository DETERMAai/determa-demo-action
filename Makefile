.PHONY: demo demo-real demo-attack demo-all demo-report observe replay lineage explain

demo:
	python3 scripts/run_product_demo.py --operator-token demo-token

demo-real:
	@if [ "$$DETERMA_DEMO_REAL_GITHUB" != "1" ]; then echo "Missing DETERMA_DEMO_REAL_GITHUB=1"; exit 1; fi
	@if [ -z "$$GITHUB_TOKEN" ]; then echo "Missing GITHUB_TOKEN"; exit 1; fi
	@if [ -z "$$DETERMA_DEMO_REPO" ]; then echo "Missing DETERMA_DEMO_REPO"; exit 1; fi
	python3 scripts/run_product_demo.py --operator-token "$${OPERATOR_API_TOKEN:-demo-token}" --real-github --repo "$$DETERMA_DEMO_REPO" --branch "$${DETERMA_DEMO_BRANCH:-determa-demo/dev-demo}"

demo-attack:
	python3 scripts/run_adversarial_demo.py

demo-all:
	python3 scripts/run_product_demo.py --operator-token demo-token
	python3 scripts/run_product_demo.py --operator-token demo-token
	python3 scripts/run_adversarial_demo.py

demo-report:
	python3 scripts/run_product_demo.py --operator-token "$${OPERATOR_API_TOKEN:-demo-token}" --report-md reports/governed_pr_demo.md --report-json reports/governed_pr_demo.json

observe:
	python3 scripts/replay_viewer.py observe

replay:
	python3 scripts/replay_viewer.py replay

lineage:
	python3 scripts/replay_viewer.py lineage

explain:
	python3 scripts/replay_viewer.py explain
