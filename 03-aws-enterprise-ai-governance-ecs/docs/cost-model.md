# Cost Model

This document explains how to estimate cost for the ECS AI governance platform. Exact prices change by region and date, so use the AWS Pricing Calculator before a customer proposal.

## Main Cost Drivers

| Component | Cost Driver | Notes |
| --- | --- | --- |
| API Gateway HTTP API | Number of API calls and data transfer | Good fit for lightweight HTTP APIs. |
| API Gateway VPC Link | Hourly VPC Link and data processing charges | Required for private ECS integration. |
| ECS Fargate | vCPU, memory, storage, and running duration | Charged while tasks run. |
| Internal ALB | ALB hours and LCU usage | Required in this design for private HTTP routing. |
| VPC endpoints | Hourly endpoint charge and data processing | Cost tradeoff against NAT and public internet dependency. |
| Bedrock | Input and output tokens by model | Managed foundation model cost. |
| SageMaker | Endpoint instance/serverless/batch usage | Depends heavily on inference mode and instance type. |
| DynamoDB | Write/read request units and storage | Audit table uses on-demand billing. |
| CloudWatch | Logs ingestion, storage, metrics, dashboards, alarms | Control log volume and retention. |
| CloudTrail/S3 | Trail delivery, S3 storage, requests | Evidence storage. |

## Recommended Demo Cost Approach

For a sandbox demo:

- Use `AI_PROVIDER=demo` for the first architecture walkthrough.
- Keep ECS desired count at `1`.
- Keep CloudWatch retention at `14` days.
- Keep Bedrock invocation logging disabled until evidence capture is needed.
- Use an AWS Budget notification.
- Destroy resources after screenshots and demo testing.

## Bedrock Cost Thinking

Bedrock cost is mostly token-based for on-demand model usage. Estimate:

```text
monthly_bedrock_cost =
  (monthly_input_tokens / 1,000,000 * input_price_per_1m_tokens)
  + (monthly_output_tokens / 1,000,000 * output_price_per_1m_tokens)
```

Architectural recommendation:

- Use a low-cost model for classification, routing, simple Q&A, and demos.
- Use a stronger model only for complex reasoning.
- Keep max output tokens controlled.
- Use guardrails and prompt templates to reduce unnecessary tokens.
- Consider batch inference for non-real-time workloads where supported.

## SageMaker Cost Thinking

SageMaker inference cost depends on the deployment mode:

| Mode | Use When | Cost Behavior |
| --- | --- | --- |
| Real-time endpoint | Always-on low-latency custom model | Pay for endpoint instances while running |
| Serverless inference | Intermittent traffic | Pay for compute used by request, with optional provisioned concurrency |
| Asynchronous inference | Large payloads or longer processing | Pay for selected instances while processing queued work |
| Batch Transform | Offline prediction jobs | Pay for instance duration during the batch job |

Architectural recommendation:

- Use serverless inference for early pilots with uneven traffic.
- Use real-time endpoints for predictable production latency.
- Use batch transform for non-interactive jobs.
- Use Inference Recommender before choosing production instance types.
- Use Model Monitor when model quality and drift matter.

## ECS Platform Cost Thinking

Fargate cost is driven by task size and running time:

```text
monthly_fargate_cost =
  task_count * hours_per_month *
  ((vcpu_count * vcpu_hour_price) + (memory_gb * gb_hour_price))
```

For production:

- Start with 0.5 vCPU and 1 GB for the gateway.
- Increase only if CPU, memory, or concurrency metrics prove it is needed.
- Use autoscaling for traffic spikes.
- Consider ECS on EC2 only when workload is steady and cost optimization justifies extra operations.

## Manager-Level Cost Message

The model is only one part of the cost. For enterprise AI governance, platform cost includes API management, private networking, container runtime, monitoring, audit logs, and security evidence. The right discussion is not "Which model is cheapest?" It is "Which model and platform pattern meets the use case latency, risk, and audit requirements at acceptable cost?"

## Pricing References

- AWS Fargate pricing
- Amazon API Gateway pricing
- Amazon SageMaker pricing
- Amazon Bedrock pricing

Verify all numbers in the customer target region before final proposal.
