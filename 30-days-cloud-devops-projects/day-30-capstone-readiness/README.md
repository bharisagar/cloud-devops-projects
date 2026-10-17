# Day 30 - Cloud DevOps Readiness Capstone

Run the local exercises together and create a portfolio-level readiness summary. The sample deliberately includes failed gates so the final decision requires remediation and another run.

## Architecture

`review.py` invokes Days 15-29, checks that each exercise returned its documented sample outcome, then reports the number of unresolved gates. Kubernetes days are rendered locally with `kubectl kustomize`; no cluster is touched.

## Run

From this folder, run `python review.py`. Required tools: Python 3.10+ and `kubectl`. The script locates the repository root from its own path. It prints each check and exits with code 1 while sample risks remain. Use the earlier READMEs to resolve each failed gate in a copy of its fixture, then rerun the individual lab to prove the change.

## Portfolio evidence

Record the capstone output, selected screenshots from earlier days, unresolved risks, owners, and next review dates. A professional final presentation should include the actual commands and evidence collected, not claim that synthetic exercises were run in production.

## Cleanup

The capstone only reads local files and renders YAML. It creates no cloud or cluster resources.
