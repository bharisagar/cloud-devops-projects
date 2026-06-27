# Terraform Policy Guardrail Report

Generated: 2026-06-27T05:38:20.594508+00:00

Plan source: terraform\sample-risky-plan.json

Risk score: 0/100

Decision: BLOCKED

## Summary

- Total findings: 11
- Critical: 3
- High: 3
- Medium: 5
- Low: 0

## Findings

### [Medium] Resource is missing required governance tags

- Resource: `aws_s3_bucket.logs`
- Detail: Missing tags: CostCenter, Owner
- Recommendation: Add Project, Owner, Environment, and CostCenter tags.
- Score impact: -8

### [Critical] S3 bucket does not have strong public access block settings

- Resource: `aws_s3_bucket.logs`
- Detail: Bucket day-10-risky-logs-demo does not have a strong public access block resource in this plan.
- Recommendation: Add aws_s3_bucket_public_access_block with all block/restrict settings enabled.
- Score impact: -25

### [Medium] Resource is missing required governance tags

- Resource: `aws_security_group.web`
- Detail: Missing tags: CostCenter, Environment, Owner
- Recommendation: Add Project, Owner, Environment, and CostCenter tags.
- Score impact: -8

### [High] Security group allows inbound access from the internet

- Resource: `aws_security_group.web`
- Detail: Ingress allows 0.0.0.0/0 on ports 22-22.
- Recommendation: Restrict inbound CIDR ranges to a trusted network or remove the rule.
- Score impact: -15

### [Critical] Security group exposes a sensitive port to the internet

- Resource: `aws_security_group.web`
- Detail: Sensitive port 22-22 is exposed to the internet.
- Recommendation: Do not expose SSH, RDP, databases, or admin ports to 0.0.0.0/0.
- Score impact: -25

### [Medium] Resource is missing required governance tags

- Resource: `aws_iam_policy.wildcard_admin`
- Detail: Missing tags: CostCenter, Environment, Owner, Project
- Recommendation: Add Project, Owner, Environment, and CostCenter tags.
- Score impact: -8

### [Critical] IAM policy grants wildcard admin permissions

- Resource: `aws_iam_policy.wildcard_admin`
- Detail: Policy allows Action '*' on Resource '*'.
- Recommendation: Replace Action '*' and Resource '*' with least-privilege permissions.
- Score impact: -25

### [Medium] Resource is missing required governance tags

- Resource: `aws_db_instance.demo`
- Detail: Missing tags: CostCenter, Environment, Owner, Project
- Recommendation: Add Project, Owner, Environment, and CostCenter tags.
- Score impact: -8

### [High] RDS storage encryption is disabled

- Resource: `aws_db_instance.demo`
- Detail: RDS storage_encrypted is false.
- Recommendation: Set storage_encrypted = true and use a managed KMS key where appropriate.
- Score impact: -15

### [Medium] EBS or root volume encryption is disabled

- Resource: `aws_instance.legacy`
- Detail: Root block device encryption is false.
- Recommendation: Enable encryption for all block storage.
- Score impact: -8

### [High] Terraform plan contains a delete action

- Resource: `aws_instance.legacy`
- Detail: Plan action contains delete: delete.
- Recommendation: Require human approval before destructive infrastructure changes.
- Score impact: -15
