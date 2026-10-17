# Day 15 Evidence

The `evidence/` folder contains desktop (`01-dashboard.png`) and compact (`02-mobile.png`) screenshots of the local dashboard reviewing the synthetic sample. They show the line number and finding, with no credential value in the result panel. `03-ci-success.png` captures the successful GitHub Actions validation and report artifact.

## Capture checklist

1. `run-demo.ps1` or `run-demo.sh` passing unit tests and checking both risky and clean samples.
2. Browser dashboard showing the sample finding and response checklist.
3. A clean scan after replacing the literal with `${PASSWORD_FROM_SECRET_MANAGER}`.
4. JSON or Markdown report with redacted findings.
5. GitHub Actions validation run after pushing the project.

Use only the included fake sample data. Do not capture real credentials, private infrastructure URLs, or customer data.
