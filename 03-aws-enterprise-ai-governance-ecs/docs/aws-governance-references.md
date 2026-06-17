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
| Responsible AI metadata | Each rule can declare responsible AI dimensions, Bedrock Guardrails policy mappings, human-review requirement, and reviewer route. |
| Guardrails | Bedrock Guardrail Terraform resource and runtime support through `AI_PROVIDER=bedrock`; local input and output policy checks mirror the guardrail pattern for demo and preflight enforcement. |
| Sensitive data handling | Prompt and answer preview redaction before audit/log storage. |
| Audit evidence | Request IDs, DynamoDB audit records, CloudWatch structured logs, CloudTrail, and S3 evidence bucket. |
| Monitoring | CloudWatch logs, metric filters, dashboard, blocked prompt metrics, critical policy block alarm, latency and ECS health alarms. |
| Evaluation and accountability | Automated governance tests, policy-stage assertions, human-review routing metadata, and a production path for Bedrock Evaluations. |

## Rule-Level AWS Mapping

Each rule in `app/policies/governance-rules.json` includes these production metadata fields:

- `responsible_ai_dimensions` maps the rule to AWS responsible AI dimensions such as privacy and security, safety, controllability, robustness, transparency, and governance.
- `guardrail_policy_types` maps the rule to Bedrock Guardrails controls such as content filters, denied topics, word filters, sensitive information filters, prompt attack filters, contextual grounding, or automated reasoning.
- `human_review_required` and `reviewer_route` identify whether security, privacy, compliance, or the AI platform team must review the event.
- `policy_stage` in the API response shows whether the input prompt or output response triggered the policy.

## Production Gap Checklist

Before using this for real organization traffic, validate these items:

- Configure Bedrock Guardrails in AWS and deploy a versioned guardrail.
- Enable Bedrock model invocation logging only after reviewing data-retention and privacy requirements.
- Use CloudTrail trails and S3 evidence storage for ongoing audit records.
- Add continuous model evaluation jobs for output quality, robustness, toxicity, correctness, and RAG grounding.
- Connect `human_review_required=true` events to a ticketing or approval workflow such as EventBridge, Security Hub, ServiceNow, Jira, or Slack.
- Keep governance rules under pull-request approval with automated tests and release evidence.
