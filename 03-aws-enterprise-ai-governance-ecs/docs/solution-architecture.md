# Solution Architecture

## Customer Scenario

A customer wants to let product teams build AI features without every team creating its own uncontrolled model integration. The organization needs a shared AI access layer that can support approved use cases, enforce governance controls, store audit evidence, and give platform teams operational visibility.

## Business Outcomes

- Reduce risk when teams adopt generative AI and custom ML.
- Centralize model access behind one governed API.
- Show auditors where prompts, model choices, guardrail decisions, and errors are tracked.
- Give platform teams monitoring and latency signals before production rollout.
- Keep the architecture flexible enough to use Bedrock managed foundation models or SageMaker-hosted custom models.

## Technical Outcomes

- API Gateway provides the public API boundary.
- API Gateway VPC Link sends traffic privately into the VPC.
- Internal ALB routes traffic to ECS tasks.
- ECS Fargate runs the AI governance gateway as a container service.
- The app can invoke Bedrock, SageMaker, or demo mode using the same API contract.
- DynamoDB records request-level audit metadata.
- CloudWatch captures container logs, ALB metrics, ECS metrics, and dashboards.
- CloudTrail stores AWS API activity in an encrypted S3 bucket.
- VPC endpoints reduce public internet dependency for AWS service access.

## Request Flow

1. Customer app sends `POST /prompt` to API Gateway.
2. API Gateway routes the request through a VPC Link.
3. Internal ALB forwards traffic to the ECS Fargate service.
4. The container creates a request ID and evaluates local policy rules.
5. Depending on `AI_PROVIDER`, the container invokes demo logic, Amazon Bedrock, or a SageMaker endpoint.
6. If Bedrock is used, the request includes the configured Bedrock Guardrail.
7. The app stores audit metadata in DynamoDB.
8. CloudWatch records structured logs and platform metrics.
9. CloudTrail stores AWS API activity in S3 for investigation and evidence.

## Production Architecture Notes

- Use AWS WAF in front of API Gateway for internet-facing workloads.
- Add JWT/OIDC authorizers for customer or workforce identity.
- Use separate AWS accounts for dev, staging, production, and centralized audit logging.
- Use KMS customer-managed keys for regulated environments.
- Use private subnets and VPC endpoints for model, audit, and logging access.
- Send CloudWatch alarms to an incident channel through SNS or an event workflow.
- Use blue/green deployments or canary release for model and prompt changes.

## Why This Is Enterprise-Ready

This architecture does not expose the container service directly. The only public surface is API Gateway. The model call is owned by a platform-controlled ECS task role. Every request has a request ID, audit record, logs, and latency measurement. This is the foundation for a customer-facing AI platform discussion.
