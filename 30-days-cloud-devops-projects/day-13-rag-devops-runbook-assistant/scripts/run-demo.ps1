$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

python scripts\runbook_assistant.py `
  --incident incidents\sample-checkout-incident.json `
  --knowledge-base knowledge-base\runbooks `
  --output-json reports\sample-rag-response.json `
  --output-md reports\sample-rag-response.md