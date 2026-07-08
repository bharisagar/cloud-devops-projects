$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

python scripts\validate_app.py --strict `
  --output-json reports\sample-validation-report.json `
  --output-md reports\sample-validation-report.md