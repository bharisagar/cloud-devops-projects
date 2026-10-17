#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -v
if python3 scan.py sample.env.txt --output-json reports/scan-report.json --output-md reports/scan-report.md; then
  echo "Expected sample risk was not detected" >&2
  exit 1
else
  status=$?
  if [ "$status" -ne 1 ]; then exit "$status"; fi
fi
test -s reports/scan-report.json
test -s reports/scan-report.md
python3 -c 'import json; r=json.load(open("reports/scan-report.json")); assert r["decision"] == "BLOCK AND TRIAGE" and len(r["findings"]) == 1'
python3 scan.py sample-clean.env.txt
echo "Day 15 demo passed. Report: reports/scan-report.md"
