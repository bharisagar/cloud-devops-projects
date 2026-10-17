"""Apply simple reproducible rules to a synthetic dependency inventory."""
import json
import sys
from datetime import date


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    as_of = date.fromisoformat(data["as_of"])
    findings = []
    for package in data["packages"]:
        name = f"{package['name']}@{package['version']}"
        if package["license"] in data["blocked_licenses"]:
            findings.append(f"{name}: blocked license {package['license']}")
        age = (as_of - date.fromisoformat(package["last_updated"])).days
        if age > data["maximum_age_days"]:
            findings.append(f"{name}: last updated {age} days ago")
    for finding in findings:
        print(f"FAIL {finding}")
    print(f"Decision: {'BLOCK' if findings else 'PASS'}")
    return int(bool(findings))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "inventory.json"))
