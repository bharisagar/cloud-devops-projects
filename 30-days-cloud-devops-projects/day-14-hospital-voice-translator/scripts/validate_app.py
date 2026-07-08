import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path


REQUIRED_APP_FILES = [
    "app/index.html",
    "app/styles.css",
    "app/app.js",
    "app/translation-pack.json",
]

REQUIRED_LANGUAGE_KEYS = ["english", "tamil", "telugu"]
REQUIRED_PHRASE_FIELDS = ["id", "intent", "severity", "kannada", "keywords", "english", "tamil", "telugu", "clinicalNote"]
REQUIRED_DOM_IDS = [
    "sourceText",
    "micButton",
    "translationGrid",
    "speakAllButton",
    "handoffLog",
    "safetyNotice",
]


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def load_json(path):
    return json.loads(read_text(path))


def add_issue(issues, severity, message, path=None):
    issues.append({"severity": severity, "message": message, "path": path})


def validate_files(root, issues):
    for relative_path in REQUIRED_APP_FILES:
        path = root / relative_path
        if not path.exists():
            add_issue(issues, "error", f"Missing required file: {relative_path}", relative_path)


def validate_html(root, issues):
    index_path = root / "app/index.html"
    if not index_path.exists():
        return
    html = read_text(index_path)
    for element_id in REQUIRED_DOM_IDS:
        if f'id="{element_id}"' not in html:
            add_issue(issues, "error", f"Missing required DOM id: {element_id}", "app/index.html")
    if "Clinical safety" not in html:
        add_issue(issues, "error", "Clinical safety banner is required.", "app/index.html")


def validate_js(root, issues):
    app_path = root / "app/app.js"
    if not app_path.exists():
        return
    js = read_text(app_path)
    required_terms = ["SpeechRecognition", "SpeechSynthesisUtterance", "translation-pack.json", "kn-IN"]
    for term in required_terms:
        if term not in js:
            add_issue(issues, "error", f"JavaScript missing expected term: {term}", "app/app.js")
    if re.search(r"https?://", js):
        add_issue(issues, "warning", "JavaScript contains an external URL. Keep demo privacy-first unless intentional.", "app/app.js")


def validate_translation_pack(root, issues):
    pack_path = root / "app/translation-pack.json"
    if not pack_path.exists():
        return None

    pack = load_json(pack_path)
    source = pack.get("sourceLanguage", {})
    if source.get("code") != "kn-IN":
        add_issue(issues, "error", "Source language must be Kannada kn-IN.", "app/translation-pack.json")

    languages = {item.get("key") for item in pack.get("targetLanguages", [])}
    for key in REQUIRED_LANGUAGE_KEYS:
        if key not in languages:
            add_issue(issues, "error", f"Missing target language key: {key}", "app/translation-pack.json")

    safety = pack.get("safetyNotice", {})
    for key in REQUIRED_LANGUAGE_KEYS:
        if not safety.get(key):
            add_issue(issues, "error", f"Missing safety notice translation: {key}", "app/translation-pack.json")

    phrases = pack.get("phrases", [])
    if len(phrases) < 10:
        add_issue(issues, "error", "At least 10 hospital phrases are required.", "app/translation-pack.json")

    urgent_count = 0
    seen_ids = set()
    for phrase in phrases:
        phrase_id = phrase.get("id", "unknown")
        if phrase_id in seen_ids:
            add_issue(issues, "error", f"Duplicate phrase id: {phrase_id}", "app/translation-pack.json")
        seen_ids.add(phrase_id)

        for field in REQUIRED_PHRASE_FIELDS:
            if not phrase.get(field):
                add_issue(issues, "error", f"Phrase {phrase_id} missing field: {field}", "app/translation-pack.json")
        if phrase.get("severity") == "urgent":
            urgent_count += 1
        if phrase.get("severity") not in {"routine", "urgent", "review"}:
            add_issue(issues, "error", f"Phrase {phrase_id} has invalid severity.", "app/translation-pack.json")

    if urgent_count < 2:
        add_issue(issues, "error", "At least two urgent phrases are required for safety demo coverage.", "app/translation-pack.json")

    fallback = pack.get("fallback", {})
    for key in ["english", "tamil", "telugu", "severity", "intent"]:
        if not fallback.get(key):
            add_issue(issues, "error", f"Fallback missing field: {key}", "app/translation-pack.json")

    return pack


def write_markdown(report, output_path):
    lines = [
        "# Day 14 Validation Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        f"Decision: {report['decision']}",
        "",
        f"Errors: {report['summary']['errors']}",
        "",
        f"Warnings: {report['summary']['warnings']}",
        "",
        f"Phrase count: {report['summary']['phraseCount']}",
        "",
        "## Checks",
        "",
    ]
    if not report["issues"]:
        lines.append("- All checks passed.")
    else:
        for issue in report["issues"]:
            path = f" ({issue['path']})" if issue.get("path") else ""
            lines.append(f"- {issue['severity']}: {issue['message']}{path}")
    lines.append("")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def validate(root):
    issues = []
    validate_files(root, issues)
    validate_html(root, issues)
    validate_js(root, issues)
    pack = validate_translation_pack(root, issues)

    errors = len([issue for issue in issues if issue["severity"] == "error"])
    warnings = len([issue for issue in issues if issue["severity"] == "warning"])
    phrase_count = len(pack.get("phrases", [])) if pack else 0

    return {
        "project": "Day 14 - Hospital Voice Translation Assistant",
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "decision": "passed" if errors == 0 else "failed",
        "summary": {
            "errors": errors,
            "warnings": warnings,
            "phraseCount": phrase_count,
        },
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate the Day 14 static hospital voice translation app.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-json", default="reports/sample-validation-report.json")
    parser.add_argument("--output-md", default="reports/sample-validation-report.md")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when validation fails.")
    args = parser.parse_args()

    root = Path(args.root)
    report = validate(root)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(report, output_md)

    print(f"Decision: {report['decision']}")
    print(f"Errors: {report['summary']['errors']}")
    print(f"Warnings: {report['summary']['warnings']}")
    print(f"Phrase count: {report['summary']['phraseCount']}")
    print(f"JSON report: {output_json}")
    print(f"Markdown report: {output_md}")

    if args.strict and report["decision"] != "passed":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())