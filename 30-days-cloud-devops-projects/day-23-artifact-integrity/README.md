# Day 23 - Artifact Integrity Check

Hash a release payload, record the digest, and verify that the bytes have not changed. A digest proves integrity relative to a trusted digest source; it does not prove who built the artifact.

## Architecture

`payload.txt` + `manifest.json` -> `verify.py` -> match/mismatch decision.

## Run

From this folder, run `python verify.py payload.txt manifest.json`. Then change a copy of the payload and verify it against the same manifest to see a mismatch. In a real pipeline, publish a signed provenance statement alongside the digest.

## Evidence

Capture a passing and failing verification and explain where the trusted digest must come from.

## Cleanup

No external artifacts are published.
