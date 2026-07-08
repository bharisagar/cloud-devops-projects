# Node.js Memory Pressure

## When To Use

Use this runbook when a Node.js service shows memory growth, process restarts, garbage collection pressure, or out of memory errors.

## Symptoms

- Container memory approaches the limit.
- The service restarts with out of memory errors.
- Latency increases during garbage collection pauses.
- Heap usage grows after each request burst.
- Logs include allocation failure or heap out of memory messages.

## Immediate Checks

- Check pod or container memory usage.
- Review restart count and exit reasons.
- Compare memory growth with traffic and release timing.
- Capture a heap snapshot in a safe environment.
- Inspect recent changes for caching or unbounded queues.

## Mitigation

- Roll back the release if memory growth began after deployment.
- Reduce traffic or disable the feature that triggers the leak.
- Increase memory limit only as a temporary mitigation.
- Add alerts for memory growth and restart count.

## Verification

- Memory remains stable under normal traffic.
- Restart count stops increasing.
- Latency returns to baseline.
- No new out of memory events appear.