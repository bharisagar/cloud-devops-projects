param(
  [Parameter(Mandatory = $false)]
  [string]$Profile = "default",

  [Parameter(Mandatory = $false)]
  [string]$Region = "ap-south-1",

  [Parameter(Mandatory = $false)]
  [string]$EvidenceBucket = "",

  [Parameter(Mandatory = $false)]
  [int]$MonthlyBudgetUsd = 5,

  [Parameter(Mandatory = $false)]
  [string]$AlertEmail = ""
)

$ErrorActionPreference = "Stop"

function Invoke-Aws {
  param([string[]]$Arguments)
  & aws @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "AWS CLI command failed: aws $($Arguments -join ' ')"
  }
}

Write-Host "Day 8 AWS foundation bootstrap"
Write-Host "Profile: $Profile"
Write-Host "Region:  $Region"

$identityJson = Invoke-Aws @("sts", "get-caller-identity", "--profile", $Profile, "--region", $Region, "--output", "json")
$identity = $identityJson | ConvertFrom-Json
$accountId = $identity.Account

Write-Host "Verified AWS identity:"
Write-Host "Account: $($identity.Account)"
Write-Host "Arn:     $($identity.Arn)"

if ([string]::IsNullOrWhiteSpace($EvidenceBucket)) {
  $EvidenceBucket = "barisagar-cloud-devops-evidence-$accountId-$Region".ToLower()
}

Write-Host "Evidence bucket: $EvidenceBucket"

$bucketExists = $false
try {
  Invoke-Aws @("s3api", "head-bucket", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region) | Out-Null
  $bucketExists = $true
  Write-Host "Bucket already exists. Continuing with hardening."
} catch {
  Write-Host "Bucket does not exist. Creating bucket."
}

if (-not $bucketExists) {
  if ($Region -eq "us-east-1") {
    Invoke-Aws @("s3api", "create-bucket", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region) | Out-Null
  } else {
    Invoke-Aws @(
      "s3api", "create-bucket",
      "--bucket", $EvidenceBucket,
      "--create-bucket-configuration", "LocationConstraint=$Region",
      "--profile", $Profile,
      "--region", $Region
    ) | Out-Null
  }
}

Invoke-Aws @("s3api", "wait", "bucket-exists", "--bucket", $EvidenceBucket, "--profile", $Profile, "--region", $Region) | Out-Null

Write-Host "Blocking public access."
Invoke-Aws @(
  "s3api", "put-public-access-block",
  "--bucket", $EvidenceBucket,
  "--public-access-block-configuration", "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true",
  "--profile", $Profile,
  "--region", $Region
) | Out-Null

Write-Host "Enabling default encryption."
$encryptionConfig = @{
  Rules = @(
    @{
      ApplyServerSideEncryptionByDefault = @{
        SSEAlgorithm = "AES256"
      }
      BucketKeyEnabled = $true
    }
  )
} | ConvertTo-Json -Depth 10 -Compress

$encryptionFile = Join-Path $env:TEMP "day8-s3-encryption.json"
Set-Content -LiteralPath $encryptionFile -Value $encryptionConfig -Encoding ascii
Invoke-Aws @(
  "s3api", "put-bucket-encryption",
  "--bucket", $EvidenceBucket,
  "--server-side-encryption-configuration", "file://$encryptionFile",
  "--profile", $Profile,
  "--region", $Region
) | Out-Null

Write-Host "Enabling versioning."
Invoke-Aws @(
  "s3api", "put-bucket-versioning",
  "--bucket", $EvidenceBucket,
  "--versioning-configuration", "Status=Enabled",
  "--profile", $Profile,
  "--region", $Region
) | Out-Null

Write-Host "Adding tags."
$taggingConfig = @{
  TagSet = @(
    @{ Key = "Project"; Value = "30-days-cloud-devops-projects" },
    @{ Key = "Day"; Value = "day-08" },
    @{ Key = "Environment"; Value = "learning" },
    @{ Key = "ManagedBy"; Value = "aws-cli" },
    @{ Key = "Owner"; Value = "barisagar" }
  )
} | ConvertTo-Json -Depth 10 -Compress

$taggingFile = Join-Path $env:TEMP "day8-s3-tags.json"
Set-Content -LiteralPath $taggingFile -Value $taggingConfig -Encoding ascii
Invoke-Aws @(
  "s3api", "put-bucket-tagging",
  "--bucket", $EvidenceBucket,
  "--tagging", "file://$taggingFile",
  "--profile", $Profile,
  "--region", $Region
) | Out-Null

Write-Host "Adding lifecycle hygiene rule."
$lifecycleConfig = @{
  Rules = @(
    @{
      ID = "day8-evidence-hygiene"
      Status = "Enabled"
      Filter = @{ Prefix = "" }
      AbortIncompleteMultipartUpload = @{ DaysAfterInitiation = 7 }
      NoncurrentVersionExpiration = @{ NoncurrentDays = 30 }
    }
  )
} | ConvertTo-Json -Depth 10 -Compress

$lifecycleFile = Join-Path $env:TEMP "day8-s3-lifecycle.json"
Set-Content -LiteralPath $lifecycleFile -Value $lifecycleConfig -Encoding ascii
Invoke-Aws @(
  "s3api", "put-bucket-lifecycle-configuration",
  "--bucket", $EvidenceBucket,
  "--lifecycle-configuration", "file://$lifecycleFile",
  "--profile", $Profile,
  "--region", $Region
) | Out-Null

Write-Host "Uploading Day 8 evidence object."
$evidenceText = @"
Day 8 AWS Cloud Foundation Evidence
Account: $accountId
Region: $Region
Bucket: $EvidenceBucket
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz")
"@

$evidenceFile = Join-Path $env:TEMP "day8-evidence.txt"
Set-Content -LiteralPath $evidenceFile -Value $evidenceText -Encoding ascii
Invoke-Aws @(
  "s3", "cp", $evidenceFile, "s3://$EvidenceBucket/day8/day8-evidence.txt",
  "--profile", $Profile,
  "--region", $Region
) | Out-Null

if (-not [string]::IsNullOrWhiteSpace($AlertEmail)) {
  Write-Host "Creating AWS Budget: Day8-Cloud-DevOps-Guardrail"

  $budgetConfig = @{
    BudgetName = "Day8-Cloud-DevOps-Guardrail"
    BudgetLimit = @{
      Amount = "$MonthlyBudgetUsd"
      Unit = "USD"
    }
    TimeUnit = "MONTHLY"
    BudgetType = "COST"
  } | ConvertTo-Json -Depth 10 -Compress

  $notificationConfig = ConvertTo-Json -InputObject @(
    @{
      Notification = @{
        NotificationType = "ACTUAL"
        ComparisonOperator = "GREATER_THAN"
        Threshold = 80
        ThresholdType = "PERCENTAGE"
      }
      Subscribers = @(
        @{
          SubscriptionType = "EMAIL"
          Address = $AlertEmail
        }
      )
    }
  ) -Depth 10 -Compress

  $budgetFile = Join-Path $env:TEMP "day8-budget.json"
  $notificationFile = Join-Path $env:TEMP "day8-budget-notification.json"
  Set-Content -LiteralPath $budgetFile -Value $budgetConfig -Encoding ascii
  Set-Content -LiteralPath $notificationFile -Value $notificationConfig -Encoding ascii

  try {
    Invoke-Aws @(
      "budgets", "create-budget",
      "--account-id", $accountId,
      "--budget", "file://$budgetFile",
      "--notifications-with-subscribers", "file://$notificationFile",
      "--profile", $Profile,
      "--region", "us-east-1"
    ) | Out-Null
    Write-Host "Budget created. Confirm the email subscription if AWS sends a confirmation email."
  } catch {
    Write-Host "Budget creation did not complete. It may already exist, or this identity may not have billing permissions."
    Write-Host "Create or verify the budget from AWS Console if needed."
  }
} else {
  Write-Host "AlertEmail not provided. Skipping AWS Budget API creation."
  Write-Host "Create a budget manually from AWS Console, or rerun with -AlertEmail."
}

Write-Host ""
Write-Host "Bootstrap complete."
Write-Host "Evidence bucket: $EvidenceBucket"
Write-Host "Verify with:"
Write-Host ".\scripts\verify-foundation.ps1 -Profile `"$Profile`" -Region `"$Region`" -EvidenceBucket `"$EvidenceBucket`""
