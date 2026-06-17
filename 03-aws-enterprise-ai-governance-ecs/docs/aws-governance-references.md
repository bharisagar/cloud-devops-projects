# AWS Governance References

This implementation is aligned with AWS guidance for responsible AI, Bedrock Guardrails, evaluation, monitoring, auditability, and production operations.

## Reference Mapping

| AWS reference | What it supports in this project |
| --- | --- |
| [AWS Responsible AI](https://aws.amazon.com/ai/responsible-ai/) | Responsible AI dimensions such as privacy and security, safety, controllability, explainability, robustness, governance, and transparency. |
| [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) | Guardrail layer for harmful content, denied topics, word filters, sensitive information filters, contextual grounding, automated reasoning, and guardrail versioning. |
| [Amazon Bedrock Evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) | Continuous evaluation of model and RAG performance using automatic evaluation, human evaluation, LLM-as-judge, and quality metrics. |
| [Bedrock model invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) | Model input/output logging through CloudWatch Logs and S3 for governance, operations, and audit analysis. |
| [Bedrock CloudTrail logging](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html) | Audit trail for Bedrock API activity, caller identity, request timing, and ongoing delivery to S3. |
| [AWS Well-Architected Responsible AI Lens announcement](https://aws.amazon.com/blogs/machine-learning/announcing-the-aws-well-architected-responsible-ai-lens/) | Production framing for use-case scoping, risk assessment, release criteria, evidence-based release decisions, post-release monitoring, and decommissioning. |

## How This Project Implements The Guidance

| Governance area | Project implementation |
| --- | --- |
| Infrastructure controls | API Gateway, optional JWT authorizer, AWS WAF, private VPC Link, internal ALB, ECS Fargate in private subnets, VPC endpoints, least-privilege IAM. |
| Application policy controls | JSON governance rules with `block`, `monitor`, and `policy_mode` actions; policy versioning; rule category and severity. |
| Guardrails | Bedrock Guardrail Terraform resource and runtime support through `AI_PROVIDER=bedrock`. |
| Sensitive data handling | Prompt and answer preview redaction before audit/log storage. |
| Audit evidence | Request IDs, DynamoDB audit records, CloudWatch structured logs, CloudTrail, and S3 evidence bucket. |
| Monitoring | CloudWatch logs, metric filters, dashboard, blocked prompt metrics, critical policy block alarm, latency and ECS health alarms. |
| Evaluation and accountability | Automated governance tests today; next production maturity step is Bedrock Evaluations and human review for high-risk use cases. |

## Production Gap Checklist

Before using this for real organization traffic, validate these items:

- Configure Bedrock Guardrails in AWS and deploy a versioned guardrail.
- Enable Bedrock model invocation logging only after reviewing data-retention and privacy requirements.
- Use CloudTrail trails and S3 evidence storage for ongoing audit records.
- Add continuous model evaluation jobs for output quality, robustness, toxicity, correctness, and RAG grounding.
- Add human-in-the-loop review for high-risk prompts, regulated advice, or sensitive business workflows.
- Keep governance rules under pull-request approval with automated tests and release evidence.
