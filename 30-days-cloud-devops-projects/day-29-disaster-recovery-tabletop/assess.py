"""Compare a tabletop drill with recovery objectives."""
import json
import sys


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    observed = data["observed"]
    failures = []
    if observed["recovery_minutes"] > data["rto_minutes"]:
        failures.append(f"RTO missed: {observed['recovery_minutes']} > {data['rto_minutes']} minutes")
    if observed["data_loss_minutes"] > data["rpo_minutes"]:
        failures.append(f"RPO missed: {observed['data_loss_minutes']} > {data['rpo_minutes']} minutes")
    print(f"Scenario: {data['scenario']}")
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"Decision: {'RECOVERY PLAN NEEDS WORK' if failures else 'OBJECTIVES MET IN TABLETOP'}")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "drill.json"))
