# Day 22 - Release Quality Gate

Combine build, test, security, policy, and change approval signals into a single release decision.

## Architecture

`evidence.json` -> `gate.py` -> release decision. The input is a sample report, not a CI integration.

## Run

From this folder, run `python gate.py evidence.json`. Expect a blocked release because a security check failed. Change a copy to passing evidence and rerun. A production workflow should collect signed evidence from CI rather than trusting hand-edited JSON.

## Evidence

Capture the failing and passing decisions. Identify which role owns each gate and when an exception expires.

## Cleanup

No deployment occurs.
