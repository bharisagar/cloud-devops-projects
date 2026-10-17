"""Require every named gate to pass before a release is eligible."""
import json
import sys


REQUIRED = ("build", "unit_tests", "integration_tests", "security_scan", "terraform_policy", "change_approval")


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    failures = [name for name in REQUIRED if data["checks"].get(name) is not True]
    for name in failures:
        print(f"FAIL {name}")
    print(f"{data['release']}: {'BLOCKED' if failures else 'ELIGIBLE FOR REVIEW'}")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "evidence.json"))
