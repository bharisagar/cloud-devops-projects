"""Score a bounded failure drill against explicit stop conditions."""
import json
import sys


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    observed = data["observed"]
    failures = []
    if observed["recovery_seconds"] > data["max_recovery_seconds"]:
        failures.append("recovery time exceeded")
    if observed["error_rate_percent"] > data["max_error_rate_percent"]:
        failures.append("customer error rate exceeded")
    print(f"Hypothesis: {data['hypothesis']}")
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"Decision: {'IMPROVE AND RETEST' if failures else 'HYPOTHESIS SUPPORTED'}")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "experiment.json"))
