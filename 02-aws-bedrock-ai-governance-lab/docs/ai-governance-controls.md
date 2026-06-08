# AI Governance Controls

This project maps common AI governance concerns to AWS-native services.

## 1. Access Governance

IAM policies restrict which principals can deploy resources, invoke the Lambda function, and call Amazon Bedrock. The Lambda execution role only receives the permissions needed for Bedrock inference, DynamoDB writes, CloudWatch logs, and S3 access where required.

## 2. Prompt Governance

Amazon Bedrock Guardrails evaluate user input before the foundation model is invoked. This helps block or handle unsafe content, prompt attacks, denied topics, and sensitive information based on the configured policies.

## 3. Response Governance

Guardrails also evaluate model output before the application returns it to the user. This helps reduce unsafe responses and accidental disclosure of sensitive data.

## 4. Audit Governance

DynamoDB stores request-level audit metadata such as request ID, timestamp, model ID, guardrail ID, prompt preview, response preview, latency, and status.

## 5. Logging Governance

CloudWatch Logs stores Lambda runtime logs. Amazon Bedrock model invocation logging can publish invocation records to CloudWatch Logs and S3.

## 6. Evidence Governance

S3 stores governance evidence such as Bedrock invocation logs and CloudTrail logs. Buckets should use encryption, block public access, and least-privilege access policies.

## 7. Operational Governance

CloudTrail records API activity so teams can investigate who changed guardrails, IAM policies, Lambda code, API Gateway stages, or logging settings.
