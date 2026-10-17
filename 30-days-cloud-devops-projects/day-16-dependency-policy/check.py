"""Deterministic policy gate for a synthetic dependency inventory."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _date(value, field):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD)") from exc


def evaluate(inventory, policy):
    if not isinstance(inventory, dict) or not isinstance(policy, dict):
        raise ValueError("inventory and policy must be JSON objects")
    as_of = _date(inventory.get("as_of"), "as_of")
    packages = inventory.get("packages")
    if not isinstance(packages, list) or not packages:
        raise ValueError("packages must be a non-empty array")
    blocked = policy.get("blocked_licenses")
    maximum = policy.get("maximum_review_age_days")
    if not isinstance(blocked, list) or any(not isinstance(x, str) for x in blocked):
        raise ValueError("blocked_licenses must be an array of strings")
    if type(maximum) is not int or maximum < 0:
        raise ValueError("maximum_review_age_days must be a non-negative integer")
    require_owner = policy.get("require_owner")
    if type(require_owner) is not bool:
        raise ValueError("require_owner must be a boolean")
    blocked_set = {x.upper() for x in blocked}

    findings = []
    components = []
    seen = set()
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise ValueError(f"packages[{index}] must be an object")
        name, version, license_id, owner = (package.get(key) for key in ("name", "version", "license", "owner"))
        if not all(isinstance(x, str) and x.strip() for x in (name, version, license_id)):
            raise ValueError(f"packages[{index}] requires non-empty name, version, and license")
        if owner is not None and not isinstance(owner, str):
            raise ValueError(f"packages[{index}].owner must be a string")
        updated = _date(package.get("last_reviewed"), f"packages[{index}].last_reviewed")
        if updated > as_of:
            raise ValueError(f"packages[{index}].last_reviewed cannot be after as_of")
        key = (name.lower(), version)
        if key in seen:
            raise ValueError(f"duplicate component {name}@{version}")
        seen.add(key)
        age = (as_of - updated).days
        component_findings = []
        for condition, code, detail, action in (
            (license_id.upper() in blocked_set, "BLOCKED_LICENSE", f"License {license_id} is blocked by policy.", "Replace the component or obtain an approved exception."),
            (age > maximum, "STALE_REVIEW", f"Last policy review was {age} days ago (limit {maximum}).", "Review the component and record a new review date."),
            (require_owner and not (owner or "").strip(), "MISSING_OWNER", "No accountable owner is recorded.", "Assign an owner before release."),
        ):
            if condition:
                finding = {"component": f"{name}@{version}", "code": code, "detail": detail, "action": action}
                findings.append(finding)
                component_findings.append(code)
        components.append({"name": name, "version": version, "license": license_id, "owner": owner or "", "last_reviewed": updated.isoformat(), "review_age_days": age, "status": "BLOCK" if component_findings else "PASS", "finding_codes": component_findings})
    return {
        "as_of": as_of.isoformat(),
        "decision": "BLOCK" if findings else "PASS",
        "summary": {"components": len(components), "blocked_components": sum(x["status"] == "BLOCK" for x in components), "findings": len(findings)},
        "policy": {"blocked_licenses": blocked, "maximum_review_age_days": maximum, "require_owner": require_owner},
        "components": components,
        "findings": findings,
        "scope": "Synthetic inventory policy checks only; no vulnerability or live registry lookup.",
    }


def markdown(report):
    lines = [
        "# Dependency Policy Report", "",
        f"Decision: **{report['decision']}**", "",
        f"As of: {report['as_of']}", "",
        f"Components: {report['summary']['components']}", "",
        f"Blocked components: {report['summary']['blocked_components']}", "",
        f"Findings: {report['summary']['findings']}", "",
        "## Findings", "",
    ]
    if not report["findings"]:
        lines.append("No policy violations.")
    else:
        for item in report["findings"]:
            lines.append(f"- **{item['component']} [{item['code']}]** {item['detail']} {item['action']}")
    lines.extend(["", "## Scope", "", report["scope"], ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", nargs="?", default=str(ROOT / "inventory.json"))
    parser.add_argument("--policy", default=str(ROOT / "policy.json"))
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args(argv)
    try:
        inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
        policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
        report = evaluate(inventory, policy)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2
    if args.output_json:
        target = Path(args.output_json)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        target = Path(args.output_md)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown(report), encoding="utf-8")
    for item in report["findings"]:
        print(f"FAIL {item['component']} [{item['code']}]: {item['detail']}")
    print(f"Decision: {report['decision']} | {report['summary']['components']} components | {report['summary']['findings']} findings")
    return 1 if report["decision"] == "BLOCK" else 0


if __name__ == "__main__":
    sys.exit(main())
