$ErrorActionPreference = "Continue"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

python scripts\evaluate_plan.py `
  --plan terraform\sample-risky-plan.json `
  --rules policies\guardrails.json `
  --output-json reports\policy-report.json `
  --output-md reports\policy-report.md

if ($LASTEXITCODE -eq 2) {
  Write-Host "Deployment gate blocked the sample plan. This is expected for the risky demo." -ForegroundColor Yellow
  exit 0
}

exit $LASTEXITCODE
