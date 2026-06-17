# Deployment Evidence

These screenshots were captured from the live AWS sandbox deployment in `ap-south-1` on June 10, 2026. They are included to show the platform was deployed, tested, and reviewed across the main operational layers.

Additional production-like Bedrock/enforce evidence was captured on June 17, 2026. That evidence shows Terraform validation, container delivery, API health, blocked prompt behavior, CloudWatch structured logs, Bedrock Guardrail readiness, and S3-published governance rules.

## ECS and Container Delivery

| Evidence | What it shows |
| --- | --- |
| [ECS service health](../screenshots/evidence/04-ecs-service-health-targets.png) | ECS service active with one desired and running task, deployment success, and healthy ALB target. |
| [Running ECS task](../screenshots/evidence/05-ecs-running-task-image.png) | Fargate task running the ECR image for the AI governance gateway. |
| [Task definition](../screenshots/evidence/03-ecs-task-definition-fargate.png) | Fargate task size, task role, execution role, and `awsvpc` network mode. |
| [Task environment variables](../screenshots/evidence/02-ecs-task-definition-env-vars.png) | Runtime configuration for provider mode, Bedrock model, guardrail ID, audit table, and region. |
| [ECR repository](../screenshots/evidence/09-ecr-ecs-repository.png) | Private ECR repository created for the ECS service image. |
| [ECR image digest](../screenshots/evidence/08-ecr-image-digest.png) | Pushed container image with `latest` tag, SHA digest, image size, and active status. |

## Private Networking and Routing

| Evidence | What it shows |
| --- | --- |
| [Internal Application Load Balancer](../screenshots/evidence/07-internal-application-load-balancer.png) | Internal ALB in private subnets across two Availability Zones. |
| [ALB listener](../screenshots/evidence/06-alb-http-listener-target-group.png) | HTTP listener forwarding traffic to the ECS target group. |

## AI Governance

| Evidence | What it shows |
| --- | --- |
| [Bedrock Guardrail](../screenshots/evidence/01-bedrock-guardrail-ready.png) | Amazon Bedrock Guardrail created for the platform and in `Ready` status. |
| [SageMaker smoke IAM role](../screenshots/evidence/10-sagemaker-smoke-role.png) | IAM execution role used for the SageMaker Runtime smoke-test path. |
| [SageMaker smoke model list](../screenshots/evidence/12-sagemaker-smoke-model-list.png) | SageMaker model created for low-cost runtime integration validation. |
| [SageMaker smoke model detail](../screenshots/evidence/11-sagemaker-smoke-model-detail.png) | SageMaker model details, container image, and execution role. |
| [SageMaker smoke ECR repository](../screenshots/evidence/13-ecr-sagemaker-smoke-repository.png) | Private ECR repository used for the SageMaker smoke-test container. |

## Production-Like Bedrock Enforce Validation - June 17, 2026

| Evidence | What it shows |
| --- | --- |
| [Terraform init and validate](../screenshots/evidence/prod-2026-06-17/01-terraform-init-validate.png) | Terraform initialized successfully and configuration validation passed. |
| [Docker build and ECR push](../screenshots/evidence/prod-2026-06-17/02-docker-build-ecr-push.png) | Governance container image built and pushed to ECR. |
| [Terraform plan and apply](../screenshots/evidence/prod-2026-06-17/03-terraform-plan-apply.png) | AWS infrastructure plan generated and applied for the platform. |
| [API health and blocked prompt](../screenshots/evidence/prod-2026-06-17/04-api-health-blocked-prompt.png) | Deployed API is healthy in Bedrock/enforce mode and blocks credential exfiltration. |
| [Bedrock throttling observed](../screenshots/evidence/prod-2026-06-17/05-bedrock-throttling-observed.png) | Safe prompt reached the Bedrock backend and hit a model quota/throttling condition. |
| [Chat console in Bedrock enforce mode](../screenshots/evidence/prod-2026-06-17/06-chat-console-bedrock-enforce.png) | Browser console shows provider `bedrock`, policy mode `enforce`, and DynamoDB plus CloudWatch audit path. |
| [CloudWatch blocked prompt log](../screenshots/evidence/prod-2026-06-17/07-cloudwatch-blocked-prompt-log.png) | CloudWatch log event records `prompt_completed`, `credential_exfiltration`, `policy_stage=input`, severity, and review route. |
| [CloudWatch throttling log](../screenshots/evidence/prod-2026-06-17/08-cloudwatch-throttling-log.png) | CloudWatch log event records `prompt_failed` with `ThrottlingException`. |
| [Bedrock Guardrail ready](../screenshots/evidence/prod-2026-06-17/09-bedrock-guardrail-ready-prod.png) | Bedrock Guardrail `rs1xf8wegx0f` is created and ready. |
| [S3 governance rules](../screenshots/evidence/prod-2026-06-17/10-s3-governance-rules-prod.png) | Governance rules JSON is published to the S3 evidence bucket. |

## Notes

- The ECS gateway was validated in `demo` provider mode to keep the walkthrough predictable and control model spend.
- The task definition includes the Bedrock Nova Pro model ID and Bedrock Guardrail configuration for the production Bedrock path.
- The SageMaker smoke model validates the custom endpoint integration pattern without running a high-cost GPU LLM endpoint.
- The June 17 validation used `AI_PROVIDER=bedrock` and `APP_POLICY_MODE=enforce`.
- Bedrock throttling is captured as operational evidence. It indicates backend quota/rate limiting, not a governance policy failure.
