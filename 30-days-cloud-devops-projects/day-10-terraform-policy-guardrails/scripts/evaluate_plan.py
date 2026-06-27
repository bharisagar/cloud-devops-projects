import argparse
import datetime as dt
import json
from pathlib import Path


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def find_rule(rules, rule_id):
    for rule in rules.get("rules", []):
        if rule["id"] == rule_id:
            return rule
    raise KeyError(f"Rule not found: {rule_id}")


def resource_list(plan):
    root = plan.get("planned_values", {}).get("root_module", {})
    resources = list(root.get("resources", []))
    for child in root.get("child_modules", []):
        resources.extend(child.get("resources", []))
    return resources


def tags_for(resource):
    values = resource.get("values") or {}
    tags = values.get("tags") or {}
    if not isinstance(tags, dict):
        return {}
    return tags


def add_finding(findings, rules, rule_id, resource, detail):
    rule = find_rule(rules, rule_id)
    impact = rules["severityScoreImpact"][rule["severity"]]
    findings.append(
        {
            "id": rule_id,
            "title": rule["title"],
            "severity": rule["severity"],
            "resource": resource,
            "detail": detail,
            "recommendation": rule["recommendation"],
            "scoreImpact": impact,
        }
    )


def has_strong_public_access_block(resources, bucket_name):
    for resource in resources:
        if resource.get("type") != "aws_s3_bucket_public_access_block":
            continue
        values = resource.get("values") or {}
        if values.get("bucket") != bucket_name:
            continue
        return all(
            values.get(key) is True
            for key in [
                "block_public_acls",
                "block_public_policy",
                "ignore_public_acls",
                "restrict_public_buckets",
            ]
        )
    return False


def contains_wildcard_admin(policy_text):
    if not policy_text:
        return False
    try:
        policy = json.loads(policy_text)
    except json.JSONDecodeError:
        compact = policy_text.replace(" ", "")
        return '"Action":"*"' in compact and '"Resource":"*"' in compact

    statements = policy.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]

    for statement in statements:
        actions = statement.get("Action", [])
        resources = statement.get("Resource", [])
        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]
        if "*" in actions and "*" in resources and statement.get("Effect") == "Allow":
            return True
    return False


def evaluate(plan, rules):
    findings = []
    resources = resource_list(plan)
    required_tags = set(rules.get("requiredTags", []))
    sensitive_ports = set(rules.get("sensitivePorts", []))

    for resource in resources:
        address = resource.get("address", "unknown")
        resource_type = resource.get("type")
        values = resource.get("values") or {}

        if resource_type in {
            "aws_s3_bucket",
            "aws_security_group",
            "aws_instance",
            "aws_db_instance",
            "aws_iam_policy",
        }:
            missing_tags = sorted(required_tags - set(tags_for(resource).keys()))
            if missing_tags:
                add_finding(
                    findings,
                    rules,
                    "MISSING_REQUIRED_TAGS",
                    address,
                    f"Missing tags: {', '.join(missing_tags)}",
                )

        if resource_type == "aws_s3_bucket":
            bucket_name = values.get("bucket")
            if bucket_name and not has_strong_public_access_block(resources, bucket_name):
                add_finding(
                    findings,
                    rules,
                    "S3_PUBLIC_ACCESS_BLOCK_MISSING",
                    address,
                    f"Bucket {bucket_name} does not have a strong public access block resource in this plan.",
                )

        if resource_type == "aws_security_group":
            for ingress in values.get("ingress", []) or []:
                cidrs = ingress.get("cidr_blocks", []) or []
                from_port = ingress.get("from_port")
                to_port = ingress.get("to_port")
                if "0.0.0.0/0" in cidrs:
                    add_finding(
                        findings,
                        rules,
                        "EC2_SECURITY_GROUP_OPEN_INTERNET",
                        address,
                        f"Ingress allows 0.0.0.0/0 on ports {from_port}-{to_port}.",
                    )
                    if from_port in sensitive_ports or to_port in sensitive_ports:
                        add_finding(
                            findings,
                            rules,
                            "EC2_SECURITY_GROUP_OPEN_SENSITIVE_PORT",
                            address,
                            f"Sensitive port {from_port}-{to_port} is exposed to the internet.",
                        )

        if resource_type == "aws_iam_policy" and contains_wildcard_admin(values.get("policy")):
            add_finding(
                findings,
                rules,
                "IAM_WILDCARD_ADMIN",
                address,
                "Policy allows Action '*' on Resource '*'.",
            )

        if resource_type == "aws_db_instance" and values.get("storage_encrypted") is False:
            add_finding(
                findings,
                rules,
                "RDS_STORAGE_NOT_ENCRYPTED",
                address,
                "RDS storage_encrypted is false.",
            )

        if resource_type == "aws_instance":
            for block in values.get("root_block_device", []) or []:
                if block.get("encrypted") is False:
                    add_finding(
                        findings,
                        rules,
                        "EBS_VOLUME_NOT_ENCRYPTED",
                        address,
                        "Root block device encryption is false.",
                    )

    for change in plan.get("resource_changes", []) or []:
        actions = change.get("change", {}).get("actions", [])
        if "delete" in actions:
            add_finding(
                findings,
                rules,
                "TERRAFORM_DELETE_ACTION",
                change.get("address", "unknown"),
                f"Plan action contains delete: {', '.join(actions)}.",
            )

    score = max(0, 100 - sum(finding["scoreImpact"] for finding in findings))
    summary = {
        "totalFindings": len(findings),
        "critical": len([item for item in findings if item["severity"] == "Critical"]),
        "high": len([item for item in findings if item["severity"] == "High"]),
        "medium": len([item for item in findings if item["severity"] == "Medium"]),
        "low": len([item for item in findings if item["severity"] == "Low"]),
    }

    minimum_score = rules.get("deploymentGate", {}).get("minimumScore", 80)
    block_on_critical = rules.get("deploymentGate", {}).get("blockOnCritical", True)
    has_critical = summary["critical"] > 0
    decision = "approved"
    if score < minimum_score or (block_on_critical and has_critical):
        decision = "blocked"

    return {
        "project": "Day 10 - Terraform Policy-as-Code Guardrail Platform",
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "planSource": "",
        "riskScore": score,
        "decision": decision,
        "deploymentGate": {
            "minimumScore": minimum_score,
            "blockOnCritical": block_on_critical,
        },
        "summary": summary,
        "findings": findings,
    }


def write_markdown(report, output_path):
    lines = [
        "# Terraform Policy Guardrail Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        f"Plan source: {report['planSource']}",
        "",
        f"Risk score: {report['riskScore']}/100",
        "",
        f"Decision: {report['decision'].upper()}",
        "",
        "## Summary",
        "",
        f"- Total findings: {report['summary']['totalFindings']}",
        f"- Critical: {report['summary']['critical']}",
        f"- High: {report['summary']['high']}",
        f"- Medium: {report['summary']['medium']}",
        f"- Low: {report['summary']['low']}",
        "",
        "## Findings",
        "",
    ]

    if not report["findings"]:
        lines.append("No findings detected.")
    else:
        for finding in report["findings"]:
            lines.extend(
                [
                    f"### [{finding['severity']}] {finding['title']}",
                    "",
                    f"- Resource: `{finding['resource']}`",
                    f"- Detail: {finding['detail']}",
                    f"- Recommendation: {finding['recommendation']}",
                    f"- Score impact: -{finding['scoreImpact']}",
                    "",
                ]
            )

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Evaluate Terraform plan JSON against Day 10 guardrails.")
    parser.add_argument("--plan", required=True, help="Path to Terraform plan JSON from terraform show -json.")
    parser.add_argument("--rules", required=True, help="Path to guardrails.json.")
    parser.add_argument("--output-json", default="reports/policy-report.json")
    parser.add_argument("--output-md", default="reports/policy-report.md")
    args = parser.parse_args()

    plan = load_json(args.plan)
    rules = load_json(args.rules)
    report = evaluate(plan, rules)
    report["planSource"] = str(Path(args.plan))

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, output_md)

    print(f"Risk score: {report['riskScore']}/100")
    print(f"Decision: {report['decision'].upper()}")
    print(f"JSON report: {output_json}")
    print(f"Markdown report: {output_md}")

    if report["decision"] == "blocked":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
