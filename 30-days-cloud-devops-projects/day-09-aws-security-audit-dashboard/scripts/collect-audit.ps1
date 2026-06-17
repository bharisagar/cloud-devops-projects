param(
    [string]$ProfileName = "",
    [string]$Region = "ap-south-1",
    [int]$OldAccessKeyDays = 90
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReportsDir = Join-Path $ProjectRoot "reports"
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

function Invoke-AwsJson {
    param(
        [string[]]$Arguments,
        [switch]$AllowFailure
    )

    $baseArgs = @()
    if ($ProfileName) { $baseArgs += @("--profile", $ProfileName) }
    if ($Region) { $baseArgs += @("--region", $Region) }

    $output = & aws @baseArgs @Arguments --output json 2>$null
    if ($LASTEXITCODE -ne 0) {
        if ($AllowFailure) { return $null }
        throw "AWS CLI command failed: aws $($Arguments -join ' ')"
    }

    if (-not $output) { return $null }
    return $output | ConvertFrom-Json
}

function Add-Finding {
    param(
        [System.Collections.Generic.List[object]]$Findings,
        [string]$Id,
        [string]$Title,
        [string]$Severity,
        [string]$Resource,
        [string]$Recommendation,
        [int]$ScoreImpact
    )

    $Findings.Add([ordered]@{
        id = $Id
        title = $Title
        severity = $Severity
        resource = $Resource
        recommendation = $Recommendation
        scoreImpact = $ScoreImpact
    }) | Out-Null
}

Write-Host "Starting AWS security audit..."

$identity = Invoke-AwsJson @("sts", "get-caller-identity")
$accountSummary = Invoke-AwsJson @("iam", "get-account-summary") -AllowFailure
$passwordPolicy = Invoke-AwsJson @("iam", "get-account-password-policy") -AllowFailure
$usersResponse = Invoke-AwsJson @("iam", "list-users")
$trails = Invoke-AwsJson @("cloudtrail", "describe-trails") -AllowFailure
$securityGroups = Invoke-AwsJson @("ec2", "describe-security-groups") -AllowFailure
$buckets = Invoke-AwsJson @("s3api", "list-buckets") -AllowFailure
$budgets = Invoke-AwsJson @("budgets", "describe-budgets", "--account-id", $identity.Account) -AllowFailure

$findings = [System.Collections.Generic.List[object]]::new()
$iamUsers = @()
$now = Get-Date

foreach ($user in $usersResponse.Users) {
    $userName = $user.UserName
    $mfaDevices = Invoke-AwsJson @("iam", "list-mfa-devices", "--user-name", $userName) -AllowFailure
    $accessKeys = Invoke-AwsJson @("iam", "list-access-keys", "--user-name", $userName) -AllowFailure
    $attachedPolicies = Invoke-AwsJson @("iam", "list-attached-user-policies", "--user-name", $userName) -AllowFailure

    $keyDetails = @()
    foreach ($key in @($accessKeys.AccessKeyMetadata)) {
        $ageDays = [int]($now - ([datetime]$key.CreateDate)).TotalDays
        $keyDetails += [ordered]@{
            accessKeyId = $key.AccessKeyId
            status = $key.Status
            ageDays = $ageDays
        }

        if ($ageDays -gt $OldAccessKeyDays -and $key.Status -eq "Active") {
            Add-Finding $findings "IAM-OLD-KEY" "Active access key older than $OldAccessKeyDays days" "Medium" $userName "Rotate or delete old access keys." 8
        }
    }

    $hasMfa = @($mfaDevices.MFADevices).Count -gt 0
    if (-not $hasMfa) {
        Add-Finding $findings "IAM-NO-MFA" "IAM user does not have MFA enabled" "High" $userName "Enable MFA for every human IAM user." 12
    }

    $adminPolicies = @($attachedPolicies.AttachedPolicies | Where-Object { $_.PolicyName -eq "AdministratorAccess" })
    if ($adminPolicies.Count -gt 0) {
        Add-Finding $findings "IAM-ADMIN" "IAM user has AdministratorAccess attached" "High" $userName "Replace broad admin access with least-privilege permissions." 12
    }

    $iamUsers += [ordered]@{
        userName = $userName
        createDate = $user.CreateDate
        hasMfa = $hasMfa
        accessKeys = $keyDetails
        attachedPolicies = @($attachedPolicies.AttachedPolicies.PolicyName)
    }
}

if (-not $passwordPolicy) {
    Add-Finding $findings "IAM-PASSWORD-POLICY" "Account password policy was not found" "Medium" "AWS Account" "Configure a strong IAM account password policy." 8
}

$trailDetails = @()
foreach ($trail in @($trails.trailList)) {
    $status = Invoke-AwsJson @("cloudtrail", "get-trail-status", "--name", $trail.TrailARN) -AllowFailure
    $isLogging = [bool]$status.IsLogging
    $trailDetails += [ordered]@{
        name = $trail.Name
        trailArn = $trail.TrailARN
        isMultiRegionTrail = $trail.IsMultiRegionTrail
        isLogging = $isLogging
    }
}

if (@($trailDetails | Where-Object { $_.isLogging }).Count -eq 0) {
    Add-Finding $findings "CLOUDTRAIL-NOT-LOGGING" "No active CloudTrail logging detected" "Critical" "CloudTrail" "Enable CloudTrail logging for audit evidence." 25
}

$openSecurityGroups = @()
foreach ($group in @($securityGroups.SecurityGroups)) {
    foreach ($permission in @($group.IpPermissions)) {
        $openIpv4 = @($permission.IpRanges | Where-Object { $_.CidrIp -eq "0.0.0.0/0" }).Count -gt 0
        $openIpv6 = @($permission.Ipv6Ranges | Where-Object { $_.CidrIpv6 -eq "::/0" }).Count -gt 0
        if ($openIpv4 -or $openIpv6) {
            $fromPort = if ($null -ne $permission.FromPort) { $permission.FromPort } else { "all" }
            $toPort = if ($null -ne $permission.ToPort) { $permission.ToPort } else { "all" }
            $openSecurityGroups += [ordered]@{
                groupId = $group.GroupId
                groupName = $group.GroupName
                protocol = $permission.IpProtocol
                portRange = "$fromPort-$toPort"
            }
            Add-Finding $findings "EC2-OPEN-SG" "Security group allows inbound access from the internet" "High" $group.GroupId "Restrict inbound CIDR ranges to trusted networks." 15
        }
    }
}

$s3Details = @()
foreach ($bucket in @($buckets.Buckets)) {
    $bucketName = $bucket.Name
    $publicAccess = Invoke-AwsJson @("s3api", "get-public-access-block", "--bucket", $bucketName) -AllowFailure
    $acl = Invoke-AwsJson @("s3api", "get-bucket-acl", "--bucket", $bucketName) -AllowFailure
    $publicGrants = @($acl.Grants | Where-Object {
        $_.Grantee.URI -match "AllUsers|AuthenticatedUsers"
    })

    $hasPublicBlock = $null -ne $publicAccess
    $hasPublicGrant = $publicGrants.Count -gt 0
    if ($hasPublicGrant -or -not $hasPublicBlock) {
        Add-Finding $findings "S3-PUBLIC-RISK" "S3 bucket has public exposure signal or missing public access block" "Critical" $bucketName "Enable S3 Block Public Access and review ACL/policy." 25
    }

    $s3Details += [ordered]@{
        name = $bucketName
        creationDate = $bucket.CreationDate
        hasPublicAccessBlock = $hasPublicBlock
        hasPublicAclGrant = $hasPublicGrant
    }
}

if (-not $budgets -or @($budgets.Budgets).Count -eq 0) {
    Add-Finding $findings "BUDGET-MISSING" "No AWS Budget found" "Low" "AWS Account" "Create a monthly AWS Budget for cost guardrails." 5
}

$score = 100
foreach ($finding in $findings) { $score -= [int]$finding.scoreImpact }
$score = [Math]::Max(0, $score)

$report = [ordered]@{
    project = "Day 9 - AWS Security Audit Dashboard"
    generatedAt = (Get-Date).ToString("o")
    region = $Region
    identity = $identity
    riskScore = $score
    summary = [ordered]@{
        totalFindings = $findings.Count
        critical = @($findings | Where-Object { $_.severity -eq "Critical" }).Count
        high = @($findings | Where-Object { $_.severity -eq "High" }).Count
        medium = @($findings | Where-Object { $_.severity -eq "Medium" }).Count
        low = @($findings | Where-Object { $_.severity -eq "Low" }).Count
    }
    checks = [ordered]@{
        iamAccountSummary = $accountSummary.SummaryMap
        passwordPolicyExists = $null -ne $passwordPolicy
        users = $iamUsers
        cloudTrail = $trailDetails
        openSecurityGroups = $openSecurityGroups
        s3Buckets = $s3Details
        budgetCount = if ($budgets) { @($budgets.Budgets).Count } else { 0 }
    }
    findings = $findings
}

$jsonPath = Join-Path $ReportsDir "audit-report.json"
$mdPath = Join-Path $ReportsDir "audit-report.md"
$report | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$markdown = @"
# AWS Security Audit Report

Generated: $($report.generatedAt)

Account: $($identity.Account)

Region: $Region

Risk Score: $score/100

## Summary

- Total findings: $($report.summary.totalFindings)
- Critical: $($report.summary.critical)
- High: $($report.summary.high)
- Medium: $($report.summary.medium)
- Low: $($report.summary.low)

## Findings

"@

foreach ($finding in $findings) {
    $markdown += @"
### [$($finding.severity)] $($finding.title)

- Resource: $($finding.resource)
- Recommendation: $($finding.recommendation)
- Score impact: -$($finding.scoreImpact)

"@
}

if ($findings.Count -eq 0) {
    $markdown += "No findings detected.`n"
}

$markdown | Set-Content -LiteralPath $mdPath -Encoding UTF8

Write-Host "Audit complete."
Write-Host "JSON report: $jsonPath"
Write-Host "Markdown report: $mdPath"
Write-Host "Risk score: $score/100"
