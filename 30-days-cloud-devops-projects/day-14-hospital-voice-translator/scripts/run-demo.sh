#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

python3 scripts/validate_app.py --strict \
  --output-json reports/sample-validation-report.json \
  --output-md reports/sample-validation-report.md