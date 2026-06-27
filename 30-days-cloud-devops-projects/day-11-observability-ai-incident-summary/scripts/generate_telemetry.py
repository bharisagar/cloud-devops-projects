import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TELEMETRY = ROOT / "telemetry"


def ts(minutes):
    base = dt.datetime(2026, 6, 27, 10, 0, tzinfo=dt.UTC)
    return (base + dt.timedelta(minutes=minutes)).isoformat()


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")


def main():
    logs = [
        {"timestamp": ts(0), "severity": "INFO", "service": "api-gateway", "message": "release 2026.06.27-1 started", "trace_id": "trace-100"},
        {"timestamp": ts(2), "severity": "INFO", "service": "checkout-service", "message": "deployment completed", "trace_id": "trace-101"},
        {"timestamp": ts(5), "severity": "WARN", "service": "checkout-service", "message": "database connection pool wait time above threshold", "trace_id": "trace-201"},
        {"timestamp": ts(7), "severity": "ERROR", "service": "checkout-service", "message": "checkout failed: db connection pool exhausted", "trace_id": "trace-202"},
        {"timestamp": ts(8), "severity": "ERROR", "service": "api-gateway", "message": "POST /checkout returned 503 from checkout-service", "trace_id": "trace-202"},
        {"timestamp": ts(10), "severity": "ERROR", "service": "checkout-service", "message": "payment authorization skipped because order write failed", "trace_id": "trace-203"},
        {"timestamp": ts(12), "severity": "WARN", "service": "postgres", "message": "active connections near max_connections", "trace_id": "trace-204"},
        {"timestamp": ts(15), "severity": "INFO", "service": "checkout-service", "message": "temporary scale-out started for checkout workers", "trace_id": "trace-205"},
    ]

    metrics = []
    for minute, latency, errors, requests in [
        (0, 145, 1, 220),
        (2, 160, 1, 230),
        (4, 310, 5, 240),
        (6, 920, 31, 235),
        (8, 1250, 48, 228),
        (10, 1380, 52, 225),
        (12, 1180, 42, 230),
        (14, 620, 18, 232),
    ]:
        metrics.append({"timestamp": ts(minute), "service": "checkout-service", "metric": "http.server.duration.p95_ms", "value": latency})
        metrics.append({"timestamp": ts(minute), "service": "checkout-service", "metric": "http.server.errors", "value": errors})
        metrics.append({"timestamp": ts(minute), "service": "checkout-service", "metric": "http.server.requests", "value": requests})

    traces = {
        "traces": [
            {
                "trace_id": "trace-201",
                "status": "slow",
                "duration_ms": 980,
                "spans": [
                    {"span_id": "a1", "service": "api-gateway", "operation": "POST /checkout", "duration_ms": 110, "status": "ok"},
                    {"span_id": "b1", "parent_span_id": "a1", "service": "checkout-service", "operation": "create_order", "duration_ms": 870, "status": "slow"},
                    {"span_id": "c1", "parent_span_id": "b1", "service": "postgres", "operation": "db.query insert orders", "duration_ms": 760, "status": "slow"}
                ]
            },
            {
                "trace_id": "trace-202",
                "status": "error",
                "duration_ms": 1430,
                "spans": [
                    {"span_id": "a2", "service": "api-gateway", "operation": "POST /checkout", "duration_ms": 80, "status": "error"},
                    {"span_id": "b2", "parent_span_id": "a2", "service": "checkout-service", "operation": "create_order", "duration_ms": 1350, "status": "error"},
                    {"span_id": "c2", "parent_span_id": "b2", "service": "postgres", "operation": "db.connection.acquire", "duration_ms": 1200, "status": "error"}
                ]
            },
            {
                "trace_id": "trace-203",
                "status": "error",
                "duration_ms": 1510,
                "spans": [
                    {"span_id": "a3", "service": "api-gateway", "operation": "POST /checkout", "duration_ms": 90, "status": "error"},
                    {"span_id": "b3", "parent_span_id": "a3", "service": "checkout-service", "operation": "create_order", "duration_ms": 1420, "status": "error"},
                    {"span_id": "c3", "parent_span_id": "b3", "service": "postgres", "operation": "db.query insert orders", "duration_ms": 1320, "status": "error"}
                ]
            }
        ]
    }

    TELEMETRY.mkdir(parents=True, exist_ok=True)
    write_jsonl(TELEMETRY / "sample-logs.jsonl", logs)
    write_jsonl(TELEMETRY / "sample-metrics.jsonl", metrics)
    (TELEMETRY / "sample-traces.json").write_text(json.dumps(traces, indent=2), encoding="utf-8")

    print("Generated telemetry files:")
    print(TELEMETRY / "sample-logs.jsonl")
    print(TELEMETRY / "sample-metrics.jsonl")
    print(TELEMETRY / "sample-traces.json")


if __name__ == "__main__":
    main()