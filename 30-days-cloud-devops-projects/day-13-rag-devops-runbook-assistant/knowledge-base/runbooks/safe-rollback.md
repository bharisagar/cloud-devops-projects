# Safe Rollback Decision

## When To Use

Use this runbook when an incident begins soon after a deployment, feature flag change, image update, or configuration release.

## Rollback Criteria

- Customer-impacting error rate stays above SLO after first mitigation.
- The release changed code or configuration related to the failing path.
- There is no fast forward fix ready and tested.
- Telemetry shows the previous version was healthy.
- The rollback risk is lower than continuing customer impact.

## Immediate Checks

- Identify the deployment version and timestamp.
- Confirm whether the incident started after the release.
- Check database migrations for backward compatibility.
- Confirm the previous image or release artifact is available.
- Notify incident lead and service owner before rollback.

## Mitigation

- Roll back one service at a time when dependencies are shared.
- Watch error rate, p95 latency, and saturation during rollback.
- Pause automated deploys until the incident is closed.
- Capture the failed version, rollback command, and recovery timestamp.

## Verification

- Error rate falls below the incident threshold.
- Latency returns to baseline.
- New traces no longer show the failed code path.
- The incident channel confirms customer impact has stopped.