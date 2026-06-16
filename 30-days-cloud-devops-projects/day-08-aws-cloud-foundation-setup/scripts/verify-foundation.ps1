param(
  [Parameter(Mandatory = $false)]
  [string]$Profile = "default",

  [Parameter(Mandatory = $false)]
  [string]$Region = "ap-south-1",

  [Parameter(Mandatory = $true)]
  [string]$EvidenceBucket
)

$ErrorActionPreference = "Stop"

function Invoke-Aws {
  param([string[]]$Arguments)
  & aws @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "AWS CLI command failed: aws $($Arguments -join ' ')"
  }
}

Write-Host "Day 8 AWS foundation verification"
Write-Host "Profile: $Profile"
Write-Host "Region:  $Region"
Write-Host "Bucket:  $EvidenceBucket"
Write-Host ""

Write-Host "1. Caller identity"
Invoke-Aws @("sts", "get-caller-identity", "--profile", $Profile, "--region", $Region, "--output", "json")
Write-Host ""

Write-Host "2. Bucket exists"
Invoke-Aws @("s3api", "head-bucket", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region) | Out-Null
Write-Host "Bucket exists."
Write-Host ""

Write-Host "3. Public access block"
Invoke-Aws @("s3api", "get-public-access-block", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region, "--output", "json")
Write-Host ""

Write-Host "4. Default encryption"
Invoke-Aws @("s3api", "get-bucket-encryption", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region, "--output", "json")
Write-Host ""

Write-Host "5. Versioning"
Invoke-Aws @("s3api", "get-bucket-versioning", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region, "--output", "json")
Write-Host ""

Write-Host "6. Tags"
Invoke-Aws @("s3api", "get-bucket-tagging", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region, "--output", "json")
Write-Host ""

Write-Host "7. Lifecycle"
Invoke-Aws @("s3api", "get-bucket-lifecycle-configuration", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region, "--output", "json")
Write-Host ""

Write-Host "8. Uploaded Day 8 object"
Invoke-Aws @("s3", "ls", "s3://$EvidenceBucket/day8/", "--profile", $Profile, "--region", $Region)
Write-Host ""

Write-Host "Verification complete. Capture terminal output and AWS Console screenshots."
