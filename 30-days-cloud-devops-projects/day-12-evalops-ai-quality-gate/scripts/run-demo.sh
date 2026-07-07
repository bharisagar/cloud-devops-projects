#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

python3 scripts/evaluate_summary.py \
  --summary summaries/sample-generated-incident-summary.json \
  --golden evals/golden-incidents.json \
  --output-json reports/sample-eval-report.json \
  --output-md reports/sample-eval-report.md