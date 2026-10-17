# Day 19 - Environment Overlays with Kustomize

Reuse one workload definition for staging and production while varying only the replica count and environment label.

## Architecture

`base/` + `overlays/staging/` or `overlays/production/` -> rendered Kubernetes manifests.

## Run

From this folder, run `kubectl kustomize overlays/staging` and `kubectl kustomize overlays/production`. Compare the replica counts, names, and labels. The production overlay is an example, not an instruction to deploy to production.

## Evidence

Capture both rendered outputs and explain how one base prevents environment configuration from drifting. Check that the Service selector still matches Pod labels.

## Cleanup

Rendering creates no resources. If you applied an overlay to your own cluster, delete that same overlay from the same namespace.
