# Cost Model

Pricing changes over time and varies by region. The estimates below are for `ap-south-1` / Asia Pacific (Mumbai), calculated on June 9-10, 2026 from AWS Pricing API results and official AWS pricing pages. Use AWS Pricing Calculator before a real customer proposal.

## Assumptions

| Assumption | Value |
| --- | ---: |
| Region | `ap-south-1` |
| Month length | 730 hours |
| ECS service | 1 Fargate task |
| Fargate task size | 0.5 vCPU, 1 GB memory |
| Interface VPC endpoints | 5 endpoints across 2 AZs |
| API usage | 10,000 requests/month |
| Average model input | 1,500 tokens/request |
| Average model output | 500 tokens/request |
| Monthly input tokens | 15M |
| Monthly output tokens | 5M |
| CloudWatch log ingestion | 1 GB/month |
| CloudWatch log storage | 1 GB/month |
| DynamoDB audit writes | 10,000 writes/month |
| S3 evidence storage | 1 GB/month |

## Selected Model Costs

| Provider | Model | Unit Price | Monthly Estimate |
| --- | --- | ---: | ---: |
| Bedrock | Amazon Nova Pro | $0.80/1M input, $3.20/1M output | $28.00 |
| Bedrock | Amazon Nova Lite | $0.06/1M input, $0.24/1M output | $2.10 |
| Bedrock | Claude Sonnet 4.6 | $3.00/1M input, $15.00/1M output | $120.00 |
| SageMaker | Custom smoke endpoint on `ml.m5.large` | $0.121/hour | $88.33/month |
| SageMaker | Gemma 3 1B Instruct on `ml.g5.2xlarge` | $1.819/hour | $1,327.87/month |
| SageMaker | Llama3 8B SEA-Lion v2.1 Instruct on `ml.g5.4xlarge` | $2.438/hour | $1,779.74/month |

Bedrock calculation:

```text
Nova Pro = (15 * 0.80) + (5 * 3.20) = $28.00/month
Nova Lite = (15 * 0.06) + (5 * 0.24) = $2.10/month
Claude Sonnet 4.6 = (15 * 3.00) + (5 * 15.00) = $120.00/month
```

SageMaker calculation:

```text
Smoke endpoint = 1 ml.m5.large endpoint * 730 hours * $0.121/hour = $88.33/month
Gemma 3 1B = 1 ml.g5.2xlarge endpoint * 730 hours * $1.819/hour = $1,327.87/month
Llama3 8B SEA-Lion = 1 ml.g5.4xlarge endpoint * 730 hours * $2.438/hour = $1,779.74/month
```

This is why the project defaults to Bedrock for the managed GenAI path and keeps SageMaker as an optional custom-model path. In the tested account, `ml.g5.2xlarge` and `ml.g5.4xlarge` endpoint quota was `0`, so the practical SageMaker evidence path used the `ml.m5.large` smoke endpoint.

## Bedrock Guardrails Cost

This project configures:

- Content filters: $0.15 per 1,000 text units.
- Denied topics: $0.15 per 1,000 text units.
- Sensitive information filters: $0.10 per 1,000 text units.

A text unit is up to 1,000 characters. For a planning estimate, assume each request processes about 8 text units across input and output.

```text
guardrail_cost_per_1k_text_units = 0.15 + 0.15 + 0.10 = $0.40
monthly_text_units = 10,000 requests * 8 = 80,000
monthly_guardrails_cost = 80,000 / 1,000 * 0.40 = $32.00
```

Actual guardrail cost depends on prompt size, response size, enabled filters, and whether blocked requests are stopped by application policy before model invocation.

## Platform Infrastructure Estimate

| Service | Unit Price Used | Monthly Estimate |
| --- | ---: | ---: |
| ECS Fargate | $0.04256/vCPU-hour + $0.004655/GB-hour | $18.93 |
| Internal Application Load Balancer | $0.0239/hour + 1 LCU at $0.008/hour | $23.29 |
| API Gateway HTTP API | $1.05 per 1M requests | $0.01 |
| Interface VPC endpoints | 5 endpoints * 2 AZs * $0.013/hour | $94.90 |
| VPC endpoint data processing | $0.01/GB, assuming 1 GB | $0.01 |
| DynamoDB on-demand writes | $0.71 per 1M write request units | $0.01 |
| DynamoDB storage | First 25 GB free, then $0.285/GB-month | $0.00 |
| CloudWatch Logs ingestion | $0.67/GB | $0.67 |
| CloudWatch Logs storage | $0.03/GB-month | $0.03 |
| CloudWatch dashboard and alarms | 1 dashboard and 3 standard alarms estimate | $3.30 |
| S3 evidence storage | $0.025/GB-month for first 50 TB | $0.03 |
| CloudTrail management events | One management event trail estimate | $0.00 |
| ECR image storage | Small image estimate | $0.03 |

Estimated platform cost without model calls:

```text
$18.93 + $23.29 + $0.01 + $94.90 + $0.01 + $0.01
+ $0.00 + $0.67 + $0.03 + $3.30 + $0.03 + $0.00 + $0.03
= $141.21/month
```

## Monthly Total Scenarios

| Scenario | Includes | Estimated Monthly Cost |
| --- | --- | ---: |
| Platform only | ECS, ALB, API Gateway, VPC endpoints, logs, audit, evidence | $141.21 |
| Platform + Nova Lite + Guardrails | Cost-optimized GenAI path | $175.31 |
| Platform + Nova Pro + Guardrails | Recommended Bedrock production baseline | $201.21 |
| Platform + Claude Sonnet 4.6 + Guardrails | Advanced long-context/reasoning path | $293.21 |
| Platform + SageMaker smoke endpoint | Runtime evidence path, one `ml.m5.large` endpoint | $229.54 |
| Platform + SageMaker Gemma 3 1B endpoint | Custom LLM path, one `ml.g5.2xlarge` endpoint | $1,469.08 |
| Platform + SageMaker Llama3 8B endpoint | Stronger Llama-class path, one `ml.g5.4xlarge` endpoint | $1,920.95 |

## Short Demo Estimate

For an 8-hour demo window with `AI_PROVIDER=demo`, 1 ECS task, 5 interface endpoints across 2 AZs, ALB, CloudWatch, and no SageMaker endpoint:

```text
Fargate: 8 * ((0.5 * 0.04256) + (1 * 0.004655)) = $0.21
ALB + 1 LCU: 8 * (0.0239 + 0.008) = $0.26
VPC endpoints: 5 * 2 * 8 * 0.013 = $1.04
Estimated 8-hour platform demo: about $2-$4 after logs/storage/API overhead
```

If Bedrock Nova Pro is tested with 100 requests averaging 1,500 input and 500 output tokens:

```text
Input: 150,000 tokens / 1M * 0.80 = $0.12
Output: 50,000 tokens / 1M * 3.20 = $0.16
Nova Pro model cost for 100 requests: about $0.28
```

Guardrails for 100 requests at 8 text units/request:

```text
100 * 8 / 1,000 * 0.40 = $0.32
```

So a controlled 8-hour Bedrock demo should stay low, but the private networking resources should still be destroyed after screenshots.

For a 30-minute SageMaker smoke test on `ml.m5.large`:

```text
0.5 hours * $0.121/hour = $0.0605
```

Delete the endpoint immediately after evidence capture. Endpoint config, model, ECR repository, and IAM role should also be removed when the smoke test is complete.

## Cost Optimization Decisions

- Use Bedrock Nova Pro as the default model path.
- Use Nova Lite for high-volume simple requests.
- Use Claude Sonnet 4.6 only for long-context or advanced reasoning.
- Use the `ml.m5.large` SageMaker smoke endpoint for low-cost runtime evidence.
- Request GPU endpoint quota before deploying JumpStart LLMs.
- Do not leave SageMaker endpoints running after testing.
- Keep `desired_count = 1` for sandbox.
- Keep log retention short in sandbox.
- Turn on Bedrock invocation logging only when evidence capture is required.
- Destroy the stack after the demo.

## Pricing Sources

- AWS Pricing API queried on June 9-10, 2026 for Fargate, ALB, API Gateway, VPC endpoints, DynamoDB, CloudWatch Logs, S3, and SageMaker endpoint hosting in `ap-south-1`.
- AWS Pricing Calculator should be used again before customer sign-off: https://calculator.aws/
- Amazon Bedrock pricing: https://aws.amazon.com/bedrock/pricing/
- Amazon ECS Fargate pricing: https://aws.amazon.com/fargate/pricing/
- Amazon SageMaker AI pricing: https://aws.amazon.com/sagemaker/ai/pricing/
- Amazon API Gateway pricing: https://aws.amazon.com/api-gateway/pricing/
- Elastic Load Balancing pricing: https://aws.amazon.com/elasticloadbalancing/pricing/
- Amazon VPC pricing: https://aws.amazon.com/vpc/pricing/
- Amazon DynamoDB pricing: https://aws.amazon.com/dynamodb/pricing/
- Amazon CloudWatch pricing: https://aws.amazon.com/cloudwatch/pricing/
- Amazon S3 pricing: https://aws.amazon.com/s3/pricing/
