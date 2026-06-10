# Deployment Evidence

These screenshots were captured from the live AWS sandbox deployment in `ap-south-1` on June 10, 2026. They are included to show the platform was deployed, tested, and reviewed across the main operational layers.

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

## Notes

- The ECS gateway was validated in `demo` provider mode to keep the walkthrough predictable and control model spend.
- The task definition includes the Bedrock Nova Pro model ID and Bedrock Guardrail configuration for the production Bedrock path.
- The SageMaker smoke model validates the custom endpoint integration pattern without running a high-cost GPU LLM endpoint.
