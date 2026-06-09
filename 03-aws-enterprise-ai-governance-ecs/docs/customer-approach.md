# Customer Approach

## Positioning

Do not approach the customer by saying, "We can build an AI API." That sounds like a small implementation task.

Approach it as:

> We can help you create a governed AI access layer on AWS so teams can use Bedrock and SageMaker safely, with auditability, security controls, model selection standards, monitoring, and cost visibility.

## Discovery Questions

Ask these before proposing the final design:

- Which business teams need AI access first?
- Are the use cases generative AI, predictive ML, document processing, or a mix?
- Is the model expected to be managed by AWS, customized by the customer, or trained by the customer?
- What data classification can be sent to the model?
- Do prompts or responses contain PII, financial data, healthcare data, or customer confidential data?
- What are the latency expectations for each use case?
- Who approves model usage before production?
- What audit evidence is required by security, risk, or compliance teams?
- What is the monthly budget for sandbox, pilot, and production?
- What happens when a prompt is blocked or model latency increases?

## Recommended Customer Journey

### Phase 1: Governed Sandbox

- Deploy this ECS gateway in a sandbox account.
- Use `AI_PROVIDER=demo` first for stakeholder walkthroughs.
- Enable Bedrock after model access, quotas, and budget controls are confirmed.
- Run governance test prompts and capture evidence.

### Phase 2: Controlled Pilot

- Add identity integration with JWT/OIDC.
- Add team and use-case metadata to every request.
- Turn on Bedrock invocation logging only after the customer approves the data handling policy.
- Create dashboards for blocked prompts, latency, 4xx/5xx errors, and model throttling.

### Phase 3: Production Platform

- Move logs to a central security account.
- Use separate AWS accounts per environment.
- Add CI/CD with container scanning and approval gates.
- Add model approval workflow using SageMaker Model Registry for custom models.
- Add WAF, rate limits, and customer-specific authorization.

## Architecture Review Focus

The value is not only the AI model. The value is the control plane around the model:

- Who can use it?
- Which model is approved?
- What data can be sent?
- What was blocked?
- What was returned?
- What was the latency?
- What did it cost?
- Can security review the evidence later?

This project demonstrates that control plane.
