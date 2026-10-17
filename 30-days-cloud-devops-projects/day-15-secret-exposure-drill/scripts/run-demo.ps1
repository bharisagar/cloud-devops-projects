$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Push-Location $projectRoot
try {
    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Unit tests failed' }

    python scan.py sample.env.txt --output-json reports/scan-report.json --output-md reports/scan-report.md
    if ($LASTEXITCODE -ne 1) { throw 'Expected sample risk was not detected' }
    if (-not (Test-Path -LiteralPath reports/scan-report.json) -or -not (Test-Path -LiteralPath reports/scan-report.md)) { throw 'Reports were not created' }
    $report = Get-Content -LiteralPath reports/scan-report.json -Raw | ConvertFrom-Json
    if ($report.decision -ne 'BLOCK AND TRIAGE' -or $report.findings.Count -ne 1) { throw 'Report did not contain the expected finding' }

    python scan.py sample-clean.env.txt
    if ($LASTEXITCODE -ne 0) { throw 'Clean sample should pass' }

    Write-Output 'Day 15 demo passed. Report: reports/scan-report.md'
} finally {
    Pop-Location
}
