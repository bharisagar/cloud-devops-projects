#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m unittest discover -s tests -v
python check.py inventory-clean.json
set +e
python check.py inventory.json --output-json reports/policy-report.json --output-md reports/policy-report.md
status=$?
set -e
test "$status" -eq 1
python -c 'import json; r=json.load(open("reports/policy-report.json")); assert r["decision"] == "BLOCK" and r["summary"]["findings"] == 4'
test -s reports/policy-report.md
echo "Day 16 demo passed: clean PASS, risky BLOCK, report generated."
