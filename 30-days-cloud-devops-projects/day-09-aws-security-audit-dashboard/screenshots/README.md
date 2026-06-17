# Day 9 Screenshot Evidence

These screenshots prove that the AWS Security Audit Dashboard was served locally and displayed the generated sample evidence report.

## Evidence Files

| Screenshot | What It Shows |
| --- | --- |
| `evidence/01-dashboard-overview.png` | Dashboard overview with risk score, account metadata, and finding counts. |
| `evidence/02-dashboard-findings.png` | Findings and service checks sections with prioritized risk signals. |
| `evidence/03-local-server-evidence.png` | Local Python HTTP server output showing dashboard assets and report JSON loaded successfully. |
| `evidence/dashboard-preview.png` | Full-page generated preview captured during local verification. |

## Evidence Checklist

- Dashboard loaded at `http://localhost:8089/dashboard/`.
- Sample report loaded from `reports/sample-audit-report.json`.
- Risk score and finding summary rendered.
- Findings and service checks rendered.
- Local server logs captured.
