# Cost Notes

This project is designed for a sandbox account, but it can still create billable resources.

Potential cost areas:

- Amazon Bedrock model invocations.
- Bedrock Guardrails evaluations.
- API Gateway requests.
- Lambda invocations and duration.
- CloudWatch Logs ingestion and retention.
- S3 storage for governance logs.
- CloudTrail storage and delivery.
- DynamoDB read/write usage.

Cost control recommendations:

- Use short test prompts.
- Keep CloudWatch log retention low for demos.
- Destroy the stack after testing.
- Avoid submitting large documents or images.
- Review the AWS Pricing Calculator for your region.
- Configure `budget_alert_email` and `monthly_budget_limit_usd` in Terraform for AWS Budget alerts.
- Use the cost governance tags in [Day 2: AI Cost Governance](./day-02-cost-governance.md) for Cost Explorer grouping.
