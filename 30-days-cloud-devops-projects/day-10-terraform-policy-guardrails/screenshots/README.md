# Day 10 Screenshot Evidence

Capture screenshots that prove the Terraform policy guardrail workflow works end to end.

## Recommended Evidence

| Screenshot | What It Shows |
| --- | --- |
| `evidence/01-dashboard-overview.png` | Dashboard overview showing score, blocked decision, and summary metrics. |
| `evidence/02-dashboard-findings.png` | Dashboard findings list showing policy violations and recommended fixes. |
| `evidence/dashboard-preview.png` | Full-page dashboard preview captured during local verification. |

## Evidence Checklist

- Terraform plan JSON was evaluated.
- Risk score was calculated.
- Deployment decision was shown.
- JSON and Markdown reports were generated.
- Dashboard loaded the report successfully.
- Findings explain the resource, risk, and recommended fix.
