# AWS Security Audit Report

Generated: 2026-06-17T08:45:00.0000000+05:30

Account: 123456789012

Region: ap-south-1

Risk Score: 40/100

## Summary

- Total findings: 5
- Critical: 1
- High: 2
- Medium: 1
- Low: 1

## Findings

### [Critical] S3 bucket has public exposure signal or missing public access block

- Resource: devops-public-demo-bucket
- Recommendation: Enable S3 Block Public Access and review ACL/policy.
- Score impact: -25

### [High] IAM user does not have MFA enabled

- Resource: devops-admin
- Recommendation: Enable MFA for every human IAM user.
- Score impact: -12

### [High] Security group allows inbound access from the internet

- Resource: sg-0123456789abcdef0
- Recommendation: Restrict inbound CIDR ranges to trusted networks.
- Score impact: -15

### [Medium] Account password policy was not found

- Resource: AWS Account
- Recommendation: Configure a strong IAM account password policy.
- Score impact: -8

### [Low] No AWS Budget found

- Resource: AWS Account
- Recommendation: Create a monthly AWS Budget for cost guardrails.
- Score impact: -5
