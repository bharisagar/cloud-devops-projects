# Day 20 - GitOps Drift Detection

Compare a desired workload snapshot with an observed snapshot. The sample shows a manual replica change outside version control.

## Architecture

`desired.json` + `observed.json` -> `compare.py` -> drift findings and exit status. These snapshots are synthetic; no cluster is queried.

## Run

From this folder, run `python compare.py desired.json observed.json`. Expect exit code 1. Copy the observed file, set replicas back to the desired value, and rerun. In a real GitOps workflow, the desired state comes from a reviewed Git commit and observed state from a cluster API.

## Evidence

Capture the drift finding and explain who should approve reconciliation. Avoid treating every difference as safe to overwrite; emergency changes need investigation.

## Cleanup

No cluster resources are created.
