# Secret exposure review

Source: sample.env.txt
Lines scanned: 4
Risk score: 20/100
Decision: BLOCK AND TRIAGE

## Findings

- Line 3 [high]: Literal password assignment. Move the value to a secret manager, rotate it if real, and review repository history.

## Response steps

1. Confirm whether the credential is real without copying its value into a ticket.
2. Revoke or disable exposed credentials and issue replacements.
3. Remove the literal from current configuration and use a managed secret reference.
4. Check access logs and repository history for potential use or spread.
5. Document owner, timeline, verification, and follow-up controls.

Limitations: Training rules detect simple patterns only. A clear result is not a security guarantee.
