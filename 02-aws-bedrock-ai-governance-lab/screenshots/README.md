# Deployment Screenshots

Use this folder for deployment screenshots and verification evidence.

Sensitive values such as account IDs, full ARNs, private URLs, and personal data should be redacted before screenshots are committed.

## Captured Evidence

Redacted deployment screenshots have been added under [`evidence/`](./evidence/).

The full screenshot gallery is documented here: [Deployment Evidence](../docs/deployment-evidence.md).

| File | Evidence |
| --- | --- |
| [`01-terraform-outputs.png`](./evidence/01-terraform-outputs.png) | Terraform outputs for the deployed stack. |
| [`02-terraform-state-list.png`](./evidence/02-terraform-state-list.png) | Terraform-managed resources before cleanup. |
| [`03-api-gateway-console.png`](./evidence/03-api-gateway-console.png) | API Gateway HTTP API in the AWS console. |
| [`04-api-gateway-route-cli.png`](./evidence/04-api-gateway-route-cli.png) | `POST /prompt` route returned by AWS CLI. |
| [`05-lambda-console.png`](./evidence/05-lambda-console.png) | Lambda application with API Gateway integration. |
| [`06-bedrock-guardrail-console.png`](./evidence/06-bedrock-guardrail-console.png) | Bedrock Guardrail overview and ready status. |
| [`07-bedrock-guardrail-cli.png`](./evidence/07-bedrock-guardrail-cli.png) | Guardrail restricted advice policy from AWS CLI. |
| [`08-governance-tests-quota-and-blocked.png`](./evidence/08-governance-tests-quota-and-blocked.png) | Governance test output with quota handling and blocked prompt injection. |
| [`09-governance-tests-restricted-advice.png`](./evidence/09-governance-tests-restricted-advice.png) | Restricted professional advice blocked by Guardrails. |
| [`10-s3-cloudtrail-evidence.png`](./evidence/10-s3-cloudtrail-evidence.png) | CloudTrail governance logs stored in S3. |

## Evidence Checklist

| File name | Evidence | Purpose |
| --- | --- | --- |
| `01-terraform-validate.png` | `terraform validate` success | Shows IaC syntax is valid. |
| `02-terraform-plan.png` | Terraform plan summary | Shows resources are planned before deployment. |
| `03-api-gateway-endpoint.png` | API Gateway route/stage | Shows the application entry point. |
| `04-lambda-function.png` | Lambda function configuration | Shows the AI application runtime. |
| `05-bedrock-guardrail.png` | Bedrock Guardrail overview | Shows governance policy exists. |
| `06-guardrail-policies.png` | Guardrail content/PII/denied-topic policies | Shows what is being controlled. |
| `07-safe-prompt-test.png` | Successful safe prompt response | Shows allowed user flow. |
| `08-blocked-prompt-test.png` | Blocked or refused unsafe prompt | Shows guardrail behavior. |
| `08a-quota-handling-test.png` | `429` Bedrock quota response if daily model tokens are exhausted | Shows operational error handling instead of a generic app failure. |
| `09-dynamodb-audit-records.png` | DynamoDB audit table items | Shows application-level traceability. |
| `10-cloudwatch-lambda-logs.png` | Lambda CloudWatch logs | Shows runtime observability. |
| `11-bedrock-invocation-logs.png` | Bedrock invocation log destination | Shows model activity logging. |
| `12-s3-governance-evidence.png` | S3 bucket with governance logs | Shows evidence storage. |
| `13-cloudtrail-events.png` | CloudTrail events for Bedrock/Lambda/IAM | Shows API auditability. |
| `14-cleanup-destroy.png` | `terraform destroy` output | Shows responsible cleanup. |
