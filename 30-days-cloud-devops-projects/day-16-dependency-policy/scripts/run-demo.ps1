$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python check.py inventory-clean.json
if ($LASTEXITCODE -ne 0) { throw "Clean inventory should pass" }
python check.py inventory.json --output-json reports/policy-report.json --output-md reports/policy-report.md
if ($LASTEXITCODE -ne 1) { throw "Risky inventory should block with exit code 1" }
$report = Get-Content reports/policy-report.json -Raw | ConvertFrom-Json
if ($report.decision -ne "BLOCK" -or $report.summary.findings -ne 4) { throw "Report verification failed" }
Write-Host "Day 16 demo passed: clean PASS, risky BLOCK, report generated."
