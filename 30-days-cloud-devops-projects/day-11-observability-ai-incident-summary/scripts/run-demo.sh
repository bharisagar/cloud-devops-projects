#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

python3 scripts/generate_telemetry.py
python3 scripts/analyze_incident.py \
  --logs telemetry/sample-logs.jsonl \
  --metrics telemetry/sample-metrics.jsonl \
  --traces telemetry/sample-traces.json \
  --output-json reports/sample-incident-summary.json \
  --output-md reports/sample-incident-summary.md