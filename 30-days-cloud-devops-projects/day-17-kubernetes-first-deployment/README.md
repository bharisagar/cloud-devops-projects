# Day 17 - First Kubernetes Deployment

Package a small web workload as a Deployment and internal Service. Render the manifest locally before connecting to any cluster.

## Architecture

Client -> `Service/hello` -> two `Deployment/hello` Pods. The Deployment uses a fixed image version, a container port, and labels shared with the Service selector.

## Run

From this folder, run `kubectl kustomize .`. Inspect the rendered image, replica count, labels, selector, and port. On a learning cluster you control, optionally run `kubectl apply -k . -n <your-namespace>` and `kubectl get deploy,svc,pods -n <your-namespace>`. Use a dedicated namespace and check the current Kubernetes context first.

## Evidence

Capture the rendered YAML. If you use a cluster, capture rollout status and explain how the Service finds Pods.

## Cleanup

For resources you created in your dedicated namespace: `kubectl delete -k . -n <your-namespace>`.
