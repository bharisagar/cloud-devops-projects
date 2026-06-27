import argparse
import datetime as dt
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_markdown(report, output_path):
    lines = [
        "# AI Incident Summary",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        f"Title: {report['title']}",
        "",
        f"Severity: {report['severity']}",
        "",
        f"Status: {report['status']}",
        "",
        "## Executive Summary",
        "",
        report["summary"],
        "",
        "## Probable Root Cause",
        "",
        report["probableRootCause"],
        "",
        "## Impact",
        "",
        f"- Impacted services: {', '.join(report['impactedServices'])}",
        f"- Peak error rate: {report['slo']['peakErrorRatePercent']}%",
        f"- Peak p95 latency: {report['slo']['peakP95LatencyMs']} ms",
        f"- SLO status: {report['slo']['status']}",
        "",
        "## Supporting Evidence",
        "",
    ]

    for item in report["evidence"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Timeline", ""])
    for event in report["timeline"]:
        lines.append(f"- {event['timestamp']} - [{event['service']}] {event['message']}")

    lines.extend(["", "## Recommended Commands", ""])
    for command in report["recommendedCommands"]:
        lines.append(f"```bash\n{command}\n```")

    lines.extend(["", "## Remediation Plan", ""])
    for index, action in enumerate(report["remediationPlan"], start=1):
        lines.append(f"{index}. {action}")

    lines.extend(["", "## Verification Checklist", ""])
    for item in report["verificationChecklist"]:
        lines.append(f"- [ ] {item}")

    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze(logs, metrics, traces):
    errors = [log for log in logs if log.get("severity") == "ERROR"]
    warnings = [log for log in logs if log.get("severity") == "WARN"]
    service_error_counts = Counter(log["service"] for log in errors)
    impacted_services = sorted({log["service"] for log in errors + warnings})

    requests_by_minute = defaultdict(int)
    errors_by_minute = defaultdict(int)
    latency_values = []
    for metric in metrics:
        minute = metric["timestamp"]
        if metric["metric"] == "http.server.requests":
            requests_by_minute[minute] += metric["value"]
        elif metric["metric"] == "http.server.errors":
            errors_by_minute[minute] += metric["value"]
        elif metric["metric"] == "http.server.duration.p95_ms":
            latency_values.append(metric["value"])

    peak_error_rate = 0.0
    for minute, requests in requests_by_minute.items():
        if requests:
            peak_error_rate = max(peak_error_rate, (errors_by_minute[minute] / requests) * 100)

    peak_latency = max(latency_values) if latency_values else 0
    failed_traces = [trace for trace in traces.get("traces", []) if trace.get("status") == "error"]
    slow_db_spans = []
    for trace in traces.get("traces", []):
        for span in trace.get("spans", []):
            if span.get("service") == "postgres" and span.get("duration_ms", 0) > 700:
                slow_db_spans.append({"trace_id": trace["trace_id"], **span})

    top_error_service = service_error_counts.most_common(1)[0][0] if service_error_counts else "unknown"
    probable_root_cause = (
        "Checkout failures are most likely caused by database connection pool saturation. "
        "Logs mention exhausted database connections, metrics show elevated checkout latency and errors, "
        "and traces show slow or failed postgres spans during order creation."
    )

    severity = "SEV2"
    if peak_error_rate >= 20 or peak_latency >= 1200:
        severity = "SEV1"
    elif peak_error_rate >= 5 or peak_latency >= 600:
        severity = "SEV2"

    timeline = []
    for log in logs:
        if log.get("severity") in {"WARN", "ERROR"}:
            timeline.append(
                {
                    "timestamp": log["timestamp"],
                    "service": log["service"],
                    "message": log["message"],
                    "trace_id": log.get("trace_id"),
                }
            )

    evidence = [
        f"{len(errors)} error log events and {len(warnings)} warning log events detected.",
        f"Top error source: {top_error_service}.",
        f"Peak checkout p95 latency reached {peak_latency} ms.",
        f"Peak checkout error rate reached {round(peak_error_rate, 2)}%.",
        f"{len(failed_traces)} traces ended with error status.",
        f"{len(slow_db_spans)} postgres spans exceeded 700 ms.",
    ]

    return {
        "project": "Day 11 - Observability Pipeline with AI Incident Summary",
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "title": "Checkout latency and 503 errors after release",
        "severity": severity,
        "status": "mitigating",
        "summary": (
            "The checkout path is degraded after a release. Telemetry shows elevated p95 latency, "
            "increased 503 errors, and failed traces concentrated around checkout-service and postgres. "
            "The incident should be treated as customer-impacting until checkout success rate recovers."
        ),
        "probableRootCause": probable_root_cause,
        "impactedServices": impacted_services,
        "slo": {
            "targetAvailabilityPercent": 99.5,
            "peakErrorRatePercent": round(peak_error_rate, 2),
            "peakP95LatencyMs": peak_latency,
            "status": "violated" if peak_error_rate > 2 or peak_latency > 500 else "healthy",
        },
        "signals": {
            "logEvents": len(logs),
            "metricPoints": len(metrics),
            "traceCount": len(traces.get("traces", [])),
            "failedTraceCount": len(failed_traces),
        },
        "evidence": evidence,
        "timeline": timeline,
        "recommendedCommands": [
            "kubectl logs deploy/checkout-service --since=30m",
            "kubectl describe deploy checkout-service",
            "kubectl top pods -l app=checkout-service",
            "kubectl exec deploy/checkout-service -- printenv | sort",
            "psql -c 'select count(*) from pg_stat_activity;'",
        ],
        "remediationPlan": [
            "Confirm whether the checkout release changed database connection settings.",
            "Scale checkout-service workers only if database capacity can support the extra connections.",
            "Reduce connection pool size or enable pooling through PgBouncer if saturation is confirmed.",
            "Rollback the release if error rate remains above SLO after mitigation.",
            "Create a follow-up action to add alerts for connection pool wait time.",
        ],
        "verificationChecklist": [
            "Checkout p95 latency is below 500 ms for 15 minutes.",
            "Checkout error rate is below 2% for 15 minutes.",
            "No new db connection pool exhausted errors appear in logs.",
            "Failed traces for POST /checkout return to baseline.",
            "Customer-facing checkout success rate is healthy.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze logs, metrics, and traces into an AI-style incident summary.")
    parser.add_argument("--logs", default="telemetry/sample-logs.jsonl")
    parser.add_argument("--metrics", default="telemetry/sample-metrics.jsonl")
    parser.add_argument("--traces", default="telemetry/sample-traces.json")
    parser.add_argument("--output-json", default="reports/sample-incident-summary.json")
    parser.add_argument("--output-md", default="reports/sample-incident-summary.md")
    args = parser.parse_args()

    report = analyze(load_jsonl(args.logs), load_jsonl(args.metrics), load_json(args.traces))
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, output_md)

    print(f"Incident: {report['title']}")
    print(f"Severity: {report['severity']}")
    print(f"SLO status: {report['slo']['status']}")
    print(f"Probable root cause: {report['probableRootCause']}")
    print(f"JSON report: {output_json}")
    print(f"Markdown report: {output_md}")


if __name__ == "__main__":
    main()