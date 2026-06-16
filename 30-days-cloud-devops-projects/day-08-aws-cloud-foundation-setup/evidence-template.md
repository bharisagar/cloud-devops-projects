# Day 8 Evidence And Project Documentation

## Project Name

AWS Cloud Foundation Setup

## Project Purpose

This project prepares a safe AWS foundation before deploying workloads such as EC2, ECS, Terraform-managed infrastructure, or Kubernetes clusters.

The objective is to prove that the AWS account is ready for hands-on DevOps work with the right baseline controls:

- Verified AWS CLI identity
- MFA-enabled account access
- Budget alert for cost control
- Private S3 evidence bucket
- Public access blocked
- Default encryption enabled
- Versioning enabled
- Ownership and project tags added
- Repeatable verification commands

This is a production-style starting point because real cloud work should begin with identity, cost safety, auditability, and evidence before compute resources are created.

## Architecture Summary

```text
Local terminal with AWS CLI profile
        |
        v
AWS STS identity verification
        |
        +----------------------------+
        |                            |
        v                            v
AWS Budget guardrail        S3 evidence bucket
Cost safety                 Private, encrypted, versioned
        |                            |
        v                            v
Email alert                 Day 8 evidence object
```

## Account And Identity Evidence

The AWS CLI was verified before creating resources. This ensures all commands run against the expected AWS account and IAM principal.

Command:

```powershell
aws --version
```

Evidence:

```text
CLI version output captured from the terminal during project execution.
```

Command:

```powershell
aws sts get-caller-identity --profile PROFILE_NAME --region REGION
```

Evidence:

```json
Caller identity output captured from AWS STS during project execution. Account details can be blurred before public posting.
```

## MFA Evidence

MFA was verified from the AWS Console. MFA protects the account from password-only compromise and is a basic control for any cloud environment.

Evidence screenshot:

```text
screenshots/02-iam-mfa-enabled.png
```

## Budget Guardrail Evidence

A monthly AWS budget was created to reduce the risk of unexpected charges during the 30-day project series.

Recommended budget:

```text
Budget name: Day8-Cloud-DevOps-Guardrail
Budget type: Monthly cost budget
Amount: 5 USD or another safe personal learning limit
Alert threshold: 80 percent actual spend
Notification: Email
```

Evidence screenshot:

```text
screenshots/03-budget-created.png
```

## S3 Evidence Bucket Controls

The evidence bucket is used to store proof from cloud projects. It is configured with production-minded controls.

| Control | Required State | Reason |
| --- | --- | --- |
| Public access block | Enabled | Prevents accidental public exposure |
| Default encryption | Enabled | Encrypts evidence objects at rest |
| Versioning | Enabled | Preserves object history |
| Tags | Present | Supports ownership, cost tracking, and cleanup |
| Lifecycle rule | Present | Cleans incomplete uploads and old noncurrent versions |

Verification command:

```powershell
.\scripts\verify-foundation.ps1 -Profile PROFILE_NAME -Region REGION -EvidenceBucket BUCKET_NAME
```

Evidence:

```text
Verification output captured from the Day 8 verification script.
```

## Screenshots Captured

| Evidence | Screenshot |
| --- | --- |
| STS identity output | screenshots/01-sts-caller-identity.png |
| IAM MFA enabled | screenshots/02-iam-mfa-enabled.png |
| Budget guardrail | screenshots/03-budget-created.png |
| S3 bucket overview | screenshots/04-s3-bucket-overview.png |
| S3 block public access | screenshots/05-s3-public-access-block.png |
| S3 encryption | screenshots/06-s3-encryption.png |
| S3 versioning | screenshots/07-s3-versioning.png |
| S3 tags | screenshots/08-s3-tags.png |
| Uploaded Day 8 object | screenshots/09-s3-uploaded-object.png |
| Intentional error and fix | screenshots/10-break-fix-terminal.png |

## Intentional Break And Fix

The project includes one controlled failure to practice cloud troubleshooting.

Example failure:

```powershell
aws s3api get-bucket-encryption --bucket wrong-day8-bucket-name --profile PROFILE_NAME --region REGION
```

Expected error:

```text
NoSuchBucket
```

Fix:

```powershell
.\scripts\verify-foundation.ps1 -Profile PROFILE_NAME -Region REGION -EvidenceBucket CORRECT_BUCKET_NAME
```

Troubleshooting lesson:

Before changing infrastructure, verify the active identity, region, resource name, and permissions. Many cloud issues are caused by the wrong profile, wrong region, incorrect resource name, or missing IAM permission.

## Final Project Explanation

Day 8 establishes the AWS foundation for the remaining cloud DevOps projects. The setup verifies the active AWS identity with STS, confirms account-level safety with MFA, adds a budget guardrail to control learning costs, and creates a private encrypted S3 bucket for project evidence. The bucket is hardened with public access blocking, versioning, lifecycle configuration, and ownership tags. This foundation makes future EC2, ECS, Terraform, Kubernetes, monitoring, and security projects safer because every deployment starts from a known account, controlled cost boundary, and documented evidence location.

## Interview-Ready Summary

I created a production-style AWS foundation before deploying workloads. I verified the active CLI identity using AWS STS, checked MFA from the console, created a monthly budget guardrail, and provisioned an S3 evidence bucket with public access blocked, encryption, versioning, lifecycle rules, and tags. This project demonstrates that DevOps work is not only about launching servers. It starts with identity, access control, billing safety, auditability, and repeatable verification.
