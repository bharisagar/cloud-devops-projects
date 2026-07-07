import argparse
import datetime as dt
import json
import sys
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(as_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(f"{key} {as_text(item)}" for key, item in value.items())
    return str(value)


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def is_empty(value):
    return value is None or value == "" or value == [] or value == {}


def contains_any(text, terms):
    haystack = text.lower()
    return any(term.lower() in haystack for term in terms)


def score_groups(text, groups):
    matched = []
    missed = []
    for group in groups:
        if contains_any(text, group):
            matched.append(group)
        else:
            missed.append(group)
    return matched, missed


def proportional_points(weight, matched_count, total_count):
    if total_count == 0:
        return weight
    return round(weight * (matched_count / total_count), 2)


def status_for(points, weight):
    if points == weight:
        return "pass"
    if points == 0:
        return "fail"
    return "partial"


def add_check(checks, check_id, title, weight, points, expected, observed, recommendation, critical=False):
    checks.append(
        {
            "id": check_id,
            "title": title,
            "status": status_for(points, weight),
            "critical": critical,
            "points": round(points, 2),
            "maxPoints": weight,
            "expected": expected,
            "observed": observed,
            "recommendation": recommendation,
        }
    )


def evaluate_summary(summary, golden, case):
    expected = case["expected"]
    rubric = golden["rubric"]
    checks = []

    severity_points = rubric["severity"] if summary.get("severity") == expected["severity"] else 0
    add_check(
        checks,
        "severity",
        "Severity classification",
        rubric["severity"],
        severity_points,
        expected["severity"],
        summary.get("severity"),
        "Set the incident severity to match the measured customer impact.",
        critical=True,
    )

    required_services = {service.lower() for service in expected["impactedServices"]}
    observed_services = {service.lower() for service in summary.get("impactedServices", [])}
    matched_services = sorted(required_services & observed_services)
    missing_services = sorted(required_services - observed_services)
    service_points = proportional_points(rubric["impactedServices"], len(matched_services), len(required_services))
    add_check(
        checks,
        "impacted_services",
        "Impacted services",
        rubric["impactedServices"],
        service_points,
        sorted(required_services),
        sorted(observed_services),
        f"Add missing impacted services: {', '.join(missing_services)}." if missing_services else "All required services are present.",
    )

    root_text = as_text([summary.get("summary"), summary.get("probableRootCause"), summary.get("evidence")])
    matched_root, missed_root = score_groups(root_text, expected["rootCauseMustMention"])
    root_points = proportional_points(rubric["rootCause"], len(matched_root), len(expected["rootCauseMustMention"]))
    add_check(
        checks,
        "root_cause",
        "Probable root cause",
        rubric["rootCause"],
        root_points,
        expected["rootCauseMustMention"],
        {"matchedGroups": matched_root, "missedGroups": missed_root},
        "Explain the database connection pool saturation and connect it to checkout failures.",
        critical=True,
    )

    slo = summary.get("slo", {})
    slo_subchecks = [
        slo.get("status") == expected["sloStatus"],
        to_float(slo.get("peakErrorRatePercent")) >= to_float(expected["minimumPeakErrorRatePercent"]),
        to_float(slo.get("peakP95LatencyMs")) >= to_float(expected["minimumPeakP95LatencyMs"]),
    ]
    slo_points = proportional_points(rubric["slo"], len([item for item in slo_subchecks if item]), len(slo_subchecks))
    add_check(
        checks,
        "slo",
        "SLO impact",
        rubric["slo"],
        slo_points,
        {
            "status": expected["sloStatus"],
            "minimumPeakErrorRatePercent": expected["minimumPeakErrorRatePercent"],
            "minimumPeakP95LatencyMs": expected["minimumPeakP95LatencyMs"],
        },
        {
            "status": slo.get("status"),
            "peakErrorRatePercent": slo.get("peakErrorRatePercent"),
            "peakP95LatencyMs": slo.get("peakP95LatencyMs"),
        },
        "Include the violated SLO status, peak error rate, and peak p95 latency.",
    )

    evidence_text = as_text(summary.get("evidence"))
    matched_evidence, missed_evidence = score_groups(evidence_text, expected["evidenceMustMention"])
    evidence_points = proportional_points(rubric["evidence"], len(matched_evidence), len(expected["evidenceMustMention"]))
    add_check(
        checks,
        "evidence",
        "Supporting evidence",
        rubric["evidence"],
        evidence_points,
        expected["evidenceMustMention"],
        {"matchedGroups": matched_evidence, "missedGroups": missed_evidence},
        "Cite concrete log, metric, and trace evidence in the summary.",
    )

    action_text = as_text(
        [
            summary.get("recommendedCommands"),
            summary.get("remediationPlan"),
            summary.get("verificationChecklist"),
        ]
    )
    matched_actions, missed_actions = score_groups(action_text, expected["actionMustMention"])
    action_points = proportional_points(rubric["actionability"], len(matched_actions), len(expected["actionMustMention"]))
    add_check(
        checks,
        "actionability",
        "Actionability",
        rubric["actionability"],
        action_points,
        expected["actionMustMention"],
        {"matchedGroups": matched_actions, "missedGroups": missed_actions},
        "Include commands, mitigation steps, rollback criteria, and alert follow-up work.",
    )

    missing_fields = [field for field in expected["requiredFields"] if field not in summary or is_empty(summary.get(field))]
    structure_points = proportional_points(
        rubric["structure"],
        len(expected["requiredFields"]) - len(missing_fields),
        len(expected["requiredFields"]),
    )
    add_check(
        checks,
        "structure",
        "Required structure",
        rubric["structure"],
        structure_points,
        expected["requiredFields"],
        {"missingFields": missing_fields},
        f"Populate missing fields: {', '.join(missing_fields)}." if missing_fields else "All required fields are populated.",
    )

    report_text = as_text(summary)
    forbidden_found = [claim for claim in expected["forbiddenClaims"] if claim.lower() in report_text.lower()]
    hallucination_points = 0 if forbidden_found else rubric["hallucinationControl"]
    add_check(
        checks,
        "hallucination_control",
        "Unsupported claim control",
        rubric["hallucinationControl"],
        hallucination_points,
        "No forbidden unsupported claims",
        {"forbiddenClaimsFound": forbidden_found},
        "Remove unsupported claims that are not present in the telemetry.",
        critical=True,
    )

    score = round(sum(check["points"] for check in checks), 2)
    failed_critical = [check for check in checks if check["critical"] and check["status"] == "fail"]
    gate = golden["qualityGate"]
    decision = "passed"
    if score < gate["minimumScore"] or (gate["blockOnCriticalFailures"] and failed_critical):
        decision = "blocked"

    return {
        "id": case["id"],
        "title": case["title"],
        "summaryTitle": summary.get("title"),
        "score": score,
        "decision": decision,
        "checks": checks,
        "failedCriticalChecks": [check["id"] for check in failed_critical],
    }


def summarize_totals(test_case_results):
    checks = [check for result in test_case_results for check in result["checks"]]
    return {
        "totalChecks": len(checks),
        "passed": len([check for check in checks if check["status"] == "pass"]),
        "partial": len([check for check in checks if check["status"] == "partial"]),
        "failed": len([check for check in checks if check["status"] == "fail"]),
        "criticalFailures": len([check for check in checks if check["critical"] and check["status"] == "fail"]),
    }


def build_report(summary, golden, summary_path, golden_path):
    results = [evaluate_summary(summary, golden, case) for case in golden["testCases"]]
    average_score = round(sum(result["score"] for result in results) / len(results), 2)
    has_blocked_case = any(result["decision"] == "blocked" for result in results)
    overall_decision = "blocked" if has_blocked_case else "passed"

    failed_or_partial = [
        check
        for result in results
        for check in result["checks"]
        if check["status"] in {"fail", "partial"}
    ]
    next_actions = [check["recommendation"] for check in failed_or_partial]
    if not next_actions:
        next_actions = ["No fixes required. Keep the golden test case in regression coverage."]

    return {
        "project": golden["project"],
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "summarySource": str(summary_path),
        "goldenSource": str(golden_path),
        "qualityGate": golden["qualityGate"],
        "score": average_score,
        "decision": overall_decision,
        "totals": summarize_totals(results),
        "testCases": results,
        "nextActions": list(dict.fromkeys(next_actions)),
    }


def markdown_cell(value):
    text = as_text(value).replace("\n", " ")
    return text.replace("|", "\\|")


def write_markdown(report, output_path):
    lines = [
        "# EvalOps Quality Gate Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        f"Decision: {report['decision']}",
        "",
        f"Score: {report['score']} / 100",
        "",
        f"Gate minimum score: {report['qualityGate']['minimumScore']}",
        "",
        f"Critical failures: {report['totals']['criticalFailures']}",
        "",
        "## Summary",
        "",
        f"- Total checks: {report['totals']['totalChecks']}",
        f"- Passed: {report['totals']['passed']}",
        f"- Partial: {report['totals']['partial']}",
        f"- Failed: {report['totals']['failed']}",
        "",
    ]

    for test_case in report["testCases"]:
        lines.extend(
            [
                f"## Test Case: {test_case['title']}",
                "",
                f"- Test ID: `{test_case['id']}`",
                f"- Summary: {test_case['summaryTitle']}",
                f"- Decision: {test_case['decision']}",
                f"- Score: {test_case['score']} / 100",
                "",
                "| Check | Status | Points | Recommendation |",
                "| --- | --- | ---: | --- |",
            ]
        )
        for check in test_case["checks"]:
            points = f"{check['points']} / {check['maxPoints']}"
            lines.append(
                f"| {markdown_cell(check['title'])} | {check['status']} | {points} | {markdown_cell(check['recommendation'])} |"
            )
        lines.append("")

    lines.extend(["## Next Actions", ""])
    for action in report["nextActions"]:
        lines.append(f"- {action}")
    lines.append("")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Evaluate an AI incident summary against golden EvalOps expectations.")
    parser.add_argument("--summary", default="summaries/sample-generated-incident-summary.json")
    parser.add_argument("--golden", default="evals/golden-incidents.json")
    parser.add_argument("--output-json", default="reports/sample-eval-report.json")
    parser.add_argument("--output-md", default="reports/sample-eval-report.md")
    parser.add_argument("--enforce-gate", action="store_true", help="Exit non-zero when the quality gate is blocked.")
    args = parser.parse_args()

    summary_path = Path(args.summary)
    golden_path = Path(args.golden)
    report = build_report(load_json(summary_path), load_json(golden_path), summary_path, golden_path)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, output_md)

    print(f"Eval score: {report['score']}")
    print(f"Decision: {report['decision']}")
    print(f"Gate: minimum score {report['qualityGate']['minimumScore']}")
    print(f"JSON report: {output_json}")
    print(f"Markdown report: {output_md}")

    if args.enforce_gate and report["decision"] == "blocked":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())