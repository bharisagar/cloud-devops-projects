# Security, Monitoring, and Latency

## Security Controls

| Layer | Control | Implementation |
| --- | --- | --- |
| API boundary | Managed public endpoint | API Gateway HTTP API |
| Private application | No public ECS task IP | ECS service runs in private subnets |
| Private integration | API Gateway does not call public container endpoint | API Gateway VPC Link to internal ALB |
| Runtime identity | Least privilege | ECS task role allows only Bedrock, SageMaker invoke, and DynamoDB audit writes |
| Audit storage | Encrypted evidence bucket | S3 encryption, public access block, CloudTrail delivery |
| Request audit | Application metadata | DynamoDB record per request |
| Prompt governance | Policy controls | App policy plus Bedrock Guardrails |
| Network egress | Reduced internet dependency | VPC endpoints for AWS services |

## Monitoring Signals

| Signal | Source | Why It Matters |
| --- | --- | --- |
| API status codes | API Gateway, ALB | Detect client errors and service failures |
| Target response time | ALB | Measures app and model path latency |
| ECS CPU/memory | ECS/Container Insights | Detect scaling or sizing problems |
| Application logs | CloudWatch Logs | Request ID, tenant, provider, action, latency |
| Bedrock throttling | App logs and error responses | Detect quota or model capacity issue |
| Guardrail interventions | App audit and Bedrock traces | Show governance controls working |
| DynamoDB writes | DynamoDB metrics | Confirm audit records are being stored |
| CloudTrail events | CloudTrail/S3 | Investigate AWS API changes and access |

## Latency Budget

Use a latency budget before discussing tools. Example:

| Segment | Target |
| --- | ---: |
| API Gateway routing | 20-80 ms |
| VPC Link and ALB | 20-100 ms |
| ECS app processing | 10-80 ms |
| Bedrock or SageMaker inference | 500 ms to 8 sec depending on model and output size |
| Audit write | 10-50 ms |
| Total target for simple prompts | 1-5 sec |

## Latency Improvement Options

- Keep prompts and responses small.
- Choose a smaller model for simple requests.
- Use intelligent routing for simple vs complex prompts.
- Scale ECS tasks before peak demo traffic.
- Use SageMaker provisioned concurrency or real-time endpoints when predictable low latency is required.
- Use asynchronous inference when the business process does not need an immediate response.
- Track latency by provider, model, use case, and tenant.

## Alarms Included

- ALB target latency over threshold.
- ALB target 5xx count.
- ECS CPU utilization.

## Production Additions

- API Gateway WAF and rate limits.
- CloudWatch log metric filters for `governance_action=blocked`.
- Dashboards for blocked requests by use case.
- Alert on Bedrock throttling and SageMaker endpoint failures.
- Centralized logs in a security/audit account.
