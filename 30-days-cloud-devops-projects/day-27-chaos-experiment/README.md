# Day 27 - Bounded Chaos Experiment

Evaluate a synthetic failure drill against a written hypothesis and stop conditions. The sample does not inject faults into a service.

## Architecture

`experiment.json` -> `evaluate.py` -> pass/fail analysis of recovery time and customer error rate.

## Run

From this folder, run `python evaluate.py experiment.json`. Expect a failed experiment because recovery is too slow. Change a copy to a faster recovery and rerun. Before a real experiment, define blast radius, owner, abort rule, and a rollback path.

## Evidence

Capture the hypothesis, observed result, and one engineering change that would improve recovery.

## Cleanup

No fault is injected and no resources are created.
