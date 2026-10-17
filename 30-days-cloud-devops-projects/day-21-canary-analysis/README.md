# Day 21 - Canary Release Analysis

Decide whether to promote or roll back a canary using baseline and canary metrics. This lab analyzes sample data; it never sends traffic.

## Architecture

`metrics.json` -> `analyze.py` -> threshold checks -> promote/rollback decision.

## Run

From this folder, run `python analyze.py metrics.json`. The sample should recommend rollback. Change a copy so the canary stays within both limits, then rerun. Use a minimum sample size so a tiny traffic slice cannot create false confidence.

## Evidence

Record the error-rate and p95-latency comparisons. Explain why rollout approval also needs human review and sufficient observation time.

## Cleanup

No deployments are performed.
