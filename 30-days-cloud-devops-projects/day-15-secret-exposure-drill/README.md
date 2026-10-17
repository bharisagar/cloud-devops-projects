# Day 15 - Secret Exposure Drill

Scan a deliberately fake configuration fixture for likely credentials and practice triage. Never commit real credentials to this exercise.

## Architecture

`sample.env.txt` -> `scan.py` -> line-numbered findings and nonzero exit status.

## Run

From this folder, run `python scan.py sample.env.txt`. Expect exit code 1 because the fixture contains a fake password. Replace its value with an environment-variable reference in a copy and rescan. The rules are training examples, not a substitute for a dedicated secret scanner.

## Evidence

Record the finding, its location, and a response plan: revoke a real exposed credential, remove it from use, replace it, then investigate where it spread. Do not paste a real secret into the report.

## Cleanup

Delete only temporary copies you created. No cloud resources are used.
