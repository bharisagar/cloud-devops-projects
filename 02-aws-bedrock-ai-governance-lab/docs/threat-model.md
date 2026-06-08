# Threat Model

## Assets

- User prompts and model responses.
- Bedrock guardrail configuration.
- AI audit records in DynamoDB.
- Model invocation logs in S3 and CloudWatch Logs.
- IAM roles and deployment permissions.

## Main Risks

| Risk | Example | Control |
| --- | --- | --- |
| Prompt injection | User asks model to ignore policy | Bedrock Guardrails, application validation, test prompts |
| Sensitive data exposure | Prompt contains PII | Guardrail sensitive information policy, audit preview limits |
| Unsafe response | Model returns harmful content | Output guardrail evaluation |
| Excessive permissions | Lambda can manage unrelated AWS services | Least-privilege IAM role |
| Missing audit trail | Team cannot investigate AI behavior | DynamoDB audit table, CloudWatch Logs, CloudTrail |
| Evidence leakage | Logs are public or unencrypted | S3 block public access, encryption, IAM controls |

## Security Assumptions

- The AWS account is a personal sandbox account.
- No production, customer, or confidential data is submitted to the test API.
- Screenshots are sanitized before being published.
