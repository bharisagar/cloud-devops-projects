"""Evaluate sample canary metrics against explicit guardrails."""
import json
import sys


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    baseline, canary = data["baseline"], data["canary"]
    assert baseline["requests"] > 0 and canary["requests"] > 0 and baseline["p95_ms"] > 0
    assert 0 <= baseline["errors"] <= baseline["requests"] and 0 <= canary["errors"] <= canary["requests"]
    error_increase = 100 * (canary["errors"] / canary["requests"] - baseline["errors"] / baseline["requests"])
    latency_increase = 100 * (canary["p95_ms"] / baseline["p95_ms"] - 1)
    failures = []
    if canary["requests"] < data["minimum_requests"]:
        failures.append("insufficient canary traffic")
    if error_increase > data["max_error_rate_increase_pct_points"]:
        failures.append(f"error rate increased {error_increase:.2f} percentage points")
    if latency_increase > data["max_p95_latency_increase_percent"]:
        failures.append(f"p95 latency increased {latency_increase:.1f}%")
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"Decision: {'ROLL BACK / INVESTIGATE' if failures else 'ELIGIBLE FOR REVIEW'}")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "metrics.json"))
