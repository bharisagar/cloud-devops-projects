# Day 28 - Capacity Planning

Estimate required replicas from peak requests, safe per-replica capacity, and headroom. This is a planning model, not a load test.

## Architecture

`demand.json` -> `plan.py` -> required replicas and capacity gap.

## Run

From this folder, run `python plan.py demand.json`. The sample needs more replicas than are currently allocated. Change peak demand or per-replica capacity in a copy to explore tradeoffs. Validate any real decision with load tests and production telemetry.

## Evidence

Capture the calculated replica count, assumptions, and proposed rollout. Explain why extra replicas alone may not fix a shared database bottleneck.

## Cleanup

No infrastructure is changed.
