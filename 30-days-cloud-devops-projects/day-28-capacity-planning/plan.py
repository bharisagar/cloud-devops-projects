"""Estimate replicas from tested throughput and utilization headroom."""
import json
import math
import sys


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    assert data["peak_requests_per_second"] >= 0 and data["tested_requests_per_second_per_replica"] > 0
    assert 0 < data["target_utilization"] <= 1 and data["current_replicas"] >= 0
    safe_rate = data["tested_requests_per_second_per_replica"] * data["target_utilization"]
    required = max(1, math.ceil(data["peak_requests_per_second"] / safe_rate))
    gap = required - data["current_replicas"]
    print(f"Service: {data['service']}; safe throughput per replica: {safe_rate:.1f} req/s")
    print(f"Required replicas: {required}; current: {data['current_replicas']}; gap: {gap:+d}")
    print(f"Decision: {'PLAN CAPACITY CHANGE' if gap > 0 else 'CAPACITY SUFFICIENT IN MODEL'}")
    return int(gap > 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "demand.json"))
