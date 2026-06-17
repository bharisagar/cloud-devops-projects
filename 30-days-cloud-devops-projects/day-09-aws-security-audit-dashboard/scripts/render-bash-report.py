import argparse
import datetime as dt
import json
from pathlib import Path


def parse_json(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def add_finding(findings, finding_id, title, severity, resource, recommendation, score_impact):
    findings.append(
        {
            "id": finding_id,
            "title": title,
            "severity": severity,
            "resource": resource,
            "recommendation": recommendation,
            "scoreImpact": score_impact,
        }
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity", required=True)
    parser.add_argument("--users", required=True)
    parser.add_argument("--password-policy", default="")
    parser.add_argument("--trails", default="")
    parser.add_argument("--security-groups", default="")
    parser.add_argument("--buckets", default="")
    parser.add_argument("--budgets", default="")
    parser.add_argument("--region", required=True)
    parser.add_argument("--old-access-key-days", type=int, default=90)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    identity = parse_json(args.identity, {})
    users = parse_json(args.users, {"Users": []})
    password_policy = parse_json(args.password_policy, {})
    trails = parse_json(args.trails, {"trailList": []})
    security_groups = parse_json(args.security_groups, {"SecurityGroups": []})
    buckets = parse_json(args.buckets, {"Buckets": []})
    budgets = parse_json(args.budgets, {"Budgets": []})
    findings = []

    # Bash collector keeps deep IAM per-user MFA/key checks in the PowerShell implementation.
    # It still produces a useful cross-service report for Linux/macOS users without extra dependencies.
    if not password_policy:
        add_finding(
            findings,
            "IAM-PASSWORD-POLICY",
            "Account password policy was not found",
            "Medium",
            "AWS Account",
            "Configure a strong IAM account password policy.",
            8,
        )

    trail_details = []
    for trail in trails.get("trailList", []):
        trail_details.append(
            {
                "name": trail.get("Name"),
                "trailArn": trail.get("TrailARN"),
                "isMultiRegionTrail": trail.get("IsMultiRegionTrail", False),
                "isLogging": "unknown",
            }
        )

    if not trail_details:
        add_finding(
            findings,
            "CLOUDTRAIL-MISSING",
            "No CloudTrail trail detected",
            "Critical",
            "CloudTrail",
            "Create and enable a multi-region CloudTrail trail.",
            25,
        )

    open_security_groups = []
    for group in security_groups.get("SecurityGroups", []):
        for permission in group.get("IpPermissions", []):
            open_ipv4 = any(r.get("CidrIp") == "0.0.0.0/0" for r in permission.get("IpRanges", []))
            open_ipv6 = any(r.get("CidrIpv6") == "::/0" for r in permission.get("Ipv6Ranges", []))
            if open_ipv4 or open_ipv6:
                from_port = permission.get("FromPort", "all")
                to_port = permission.get("ToPort", "all")
                open_security_groups.append(
                    {
                        "groupId": group.get("GroupId"),
                        "groupName": group.get("GroupName"),
                        "protocol": permission.get("IpProtocol"),
                        "portRange": f"{from_port}-{to_port}",
                    }
                )
                add_finding(
                    findings,
                    "EC2-OPEN-SG",
                    "Security group allows inbound access from the internet",
                    "High",
                    group.get("GroupId", "unknown"),
                    "Restrict inbound CIDR ranges to trusted networks.",
                    15,
                )

    if len(budgets.get("Budgets", [])) == 0:
        add_finding(
            findings,
            "BUDGET-MISSING",
            "No AWS Budget found",
            "Low",
            "AWS Account",
            "Create a monthly AWS Budget for cost guardrails.",
            5,
        )

    score = max(0, 100 - sum(item["scoreImpact"] for item in findings))
    summary = {
        "totalFindings": len(findings),
        "critical": len([f for f in findings if f["severity"] == "Critical"]),
        "high": len([f for f in findings if f["severity"] == "High"]),
        "medium": len([f for f in findings if f["severity"] == "Medium"]),
        "low": len([f for f in findings if f["severity"] == "Low"]),
    }

    report = {
        "project": "Day 9 - AWS Security Audit Dashboard",
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "region": args.region,
        "identity": identity,
        "riskScore": score,
        "summary": summary,
        "checks": {
            "passwordPolicyExists": bool(password_policy),
            "users": [{"userName": user.get("UserName"), "createDate": user.get("CreateDate")} for user in users.get("Users", [])],
            "cloudTrail": trail_details,
            "openSecurityGroups": open_security_groups,
            "s3Buckets": [{"name": bucket.get("Name"), "creationDate": bucket.get("CreationDate")} for bucket in buckets.get("Buckets", [])],
            "budgetCount": len(budgets.get("Budgets", [])),
        },
        "findings": findings,
    }

    Path(args.output_json).write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = [
        "# AWS Security Audit Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        f"Account: {identity.get('Account', 'unknown')}",
        "",
        f"Region: {args.region}",
        "",
        f"Risk Score: {score}/100",
        "",
        "## Summary",
        "",
        f"- Total findings: {summary['totalFindings']}",
        f"- Critical: {summary['critical']}",
        f"- High: {summary['high']}",
        f"- Medium: {summary['medium']}",
        f"- Low: {summary['low']}",
        "",
        "## Findings",
        "",
    ]

    if findings:
        for finding in findings:
            md.extend(
                [
                    f"### [{finding['severity']}] {finding['title']}",
                    "",
                    f"- Resource: {finding['resource']}",
                    f"- Recommendation: {finding['recommendation']}",
                    f"- Score impact: -{finding['scoreImpact']}",
                    "",
                ]
            )
    else:
        md.append("No findings detected.")

    Path(args.output_md).write_text("\n".join(md), encoding="utf-8")
    print(f"Risk score: {score}/100")


if __name__ == "__main__":
    main()
