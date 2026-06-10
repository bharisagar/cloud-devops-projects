# Solution Walkthrough

## Title

Enterprise AI Governance Platform on AWS using ECS, API Gateway, Bedrock, and a SageMaker-ready provider design.

## Opening Context

This solution exposes AI capabilities through a governed platform layer instead of allowing each application team to call models directly.

The platform provides:

- A controlled API boundary.
- A private containerized AI gateway.
- Bedrock managed model integration.
- Optional SageMaker custom-model integration.
- Audit records for every request.
- CloudWatch monitoring and alarms.
- CloudTrail and S3 evidence storage.
- Cost visibility for model and platform choices.

## Walkthrough

### 1. Architecture

Show the architecture diagram.

Key points:

- API Gateway is the public API boundary.
- API Gateway reaches the private application through VPC Link.
- The ECS service runs in private subnets behind an internal ALB.
- The ECS task role controls access to Bedrock, SageMaker, and DynamoDB.
- Audit and monitoring are built into the request path.

### 2. Security

Show Terraform files for IAM, private subnets, security groups, and VPC endpoints.

Key points:

- The ECS task is not public.
- IAM uses a dedicated task role.
- AWS service access is private through VPC endpoints.
- DynamoDB, S3, and CloudWatch store operational evidence.
- Bedrock Guardrails evaluate unsafe prompts and sensitive data.

### 3. Model Selection

Show [Bedrock vs SageMaker](./bedrock-vs-sagemaker.md).

Key points:

- Bedrock Nova Pro is the recommended managed foundation model for this project.
- Nova Lite is the lower-cost option for simple/high-volume requests.
- Claude Sonnet 4.6 is the advanced reasoning option.
- SageMaker smoke endpoint proves SageMaker Runtime integration at low cost.
- SageMaker JumpStart LLM endpoints are the custom-model path after GPU quota approval.

### 4. Governance Test

Run:

```bash
python tests/run_governance_tests.py --endpoint <api_endpoint>
```

Expected proof:

- Safe architecture question returns an allowed response.
- Prompt injection is monitored or blocked.
- Restricted professional advice is monitored or blocked.
- Sensitive identifier input is detected.
- Each request receives a request ID.

### 5. Audit Evidence

Show DynamoDB audit records.

Evidence fields:

- `request_id`
- `tenant_id`
- `use_case`
- `provider`
- `model_id`
- `policy_rule`
- `governance_action`
- `latency_ms`
- `created_at`

### 6. Monitoring

Show CloudWatch dashboard and logs.

Operational signals:

- ALB target response time.
- ALB 5xx count.
- ECS CPU and memory.
- Structured application logs.
- Bedrock throttling or endpoint failures.
- Guardrail intervention counts from audit records.

### 7. Cost Review

Show [Cost Model](./cost-model.md).

Key points:

- 24/7 private ECS platform estimate: about `$141.21/month` before model calls.
- Bedrock Nova Pro model estimate for 10,000 requests/month: about `$28/month`.
- Bedrock Guardrails estimate for the same traffic pattern: about `$32/month`.
- SageMaker `ml.m5.large` smoke endpoint estimate: about `$0.121/hour`.
- SageMaker JumpStart LLM endpoints are materially more expensive and should be used only after quota and budget approval.

## Closing

This is a governed AI platform pattern: model access, audit evidence, security controls, monitoring, latency tracking, and cost visibility are designed together.
