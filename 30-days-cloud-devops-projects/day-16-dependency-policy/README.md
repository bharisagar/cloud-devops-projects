# Day 16 - Dependency Policy Gate

Review a synthetic dependency inventory for license and age policy violations. This is a policy exercise, not a live vulnerability lookup.

## Architecture

`inventory.json` -> `check.py` -> pass/fail findings. All packages and dates in the sample are invented.

## Run

From this folder, run `python check.py inventory.json`. Expect a failure. Edit a copy to remove the disallowed license and old package, then rerun. In a real pipeline, generate the inventory with an SBOM tool and obtain vulnerability data from a maintained advisory source.

## Evidence

Capture both failing and passing output. Explain why a license exception needs an owner and review date.

## Cleanup

No resources are created.
