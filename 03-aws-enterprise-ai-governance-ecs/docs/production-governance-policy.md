# Production AI Governance Policy

This policy describes how the gateway implements AWS-aligned AI governance controls for organization use.

## AWS-Aligned Control Model

AWS guidance separates AI governance into responsible design, runtime safeguards, logging, evaluation, and post-release operations. This project implements those layers as follows:

| AWS guidance area | Production control in this project |
| --- | --- |
| Responsible AI dimensions | Every governance rule can declare `responsible_ai_dimensions`, such as privacy and security, safety, controllability, robustness, transparency, and governance. |
| Bedrock Guardrails | Every rule can declare `guardrail_policy_types`, mapping local controls to content filters, denied topics, word filters, sensitive information filters, prompt attack filters, contextual grounding, or automated reasoning. |
| Input and output safeguards | The gateway evaluates the user prompt before model invocation and evaluates the model answer before returning it to the caller. |
| Sensitive data handling | Prompt and answer previews are redacted before they are written to audit records or logs. |
| Human review | Rules can declare `human_review_required` and `reviewer_route` for security, privacy, or compliance escalation. |
| Auditability | Every request returns a `request_id` and writes structured evidence fields to DynamoDB or CloudWatch. |
| Invocation logging | Terraform can enable Bedrock model invocation logging to CloudWatch Logs and S3 after privacy and retention approval. |
| CloudTrail | Terraform creates an evidence bucket and CloudTrail trail for AWS API activity. |
| Continuous evaluation | Automated gateway tests are included; production should add Bedrock Evaluations and human review for high-risk use cases. |

## Governance Rule Contract

Each production rule must include:

```json
{
  "name": "stable_rule_id",
  "description": "Business-readable rule purpose.",
  "action": "block | monitor | policy_mode",
  "category": "secrets | data_protection | model_safety | misconduct | regulated_advice",
  "severity": "low | medium | high | critical",
  "responsible_ai_dimensions": ["privacy_and_security", "safety", "governance"],
  "guardrail_policy_types": ["sensitive_information_filters"],
  "human_review_required": true,
  "reviewer_route": "security-incident",
  "pattern": "case-insensitive regular expression"
}
```

Use `block` for credentials, secrets, PII, cyber abuse, and clearly prohibited content. Use `policy_mode` for rules that may start in monitoring and later move to enforcement. Use `monitor` only for low-risk discovery and tuning.

## Runtime Decision Fields

Every `/prompt` response includes fields that can be shown in the console or searched in logs:

- `request_id`
- `governance_action`
- `policy_rule`
- `policy_action`
- `policy_stage`
- `policy_version`
- `rule_category`
- `rule_severity`
- `responsible_ai_dimensions`
- `guardrail_policy_types`
- `human_review_required`
- `reviewer_route`
- `redaction_applied`
- `audit_status`
- `monitoring_stream`
- `evidence_lookup`

`policy_stage=input` means the user prompt triggered the policy. `policy_stage=output` means the model response triggered the policy and was stopped before returning to the user.

## Human Review Routing

Production teams should connect `human_review_required=true` events to an organization workflow:

| Reviewer route | Typical owner | Examples |
| --- | --- | --- |
| `security-incident` | Security operations or cloud security | credential retrieval, malware, phishing, exploitation |
| `privacy-review` | Privacy, data protection, or security | SSNs, payment identifiers, regulated personal data |
| `risk-and-compliance` | Legal, risk, compliance, or domain owner | legal, medical, financial, or regulated workflow advice |
| `ai-platform-security` | AI platform team | prompt injection, jailbreak attempts, prompt extraction |

For this reference project, the routing is captured in audit evidence. A production organization can forward these events to Jira, ServiceNow, Slack, Security Hub, EventBridge, or a custom approval queue.

## Release Gates

Before promoting a policy or model change:

1. Confirm the use case, users, data classes, and expected behavior.
2. Review the Responsible AI dimensions affected by the change.
3. Update `app/policies/governance-rules.json`.
4. Add or update tests in `tests/run_governance_tests.py`.
5. Run application tests and Terraform validation.
6. Review Bedrock Guardrail configuration and version.
7. Review model invocation logging privacy and retention impact.
8. Capture release evidence: commit, policy version, test output, Terraform output, dashboard screenshot, and sample request IDs.

## Production Maturity Notes

The repository now implements the application, policy, audit, infrastructure, and monitoring baseline. A real production rollout should still add:

- CI/CD with required security approval
- container image scanning and signing
- central SIEM forwarding
- EventBridge or ticket integration for human review
- Bedrock Evaluation jobs for model quality and RAG grounding
- tenant-specific policy overlays
- data retention approval for invocation logs
- periodic policy drift review

