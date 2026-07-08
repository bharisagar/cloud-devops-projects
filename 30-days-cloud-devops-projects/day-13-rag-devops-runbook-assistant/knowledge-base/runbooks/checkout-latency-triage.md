# Checkout Latency Triage

## When To Use

Use this runbook when checkout latency increases, users report failed orders, or telemetry shows elevated errors on `POST /checkout`.

## Symptoms

- Checkout p95 latency crosses the service objective.
- 503 or 500 errors appear after a release.
- Failed traces are concentrated around checkout-service.
- Order creation spans are slower than normal.
- Payment, inventory, or database calls create a downstream bottleneck.

## Immediate Checks

- Inspect `checkout-service` logs for errors in the last 30 minutes.
- Compare the error start time with deployments and configuration changes.
- Review traces for the slowest child span in the checkout path.
- Check dependency health for postgres, payment, and inventory services.
- Confirm whether retry behavior increased request volume.

## Mitigation

- If a recent release changed dependency behavior, roll back or disable the feature flag.
- If one downstream dependency is slow, reduce retry pressure and protect the dependency.
- If database queries are slow, inspect indexes and connection pool behavior.
- If payment provider errors are rising, fail gracefully and notify support.

## Verification

- Checkout success rate returns to normal.
- Failed checkout traces return to baseline.
- p95 latency remains under the SLO threshold for 15 minutes.
- Customer support reports stop increasing.