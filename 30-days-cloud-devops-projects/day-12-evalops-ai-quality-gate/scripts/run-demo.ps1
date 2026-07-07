$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

python scripts\evaluate_summary.py `
  --summary summaries\sample-generated-incident-summary.json `
  --golden evals\golden-incidents.json `
  --output-json reports\sample-eval-report.json `
  --output-md reports\sample-eval-report.md