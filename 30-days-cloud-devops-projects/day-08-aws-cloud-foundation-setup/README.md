# Day 8: AWS Cloud Foundation Setup

## Overview

Day 8 starts the cloud section of the 30 Days Cloud DevOps Projects series.

The first AWS project should not be an EC2 launch. A strong cloud journey starts by proving that the account, identity, billing guardrails, and evidence storage are ready. This project creates that foundation in a practical, production-minded way.

The setup prepares an AWS account for the remaining projects in the roadmap, including EC2, RDS, VPC, Terraform, ECS, Kubernetes, observability, security, backup, and disaster recovery.

## Project Goal

Create a safe AWS foundation with repeatable CLI verification and AWS Console evidence.

The project focuses on four production habits:

- Know which AWS identity is active before making changes.
- Protect account access with MFA.
- Protect personal learning accounts from surprise cost.
- Store project evidence in a private, encrypted, versioned S3 bucket.

## What This Project Creates

| Component | Purpose |
| --- | --- |
| AWS CLI identity verification | Confirms the active AWS account and IAM principal |
| MFA console evidence | Confirms account access is protected |
| AWS Budget guardrail | Sends cost alerts before spend becomes a problem |
| S3 evidence bucket | Stores screenshots, logs, outputs, and project proof |
| Public access block | Prevents accidental public exposure of evidence |
| Default encryption | Encrypts objects at rest |
| Versioning | Preserves history for uploaded evidence files |
| Bucket tags | Adds ownership, environment, and project metadata |
| Lifecycle rule | Cleans incomplete uploads and old noncurrent versions |
| Verification script | Produces repeatable proof for screenshots and README evidence |

## Architecture

```text
+----------------------------+
| Local machine              |
| AWS CLI named profile      |
+-------------+--------------+
              |
              v
+----------------------------+
| AWS STS                    |
| Caller identity check      |
+-------------+--------------+
              |
              +-------------------------------+
              |                               |
              v                               v
+----------------------------+   +----------------------------+
| AWS Budgets                |   | S3 Evidence Bucket         |
| Monthly cost guardrail     |   | Private, encrypted, tagged |
+----------------------------+   +-------------+--------------+
                                               |
                                               v
                                  +----------------------------+
                                  | Day 8 evidence object      |
                                  | Console screenshots        |
                                  | Verification output        |
                                  +----------------------------+
```

## Production Controls

### Identity Verification

Before creating resources, the active AWS identity is verified with AWS STS.

This prevents a common cloud mistake: deploying into the wrong account or using the wrong IAM principal.

### MFA

MFA protects AWS access from password-only compromise. This is a baseline security control for any AWS account.

### Budget Guardrail

A budget alarm gives early warning when AWS cost crosses a threshold. For learning accounts, this is one of the most important safety controls.

### Private Evidence Bucket

The evidence bucket is used as a controlled location for proof from this and future cloud projects.

The bucket is hardened with:

- Block public access
- Default encryption
- Versioning
- Lifecycle hygiene
- Tags for ownership and cleanup

## Folder Structure

```text
day-08-aws-cloud-foundation-setup/
|-- README.md
|-- evidence-template.md
|-- linkedin-post-draft.md
|-- scripts/
|   |-- bootstrap-foundation.ps1
|   `-- verify-foundation.ps1
`-- screenshots/
    `-- README.md
```

## Prerequisites

- AWS account
- AWS CLI v2
- Configured AWS CLI profile
- Console access for MFA and screenshots
- Practice region such as `ap-south-1`

Check available profiles:

```powershell
aws configure list-profiles
```

Check AWS CLI version:

```powershell
aws --version
```

## Step 1: Select Profile And Region

Use a named profile so the project is explicit about which account is being used.

Example:

```powershell
$Profile = "default"
$Region = "ap-south-1"
```

Verify identity:

```powershell
aws sts get-caller-identity --profile $Profile --region $Region
```

Capture a terminal screenshot of the result. Blur account details before posting publicly if preferred.

## Step 2: Confirm MFA In Console

Open AWS Console and verify MFA is enabled for the active user or account access method.

Capture a screenshot showing MFA enabled.

Do not publish:

- Access keys
- Secret keys
- MFA QR codes
- Recovery codes
- Sensitive billing details

## Step 3: Run Foundation Bootstrap

From this folder:

```powershell
cd 30-days-cloud-devops-projects\day-08-aws-cloud-foundation-setup
```

Run without budget email:

```powershell
.\scripts\bootstrap-foundation.ps1 `
  -Profile "default" `
  -Region "ap-south-1"
```

Run with budget creation:

```powershell
.\scripts\bootstrap-foundation.ps1 `
  -Profile "default" `
  -Region "ap-south-1" `
  -MonthlyBudgetUsd 5 `
  -AlertEmail "your-email@example.com"
```

The script creates or hardens the evidence bucket and uploads a Day 8 evidence object.

If budget creation fails because the IAM identity does not have billing permissions, create the budget manually in the AWS Console and capture the screenshot. That is acceptable because many accounts restrict billing APIs.

## Step 4: Verify The Foundation

Use the bucket name printed by the bootstrap script.

```powershell
.\scripts\verify-foundation.ps1 `
  -Profile "default" `
  -Region "ap-south-1" `
  -EvidenceBucket "YOUR-BUCKET-NAME"
```

The verification script checks:

- Caller identity
- Bucket existence
- Public access block
- Default encryption
- Versioning
- Tags
- Lifecycle rule
- Uploaded `day8/day8-evidence.txt` object

This output becomes terminal evidence for the project.

## Step 5: Capture AWS Console Evidence

Use `screenshots/README.md` as the screenshot checklist.

Required screenshots:

- STS caller identity terminal output
- IAM MFA enabled
- Budget guardrail
- S3 bucket overview
- S3 block public access
- S3 encryption
- S3 versioning
- S3 tags
- Uploaded Day 8 object
- Intentional error and fix

## Intentional Break And Fix

Test a wrong bucket name:

```powershell
aws s3api get-bucket-encryption `
  --bucket wrong-day8-bucket-name `
  --profile "default" `
  --region "ap-south-1"
```

Expected result:

```text
NoSuchBucket
```

Fix by using the correct bucket:

```powershell
.\scripts\verify-foundation.ps1 `
  -Profile "default" `
  -Region "ap-south-1" `
  -EvidenceBucket "CORRECT-BUCKET-NAME"
```

This proves a practical troubleshooting pattern: confirm identity, region, resource name, and permission before changing infrastructure.

## Troubleshooting

### Credentials Not Found

```powershell
aws configure list-profiles
aws sts get-caller-identity --profile "default"
```

### Access Denied

The active identity may not have permission for S3, Budgets, or STS. Verify the IAM policy attached to the user or role.

### Budget API Fails

Some AWS accounts restrict billing access. Create the budget from the Billing console and document the screenshot.

### Bucket Name Already Exists

S3 bucket names are globally unique. Pass a custom name:

```powershell
.\scripts\bootstrap-foundation.ps1 `
  -Profile "default" `
  -Region "ap-south-1" `
  -EvidenceBucket "yourname-day8-evidence-12345"
```

### Wrong Region

```powershell
aws configure get region --profile "default"
```

Use the same region for bootstrap and verification.

## Cleanup

The budget and evidence bucket can remain for the rest of the 30-day series.

Delete only the Day 8 evidence object:

```powershell
aws s3 rm s3://YOUR-BUCKET-NAME/day8/day8-evidence.txt --profile "default"
```

Delete the bucket only when the full learning series no longer needs it:

```powershell
aws s3 rb s3://YOUR-BUCKET-NAME --force --profile "default"
```

## Final Project Explanation

This project establishes the AWS foundation for all later cloud DevOps projects. It verifies the active AWS identity, confirms MFA, creates a cost guardrail, and provisions a private S3 bucket for project evidence. The bucket is configured with public access blocking, encryption, versioning, lifecycle management, and tags. These controls make the account safer for future EC2, ECS, Terraform, Kubernetes, monitoring, and security work because every project starts from a verified identity, controlled cost boundary, and documented evidence location.

## Interview-Ready Summary

I created a production-style AWS foundation before deploying workloads. I verified the active CLI identity using AWS STS, checked MFA from the console, created a monthly budget guardrail, and provisioned an S3 evidence bucket with public access blocked, encryption, versioning, lifecycle rules, and tags. This project demonstrates that DevOps work starts with identity, access control, billing safety, auditability, and repeatable verification before application deployment.

