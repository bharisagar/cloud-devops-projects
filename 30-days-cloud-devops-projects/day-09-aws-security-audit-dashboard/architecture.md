# Architecture - AWS Security Audit Dashboard

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Script as Audit Collector Script
    participant AWS as AWS APIs
    participant Report as JSON/Markdown Reports
    participant UI as Local Dashboard

    User->>Script: Run collector
    Script->>AWS: Read IAM, S3, EC2, CloudTrail, Budgets
    AWS-->>Script: Security posture data
    Script->>Script: Calculate findings and risk score
    Script->>Report: Write audit-report.json and audit-report.md
    User->>UI: Open dashboard
    UI->>Report: Load report JSON
    UI-->>User: Show score, findings, evidence
```

## Risk Model

The project starts with a score of `100` and subtracts points for risky signals:

| Finding | Severity | Score Impact |
|---|---:|---:|
| CloudTrail not logging | Critical | -25 |
| Public S3 bucket signal | Critical | -25 |
| Security group open to internet | High | -15 |
| User without MFA | High | -12 |
| AdministratorAccess attached | High | -12 |
| Access key older than 90 days | Medium | -8 |
| Missing password policy | Medium | -8 |
| No budget found | Low | -5 |

## Design Decisions

- Static dashboard keeps the project easy to run.
- JSON report is the contract between collectors and UI.
- Markdown report is recruiter-friendly evidence.
- Collector scripts avoid changing AWS resources.
