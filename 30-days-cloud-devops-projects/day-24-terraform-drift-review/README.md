# Day 24 - Terraform Drift Review

Compare a planned infrastructure snapshot with an observed snapshot and flag out-of-band changes for review. This lab uses synthetic snapshots; it does not read Terraform state or call AWS.

## Architecture

`desired.json` + `observed.json` -> `drift.py` -> field-level differences. Resources are keyed by stable address.

## Run

From this folder, run `python drift.py desired.json observed.json`. Expect a finding for an opened SSH port. Change a copy of the observed input to restore the approved ingress list and rerun. For real Terraform, first run a refresh-only plan in a controlled workspace and review it before changing state.

## Evidence

Capture the drift result and record whether the live change should be reverted or codified through review.

## Cleanup

No infrastructure is created or modified.
