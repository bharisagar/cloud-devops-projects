# Day 26 - Backup Restore Verification

Verify that a restored dataset matches the source dataset in a synthetic restore drill. A successful backup job alone is not proof that data can be recovered.

## Architecture

`source.json` + `restored.json` -> `verify.py` -> record count and content comparison. No actual database is touched.

## Run

From this folder, run `python verify.py source.json restored.json`. Expect a match. Delete or alter one record in a copy of the restored file and rerun to see a failure. For a real database, restore to an isolated environment and run application-level checks before declaring recovery complete.

## Evidence

Capture both outcomes and note the measured restore time and data loss window when you perform a real drill.

## Cleanup

No resources are created.
