"""Local secret exposure triage for training data, not a production secret scanner."""

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ASSIGNMENT = re.compile(r"(?i)\b(password|api[_-]?key|token|secret)\s*[:=]\s*(.+)$")
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
SAFE_REFERENCE = re.compile(r"^(?:\$\{[^}]+\}|\$[A-Z_][A-Z0-9_]*|<[^>]+>|process\.env\.[A-Z_][A-Z0-9_]*|vault://\S+)$")


def scan_text(text, source="pasted input"):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        if PRIVATE_KEY.search(line):
            findings.append({
                "id": f"KEY-{number}", "line": number, "severity": "critical",
                "title": "Private key material marker",
                "action": "Treat the key as exposed. Revoke it, replace it, then investigate access logs.",
            })
        match = ASSIGNMENT.search(line)
        if not match or line.lstrip().startswith("#"):
            continue
        value = match.group(2).strip().strip("\"'")
        if not value or SAFE_REFERENCE.fullmatch(value):
            continue
        findings.append({
            "id": f"LITERAL-{number}", "line": number, "severity": "high",
            "title": f"Literal {match.group(1).lower()} assignment",
            "action": "Move the value to a secret manager, rotate it if real, and review repository history.",
        })
    score = min(100, sum(40 if item["severity"] == "critical" else 20 for item in findings))
    return {
        "source": source,
        "lines_scanned": len(text.splitlines()),
        "risk_score": score,
        "decision": "BLOCK AND TRIAGE" if findings else "NO MATCHES IN TRAINING RULES",
        "findings": findings,
        "response_steps": [
            "Confirm whether the credential is real without copying its value into a ticket.",
            "Revoke or disable exposed credentials and issue replacements.",
            "Remove the literal from current configuration and use a managed secret reference.",
            "Check access logs and repository history for potential use or spread.",
            "Document owner, timeline, verification, and follow-up controls.",
        ],
        "limitations": "Training rules detect simple patterns only. A clear result is not a security guarantee.",
    }


def markdown(report):
    lines = [
        "# Secret exposure review", "", f"Source: {report['source']}",
        f"Lines scanned: {report['lines_scanned']}",
        f"Risk score: {report['risk_score']}/100", f"Decision: {report['decision']}",
        "", "## Findings", "",
    ]
    lines.extend(
        f"- Line {item['line']} [{item['severity']}]: {item['title']}. {item['action']}"
        for item in report["findings"]
    )
    if not report["findings"]:
        lines.append("- No pattern matches.")
    lines.extend(["", "## Response steps", ""])
    lines.extend(f"{number}. {step}" for number, step in enumerate(report["response_steps"], 1))
    lines.extend(["", f"Limitations: {report['limitations']}", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=ROOT / "sample.env.txt")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()
    report = scan_text(args.path.read_text(encoding="utf-8"), args.path.name)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(markdown(report), encoding="utf-8")
    print(f"{report['decision']}: {len(report['findings'])} finding(s), score {report['risk_score']}/100")
    for finding in report["findings"]:
        print(f"  line {finding['line']}: {finding['title']} (value hidden)")
    return int(bool(report["findings"]))


if __name__ == "__main__":
    raise SystemExit(main())
