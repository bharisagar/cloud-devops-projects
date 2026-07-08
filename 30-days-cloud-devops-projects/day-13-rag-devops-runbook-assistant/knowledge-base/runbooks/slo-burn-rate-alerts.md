# SLO Burn Rate Alerts

## When To Use

Use this runbook when error rate or latency threatens the service objective and responders need to know whether the incident is burning error budget too quickly.

## Symptoms

- Availability drops below the target objective.
- Error rate remains above the alert threshold.
- p95 latency breaches the latency SLO.
- Multiple alert windows fire together, such as 5 minute and 30 minute burn rates.

## Immediate Checks

- Calculate current error rate and compare it with the SLO threshold.
- Check whether the alert is isolated to one service or shared dependency.
- Confirm if customer-facing endpoints are affected.
- Review recent deployments and infrastructure changes.

## Mitigation

- Treat fast burn alerts as customer-impacting until disproven.
- Route to the service owner and incident lead.
- Prefer mitigation that quickly reduces impact over root-cause perfection.
- Create a follow-up action for missing alerts or noisy alert rules.

## Verification

- Burn rate returns below alert threshold.
- Error budget consumption slows to normal.
- Alerts clear without being manually silenced.
- Post-incident notes include the SLO impact window.