# Day 18 - Kubernetes Health and Rollout Controls

Extend a web Deployment with readiness, liveness, resource limits, and a conservative rolling update. Compare this manifest with Day 17.

## Architecture

The readiness probe controls whether a Pod receives Service traffic. The liveness probe restarts an unhealthy container. Resource requests and limits bound scheduling and usage.

## Run

From this folder, run `kubectl kustomize .`. Inspect both probes, `maxUnavailable`, and CPU/memory values. On your own learning cluster, optionally apply to a dedicated namespace and run `kubectl rollout status deployment/hello-guarded -n <your-namespace>`.

## Evidence

Capture the rendered YAML and write down what happens if readiness fails while liveness succeeds. Do not use a public LoadBalancer for this lab.

## Cleanup

For resources you created in your dedicated namespace: `kubectl delete -k . -n <your-namespace>`.
