"""Compare resource snapshots without contacting a cloud provider."""
import json
import sys


def main(desired_path, observed_path):
    desired = json.load(open(desired_path, encoding="utf-8"))["resources"]
    observed = json.load(open(observed_path, encoding="utf-8"))["resources"]
    findings = []
    for address in sorted(set(desired) | set(observed)):
        if address not in desired or address not in observed:
            findings.append(f"{address}: resource {'unexpected' if address in observed else 'missing'}")
            continue
        for field in sorted(set(desired[address]) | set(observed[address])):
            if desired[address].get(field) != observed[address].get(field):
                findings.append(f"{address}.{field}: desired={desired[address].get(field)!r}, observed={observed[address].get(field)!r}")
    for finding in findings:
        print(f"DRIFT {finding}")
    print(f"Decision: {'REVIEW' if findings else 'IN SYNC'}")
    return int(bool(findings))


if __name__ == "__main__":
    sys.exit(main(*(sys.argv[1:] or ["desired.json", "observed.json"])))
