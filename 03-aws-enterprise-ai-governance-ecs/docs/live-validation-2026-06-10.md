# Live Validation Notes - 2026-06-10

Region: `ap-south-1` / Asia Pacific (Mumbai)

AWS profile used: `bedrock-governance`

## ECS Platform Validation

Deployed the ECS version of the governed AI gateway and validated the full application path:

- API Gateway endpoint: `https://fbdettqx12.execute-api.ap-south-1.amazonaws.com/`
- ECS cluster: `enterprise-ai-governance-ecs`
- ECS service: `enterprise-ai-governance-ecs`
- ECR image: `909969506392.dkr.ecr.ap-south-1.amazonaws.com/enterprise-ai-governance-ecs:latest`
- Bedrock Guardrail ID: `9bo7yc28tvi6`
- DynamoDB audit table: `enterprise-ai-governance-ecs-audit`
- CloudWatch dashboard: `enterprise-ai-governance-ecs-dashboard`

Health and routing checks:

```json
{
  "service": "enterprise-ai-governance-ecs",
  "status": "healthy",
  "region": "ap-south-1",
  "provider": "demo",
  "audit_enabled": true,
  "policy_mode": "monitor"
}
```

Governance test results:

- Safe architecture prompt returned `governance_action = allowed`.
- Prompt injection prompt returned `governance_action = monitored`.
- Restricted professional advice prompt returned `governance_action = monitored`.
- Sensitive identifier prompt returned `governance_action = monitored`.
- DynamoDB stored audit records for all test requests.
- CloudWatch Logs captured structured `prompt_completed` events.

Evidence screenshots are documented in [evidence.md](./evidence.md).

## Bedrock Runtime Check

Validated that Bedrock inference profiles are available in the account, including:

- `apac.amazon.nova-pro-v1:0`
- `apac.amazon.nova-lite-v1:0`
- `global.anthropic.claude-sonnet-4-6`

Runtime calls to Nova Pro and Nova Lite reached the account's daily token quota:

```text
ThrottlingException: Too many tokens per day, please wait before trying again.
```

This is useful evidence for the governance story because quota, retry handling, model limits, and cost control are part of production AI operations.

## SageMaker Quota Check

Checked endpoint quota before deploying a model:

| Instance type | Endpoint quota |
| --- | ---: |
| `ml.g5.xlarge` | 1 |
| `ml.g5.2xlarge` | 0 |
| `ml.g5.4xlarge` | 0 |
| `ml.m5.large` | 4 |

The checked JumpStart LLMs require larger GPU instances:

| Model | Required/default endpoint instance |
| --- | --- |
| Gemma 3 1B Instruct | `ml.g5.2xlarge` |
| Llama3 8B SEA-Lion v2.1 Instruct | `ml.g5.4xlarge` |
| Zephyr 7B Beta | `ml.g5.2xlarge` |

Because GPU quota was not available, the practical validation used the custom SageMaker smoke endpoint on `ml.m5.large`.

## SageMaker Runtime Smoke Test

Created and invoked:

- ECR repository: `enterprise-ai-governance-sagemaker-smoke`
- SageMaker model: `enterprise-ai-gov-smoke-20260610`
- SageMaker endpoint config: `enterprise-ai-gov-smoke-20260610`
- SageMaker endpoint: `enterprise-ai-gov-smoke-20260610`
- Instance type: `ml.m5.large`
- Endpoint status: `InService`

Runtime response:

```json
{
  "generated_text": "SageMaker Runtime smoke test succeeded. The governed AI gateway can route a request to a SageMaker endpoint. Prompt preview: Explain AI governance in one sentence.",
  "model": "sagemaker-smoke-custom-endpoint",
  "purpose": "low-cost endpoint integration evidence"
}
```

## Cleanup Status

Cleanup completed after validation:

- SageMaker endpoint deleted.
- SageMaker endpoint config deleted.
- SageMaker model deleted.
- Temporary IAM execution role deleted.
- ECR repository deleted.

Final checks showed no matching endpoint or ECR repository remaining.
