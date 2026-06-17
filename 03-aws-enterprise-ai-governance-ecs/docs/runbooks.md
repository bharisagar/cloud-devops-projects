# Operational Runbooks

These runbooks make the project usable as an organization reference, not just a demo.

## Governance Rule Change Process

Rule source:

```text
app/policies/governance-rules.json
```

Change workflow:

1. Add or update a rule with `name`, `description`, `action`, and `pattern`.
2. Add a matching test case in `tests/run_governance_tests.py`.
3. Run the local gateway in `AI_PROVIDER=demo` and `APP_POLICY_MODE=enforce`.
4. Run `python tests/run_governance_tests.py --endpoint http://127.0.0.1:8080`.
5. Review the result in the browser console and confirm the request ID is visible.
6. Build and push a new container image.
7. Deploy through Terraform or the approved CI/CD path.
8. Capture evidence in CloudWatch logs, DynamoDB audit records, and screenshots.

Production configuration options:

- bundled file: `app/policies/governance-rules.json`
- managed S3 object: `governance_rules_s3_uri`
- Terraform-published S3 object: `publish_governance_rules_to_s3 = true`

Rule action guidance:

- `block`: always blocks the prompt. Use for credentials, secrets, PII, and clearly prohibited requests.
- `monitor`: allows the response path but records the governance match. Use only for low-risk discovery.
- `policy_mode`: follows `APP_POLICY_MODE`; use for rules that may start in monitor mode before enforcement.

Rule metadata guidance:

- `responsible_ai_dimensions`: maps the rule to AWS Responsible AI dimensions.
- `guardrail_policy_types`: maps the rule to Amazon Bedrock Guardrails policy families.
- `human_review_required`: marks events that need a person to review the request.
- `reviewer_route`: identifies the security, privacy, compliance, or AI platform owner route.

## Runbook: Human Review Required

Trigger:

- API response or audit record shows `human_review_required=true`
- CloudWatch structured log includes `reviewer_route`

Impact:

- A request matched a sensitive, security, privacy, or regulated workflow that should not be handled only by automation.

Checks:

```powershell
aws logs tail /aws/ecs/enterprise-ai-governance-ecs --since 30m
aws dynamodb scan --table-name enterprise-ai-governance-ecs-audit --limit 20
```

Actions:

- Use `request_id` to locate the audit record.
- Confirm `policy_stage` to understand whether the user prompt or model output triggered the review.
- Route by `reviewer_route`:
  - `security-incident`: security operations or cloud security.
  - `privacy-review`: privacy, data protection, or security owner.
  - `risk-and-compliance`: legal, risk, compliance, or business owner.
  - `ai-platform-security`: AI platform or model safety owner.
- Review only redacted previews in normal operational channels.
- If full payload review is required, use the approved privacy/security access path and record approval.
- Update governance rules or Bedrock Guardrails if this was a missed or noisy classification.

Evidence:

- `request_id`
- `policy_rule`
- `policy_stage`
- responsible AI dimensions
- Bedrock Guardrails policy types
- reviewer route
- reviewer decision
- follow-up ticket or incident link

## Runbook: Prompt Injection Spike

Trigger:

- CloudWatch alarm `enterprise-ai-governance-ecs-blocked-prompt-spike`
- Dashboard shows `BlockedPrompts` above the normal baseline

Impact:

- Users or automated clients may be testing jailbreaks, prompt extraction, or unsafe instructions.

Checks:

```powershell
aws logs tail /aws/ecs/enterprise-ai-governance-ecs --since 30m
aws dynamodb scan --table-name enterprise-ai-governance-ecs-audit --limit 20
```

Actions:

- Filter audit records by `policy_rule=prompt_injection`.
- Identify `tenant_id`, `user_id`, and `use_case`.
- Confirm whether the source is expected security testing.
- If unexpected, rate-limit or block the caller at API Gateway/WAF.
- Review prompt examples and update policy rules or Bedrock Guardrails if needed.

Escalation:

- Security team if prompt volume is malicious or tied to external traffic.
- Application owner if the source is an internal integration.

Evidence:

- Request IDs
- CloudWatch log query result
- DynamoDB audit records
- Guardrail configuration version

## Runbook: Sensitive Data Detected

Trigger:

- Chat console or audit record shows `policy_rule=sensitive_identifier`
- CloudWatch logs show blocked requests with sensitive input indicators

Impact:

- Users may be submitting PII, payment identifiers, secrets, or regulated data.

Checks:

```powershell
aws logs tail /aws/ecs/enterprise-ai-governance-ecs --since 15m
```

Actions:

- Use request ID to find the audit event.
- Confirm whether the data was blocked before model invocation.
- Verify prompt previews are truncated and do not expose full sensitive values.
- Notify the data owner if the source is a real business workflow.
- Update user guidance or input validation if accidental PII submission is common.

Escalation:

- Privacy/security team for real PII exposure.
- Product owner if the use case requires a revised data handling policy.

Evidence:

- `request_id`
- `policy_rule`
- `governance_action`
- timestamp
- tenant and use case

## Runbook: Credential Exfiltration Attempt

Trigger:

- Chat console or audit record shows `policy_rule=credential_exfiltration`
- CloudWatch logs show users asking for AWS keys, API keys, tokens, passwords, or private keys

Impact:

- A user or integration may be attempting to retrieve secrets from the AI system.

Checks:

```powershell
aws logs tail /aws/ecs/enterprise-ai-governance-ecs --since 15m
```

Actions:

- Use request ID to find the audit event.
- Confirm the gateway returned `governance_action=blocked`.
- Check whether the request came from an expected red-team/security test.
- If unexpected, identify `tenant_id`, `user_id`, source IP through API Gateway/ALB logs, and use case.
- Rotate any potentially exposed credentials if logs or downstream systems show actual secret disclosure.
- Review Secrets Manager/IAM access and confirm the chatbot runtime cannot read broad secret paths.

Escalation:

- Security team for unexpected credential-seeking behavior.
- Cloud platform team if IAM or secret access boundaries need tightening.

Evidence:

- `request_id`
- `policy_rule=credential_exfiltration`
- CloudWatch log event
- IAM task role policy

## Runbook: Bedrock Invocation Failure

Trigger:

- `prompt_failed` events in CloudWatch
- HTTP 500 from `/prompt`
- CloudWatch `FailedPrompts` metric increases

Impact:

- Chatbot may be unavailable or degraded.

Checks:

```powershell
aws logs tail /aws/ecs/enterprise-ai-governance-ecs --since 30m
aws bedrock list-foundation-models --region ap-south-1
```

Actions:

- Check error code in the structured log.
- For throttling, confirm quota and retry behavior.
- For access errors, check ECS task role permission for `bedrock:InvokeModel` and `bedrock:Converse`.
- For guardrail errors, confirm `BEDROCK_GUARDRAIL_ID` and version.
- Temporarily switch non-production environments to `AI_PROVIDER=demo` only for demo continuity.

Escalation:

- Cloud platform team for IAM/networking.
- AWS support for quota or regional model availability issues.

Evidence:

- CloudWatch error event
- request ID
- model ID
- ECS task role policy

## Runbook: Audit Records Missing

Trigger:

- Chat console shows `audit_status=cloudwatch_only` in AWS when DynamoDB is expected
- DynamoDB table has no record for a known request ID

Impact:

- Governance evidence is incomplete.

Checks:

```powershell
aws ecs describe-task-definition --task-definition enterprise-ai-governance-ecs
aws dynamodb describe-table --table-name enterprise-ai-governance-ecs-audit
```

Actions:

- Confirm `AUDIT_TABLE_NAME` is set in the ECS task definition.
- Confirm ECS task role can call `dynamodb:PutItem`.
- Check DynamoDB table status and key schema.
- Search CloudWatch for `audit_skipped`.
- Redeploy the task definition if environment variables are missing.

Escalation:

- Platform team if IAM or Terraform drift caused the issue.

Evidence:

- ECS task definition revision
- IAM policy
- CloudWatch `audit_skipped` event

## Runbook: High Latency

Trigger:

- ALB target response time alarm
- Dashboard shows slow `latency_ms`
- Users report slow chatbot responses

Impact:

- User experience and automation workflows are degraded.

Checks:

```powershell
aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB --metric-name TargetResponseTime --statistics Average --period 60 --start-time <start> --end-time <end>
aws logs tail /aws/ecs/enterprise-ai-governance-ecs --since 30m
```

Actions:

- Compare app `latency_ms` with ALB target response time.
- Check whether model latency or ECS CPU/memory is the bottleneck.
- Route simple prompts to Nova Lite or demo provider for non-production demos.
- Increase ECS desired count before known demos.
- Reduce prompt and response size where possible.

Escalation:

- Platform team for ECS scaling.
- AI platform owner for model/provider latency.

Evidence:

- CloudWatch dashboard screenshot
- request IDs with high `latency_ms`
- ECS CPU/memory metrics

## Runbook: Cost Spike

Trigger:

- AWS Budget alert
- Unexpected model invocation volume
- Bedrock or SageMaker spend exceeds baseline

Impact:

- Sandbox or production budget risk.

Checks:

```powershell
aws budgets describe-budgets --account-id <account_id>
aws logs tail /aws/ecs/enterprise-ai-governance-ecs --since 24h
```

Actions:

- Check prompt volume by tenant and use case.
- Verify demo traffic is not hitting expensive models.
- Use Nova Lite for simple prompts.
- Stop unused SageMaker endpoints.
- Destroy sandbox resources after demos.

Escalation:

- Finance/platform owner if spend crosses approved threshold.

Evidence:

- Budget alert
- CloudWatch request count
- model/provider configuration
