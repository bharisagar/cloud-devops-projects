# EvalOps Quality Gate Report

Generated: 2026-07-07T16:46:16.325483+00:00

Decision: passed

Score: 100.0 / 100

Gate minimum score: 80

Critical failures: 0

## Summary

- Total checks: 8
- Passed: 8
- Partial: 0
- Failed: 0

## Test Case: Checkout outage caused by database connection pool saturation

- Test ID: `checkout-db-pool-saturation`
- Summary: Checkout latency and 503 errors after release
- Decision: passed
- Score: 100.0 / 100

| Check | Status | Points | Recommendation |
| --- | --- | ---: | --- |
| Severity classification | pass | 10 / 10 | Set the incident severity to match the measured customer impact. |
| Impacted services | pass | 12.0 / 12 | All required services are present. |
| Probable root cause | pass | 20.0 / 20 | Explain the database connection pool saturation and connect it to checkout failures. |
| SLO impact | pass | 12.0 / 12 | Include the violated SLO status, peak error rate, and peak p95 latency. |
| Supporting evidence | pass | 16.0 / 16 | Cite concrete log, metric, and trace evidence in the summary. |
| Actionability | pass | 16.0 / 16 | Include commands, mitigation steps, rollback criteria, and alert follow-up work. |
| Required structure | pass | 8.0 / 8 | All required fields are populated. |
| Unsupported claim control | pass | 6 / 6 | Remove unsupported claims that are not present in the telemetry. |

## Next Actions

- No fixes required. Keep the golden test case in regression coverage.
