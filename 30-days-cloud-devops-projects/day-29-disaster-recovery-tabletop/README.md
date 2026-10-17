# Day 29 - Disaster Recovery Tabletop

Compare observed recovery time and data loss with RTO and RPO objectives. This sample is a tabletop result, not a live failover.

## Architecture

`drill.json` -> `assess.py` -> objective checks and recovery decision.

## Run

From this folder, run `python assess.py drill.json`. Expect an RPO failure. Change a copy to a smaller data loss window and rerun. A real drill should also record who declared the incident, who approved failover, and when traffic returned.

## Evidence

Capture the pass/fail result and list two changes that could reduce data loss. Link the backup verification evidence from Day 26.

## Cleanup

No failover or cloud change occurs.
