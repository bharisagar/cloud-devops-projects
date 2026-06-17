#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORTS_DIR="$PROJECT_ROOT/reports"
REGION="${AWS_REGION:-ap-south-1}"
OLD_ACCESS_KEY_DAYS="${OLD_ACCESS_KEY_DAYS:-90}"
mkdir -p "$REPORTS_DIR"

aws_json() {
  aws --region "$REGION" "$@" --output json 2>/dev/null || true
}

echo "Starting AWS security audit..."

IDENTITY="$(aws_json sts get-caller-identity)"
if [ -z "$IDENTITY" ]; then
  echo "AWS identity check failed. Configure AWS CLI first."
  exit 1
fi

ACCOUNT_ID="$(python -c "import json,sys; print(json.load(sys.stdin)['Account'])" <<< "$IDENTITY")"
USERS="$(aws_json iam list-users)"
PASSWORD_POLICY="$(aws_json iam get-account-password-policy)"
TRAILS="$(aws_json cloudtrail describe-trails)"
SECURITY_GROUPS="$(aws_json ec2 describe-security-groups)"
BUCKETS="$(aws_json s3api list-buckets)"
BUDGETS="$(aws_json budgets describe-budgets --account-id "$ACCOUNT_ID")"

python "$PROJECT_ROOT/scripts/render-bash-report.py" \
  --identity "$IDENTITY" \
  --users "$USERS" \
  --password-policy "$PASSWORD_POLICY" \
  --trails "$TRAILS" \
  --security-groups "$SECURITY_GROUPS" \
  --buckets "$BUCKETS" \
  --budgets "$BUDGETS" \
  --region "$REGION" \
  --old-access-key-days "$OLD_ACCESS_KEY_DAYS" \
  --output-json "$REPORTS_DIR/audit-report.json" \
  --output-md "$REPORTS_DIR/audit-report.md"

echo "Audit complete."
echo "JSON report: $REPORTS_DIR/audit-report.json"
echo "Markdown report: $REPORTS_DIR/audit-report.md"
