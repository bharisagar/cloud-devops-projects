# Database Connection Pool Saturation

## When To Use

Use this runbook when an application shows elevated latency, 503 responses, checkout failures, slow database spans, or log messages such as `connection pool exhausted`, `too many clients`, or `active connections near maximum`.

## Symptoms

- Application p95 latency rises above the SLO threshold.
- Error rate increases during write-heavy requests.
- Logs mention database connection pool exhaustion or timeout waiting for a connection.
- Traces show slow `postgres`, `db.query`, or `order creation` spans.
- Database active connections approach the configured maximum.

## Immediate Checks

- Check application logs for connection pool exhausted errors.
- Check database active connections and wait events.
- Compare release time with the start of errors.
- Check whether worker count, pool size, or connection timeout changed.
- Review failed traces for slow database spans.

## Mitigation

- Reduce application connection pool size if every replica opens too many connections.
- Scale application replicas only when database capacity supports the extra connections.
- Add PgBouncer or another connection pooler for high-concurrency workloads.
- Roll back the release if the pool settings changed and customer impact continues.
- Avoid restarting every application replica at once because reconnection storms can worsen saturation.

## Verification

- Error rate stays below 2 percent for at least 15 minutes.
- p95 latency returns below 500 ms.
- Database active connections remain below 80 percent of maximum.
- New traces show normal `db.query` duration.
- No new pool exhausted messages appear in logs.