#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

python3 scripts/runbook_assistant.py \
  --incident incidents/sample-checkout-incident.json \
  --knowledge-base knowledge-base/runbooks \
  --output-json reports/sample-rag-response.json \
  --output-md reports/sample-rag-response.md