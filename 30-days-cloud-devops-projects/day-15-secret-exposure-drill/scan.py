"""Identify obvious literal secret assignments in a training fixture."""
import re
import sys
from pathlib import Path


PATTERN = re.compile(r"^\s*(?:PASSWORD|TOKEN|API_KEY|SECRET)\s*=\s*(.+)$", re.I)


def main(path):
    findings = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        match = PATTERN.match(line)
        if not match:
            continue
        value = match.group(1).strip().strip('"\'')
        if value and not value.startswith(("${", "$", "<")):
            findings.append(number)
    for number in findings:
        print(f"Potential literal credential at line {number} (value hidden)")
    print(f"Findings: {len(findings)}")
    return int(bool(findings))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "sample.env.txt"))
