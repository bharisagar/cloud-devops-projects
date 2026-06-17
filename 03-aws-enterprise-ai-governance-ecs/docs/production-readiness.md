# Production Readiness Guide

This project is now structured as a production reference architecture. Before using it for real organization traffic, complete this checklist.

## Production Architecture Position

The production pattern is:

```text
Authenticated user or application
  -> API Gateway with JWT authorizer
  -> AWS WAF rate limiting and managed protections
  -> private VPC Link
  -> internal ALB
  -> ECS Fargate governance gateway
  -> app policy rules from governed config
  -> Bedrock Guardrails and approved model provider
  -> DynamoDB audit record with redacted previews
  -> CloudWatch metrics, logs, alarms, dashboard
  -> CloudTrail and S3 evidence
```

## AWS Reference Alignment

This production pattern is intentionally mapped to official AWS guidance:

- [AWS Responsible AI](https://aws.amazon.com/ai/responsible-ai/) for responsible AI dimensions such as privacy and security, safety, controllability, governance, explainability, robustness, and transparency.
- [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) for configurable safeguards, sensitive information filters, denied topics, contextual grounding, automated reasoning, and guardrail versioning.
- [Amazon Bedrock Evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) for automatic evaluation, human evaluation, LLM-as-judge, and RAG quality checks.
- [Bedrock model invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) for CloudWatch Logs and S3 model invocation records.
- [Bedrock CloudTrail logging](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html) for API audit events and caller identity.

See [AWS governance references](./aws-governance-references.md) for the full mapping.

## What AWS Guidance Means For This Project

For organization adoption, implement governance across the full AI lifecycle:

- Define the use case, users, data classes, benefits, risks, and release criteria before production.
- Use application policy rules for organization-specific controls and Bedrock Guardrails for model-level safeguards.
- Evaluate both user input and model output before returning a response.
- Redact sensitive previews before audit storage.
- Keep caller, request, policy, model, and reviewer metadata searchable through CloudWatch and DynamoDB.
- Enable Bedrock invocation logging only after privacy, retention, and access-review approval.
- Use CloudTrail and an S3 evidence bucket for AWS API auditability.
- Run automated and human evaluations for high-risk use cases.
- Route sensitive, regulated, or security-relevant events to human review.
- Maintain post-release monitoring, incident runbooks, and decommissioning criteria.

## Required Production Settings

Recommended Terraform settings:

```hcl
environment = "prod"

ai_provider     = "bedrock"
app_policy_mode = "enforce"

enable_jwt_authorizer = true
jwt_issuer            = "https://cognito-idp.<region>.amazonaws.com/<user_pool_id>"
jwt_audience          = ["<app_client_id>"]

enable_waf     = true
waf_rate_limit = 1000

publish_governance_rules_to_s3 = true
governance_policy_version      = "2026-06-16-production-baseline"

alarm_email       = "platform-alerts@example.com"
budget_alert_email = "cloud-finance@example.com"
```

If the organization already has a central policy bucket, use:

```hcl
governance_rules_s3_uri = "s3://central-policy-bucket/ai-governance/governance-rules.json"
```

Then update the ECS task role with `s3:GetObject` access to that object.

## Policy Change Control

Production rules should not be edited directly in the AWS console.

Use this flow:

1. Open a pull request changing `app/policies/governance-rules.json` or the central policy repo.
2. Add or update `tests/run_governance_tests.py`.
3. Run local tests in demo mode.
4. Run Terraform validation.
5. Get platform/security approval.
6. Publish the policy object or deploy the new container.
7. Capture evidence: request IDs, CloudWatch logs, DynamoDB audit records, dashboard screenshot.

Each rule must also include responsible AI dimensions, Bedrock Guardrails policy mappings, and human-review routing where appropriate. See [production governance policy](./production-governance-policy.md).

## Logging And Redaction

The gateway stores prompt and answer previews only after redaction. Current redaction covers:

- AWS access key IDs
- SSNs
- payment-card-like numbers
- email addresses
- common secret assignment patterns

Production teams should extend `REDACTION_PATTERNS` and governance rules for their regulated data types before onboarding sensitive use cases.

## Monitoring And Alerting

CloudWatch includes:

- total prompt requests
- blocked prompts
- failed prompts
- critical policy blocks
- human review required events
- ALB latency
- ALB 5xx
- ECS CPU and memory
- latest governed request log query

Critical policy blocks should alert immediately because they include secrets and sensitive identifier events.

## Identity And Access

Production traffic must use one of:

- API Gateway JWT authorizer with Cognito/OIDC
- private API pattern with internal network access
- enterprise API gateway in front of this API

Do not expose `/prompt` publicly without identity, rate limiting, and abuse controls.

## Bedrock Guardrails

The app policy layer is not a replacement for Bedrock Guardrails.

Use both:

- app rules for company-specific controls such as credentials, internal data handling, and tenant policy
- Bedrock Guardrails for model-level safety controls, denied topics, sensitive information handling, and model response checks

## Audit Evidence

For every high-risk request, capture:

- `request_id`
- `tenant_id`
- `user_id`
- `use_case`
- `policy_version`
- `policy_rule`
- `policy_stage`
- `rule_category`
- `rule_severity`
- responsible AI dimensions
- Bedrock Guardrails policy types
- human review requirement
- reviewer route
- `governance_action`
- `latency_ms`
- redaction status
- CloudWatch log event
- DynamoDB audit record

## Release Gate

Do not promote to production unless all pass:

```powershell
python -m py_compile app\main.py tests\run_governance_tests.py
python .\tests\run_governance_tests.py --endpoint http://127.0.0.1:8080
terraform fmt -check
terraform validate
```

## Known Enterprise Extensions

For a larger organization, add:

- centralized SIEM forwarding
- AppConfig deployment strategy for policy rollout
- approval queue for high-risk prompts
- tenant-specific policies
- model routing by risk level
- full CI/CD workflow with image signing and vulnerability scanning
- cross-account CloudTrail and audit log archive
