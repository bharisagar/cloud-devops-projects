# Day 10 Screenshot Evidence

Capture screenshots that prove the Terraform policy guardrail workflow works end to end.

## Recommended Evidence

| Screenshot | What It Shows |
| --- | --- |
| `evidence/01-evaluator-output.png` | `evaluate_plan.py` generated a score and blocked the risky plan. |
| `evidence/02-json-report.png` | JSON report generated with findings and deployment decision. |
| `evidence/03-markdown-report.png` | Markdown evidence report generated for human review. |
| `evidence/04-dashboard-overview.png` | Dashboard showing score, decision, and summary metrics. |
| `evidence/05-dashboard-findings.png` | Dashboard findings list with remediation guidance. |

## Evidence Checklist

- Terraform plan JSON was evaluated.
- Risk score was calculated.
- Deployment decision was shown.
- JSON and Markdown reports were generated.
- Dashboard loaded the report successfully.
- Findings explain the resource, risk, and recommended fix.
