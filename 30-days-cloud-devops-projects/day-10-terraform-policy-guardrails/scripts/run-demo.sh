#!/usr/bin/env bash
set +e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

python3 scripts/evaluate_plan.py \
  --plan terraform/sample-risky-plan.json \
  --rules policies/guardrails.json \
  --output-json reports/policy-report.json \
  --output-md reports/policy-report.md

status=$?
if [ "$status" -eq 2 ]; then
  echo "Deployment gate blocked the sample plan. This is expected for the risky demo."
  exit 0
fi

exit "$status"
