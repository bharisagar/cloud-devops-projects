# Architecture Notes

This project uses a serverless architecture so the governance controls are easy to understand and inexpensive to test in a sandbox AWS account.

## Request Path

1. API Gateway receives the user prompt.
2. Lambda validates the payload and prepares the Bedrock request.
3. Lambda invokes Amazon Bedrock with a guardrail identifier and version.
4. Bedrock Guardrails evaluate the input.
5. The approved foundation model generates a response only when the input passes policy evaluation.
6. Bedrock Guardrails evaluate the output.
7. Lambda stores an audit record in DynamoDB and returns the governed response.

## Audit Path

- Lambda logs application behavior to CloudWatch Logs.
- Lambda writes one structured audit item per request to DynamoDB.
- Bedrock model invocation logging sends invocation records to S3 and CloudWatch Logs.
- CloudTrail records AWS API activity for governance review.

## Why This Architecture Works

It keeps the application small while showing the controls that matter in real GenAI systems: access control, policy enforcement, logging, traceability, and cleanup.
