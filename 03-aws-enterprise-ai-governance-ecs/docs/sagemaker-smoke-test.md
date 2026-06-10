# SageMaker Runtime Smoke Test

This helper proves the governance gateway can call SageMaker Runtime without deploying an expensive GPU LLM endpoint.

Use it when GPU endpoint quota is not available or when the goal is only to capture SageMaker endpoint evidence. It is not the production LLM path. The production custom-model path remains a larger text-generation model such as Llama-class or Gemma-class models deployed through SageMaker JumpStart after quota and budget approval.

## Current Account Finding

In `ap-south-1`, the account has quota for `ml.m5.large` endpoints, but the checked JumpStart LLMs require larger GPU endpoint quota:

| Model checked | Default endpoint instance | Current quota result |
| --- | --- | --- |
| Gemma 3 1B Instruct | `ml.g5.2xlarge` | quota is `0` |
| Llama3 8B SEA-Lion v2.1 Instruct | `ml.g5.4xlarge` | quota is `0` |
| Zephyr 7B Beta | `ml.g5.2xlarge` | quota is `0` |

The smoke endpoint uses `ml.m5.large`, which is available and was priced at `$0.121/hour` in Mumbai from the AWS Pricing API on June 10, 2026.

## Evidence to Capture

- `aws service-quotas` output showing GPU quota limitation.
- SageMaker endpoint page showing `InService`.
- `aws sagemaker-runtime invoke-endpoint` output.
- CloudWatch log stream for the endpoint.
- Optional: ECS/local gateway response when `AI_PROVIDER=sagemaker`.

## Cleanup

Delete the endpoint first, then the endpoint config, model, ECR image/repository, and IAM role. Do not leave the endpoint running after screenshots.
