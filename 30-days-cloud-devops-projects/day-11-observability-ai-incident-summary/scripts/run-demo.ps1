$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

python scripts\generate_telemetry.py
python scripts\analyze_incident.py `
  --logs telemetry\sample-logs.jsonl `
  --metrics telemetry\sample-metrics.jsonl `
  --traces telemetry\sample-traces.json `
  --output-json reports\sample-incident-summary.json `
  --output-md reports\sample-incident-summary.md