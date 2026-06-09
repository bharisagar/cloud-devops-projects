# Demo Script

## Demo Title

Enterprise AI Governance Platform on AWS using ECS, API Gateway, Bedrock, and SageMaker-ready provider design.

## Opening

"This demo shows how an organization can expose AI capabilities through a governed platform layer instead of allowing every team to call models directly."

## Walkthrough

### 1. Architecture

Show the architecture diagram.

Message:

"API Gateway is the public boundary. The AI application runs privately on ECS Fargate. API Gateway reaches it through VPC Link and an internal ALB. The app records audit metadata and can call Bedrock or SageMaker using a controlled task role."

### 2. Security

Show Terraform IAM, private subnet, and VPC endpoint files.

Message:

"The ECS task has a dedicated role. It can write audit records and invoke approved AI backends. The service is not public. AWS service access goes through VPC endpoints."

### 3. Governance

Run:

```bash
python tests/run_governance_tests.py --endpoint <api_endpoint>
```

Message:

"Safe prompts are allowed. Prompt injection and restricted advice are monitored or blocked based on policy mode. Every request gets a request ID."

### 4. Audit Evidence

Show DynamoDB audit records.

Message:

"This gives security and audit teams traceability: request ID, tenant, use case, provider, policy rule, action, stop reason, and latency."

### 5. Monitoring

Show CloudWatch dashboard and logs.

Message:

"Operations teams can monitor latency, 5xx errors, ECS CPU and memory, and structured application logs."

### 6. Bedrock vs SageMaker

Show `AI_PROVIDER` variable.

Message:

"The same enterprise gateway can route to Bedrock for managed foundation models or SageMaker for custom models. That keeps customer access, audit, and monitoring consistent."

## Close

"The architecture is not just an AI demo. It is a governed AI platform pattern that helps customers adopt AI with security, auditability, cost control, latency monitoring, and a clear production path."
