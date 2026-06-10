# Bedrock vs SageMaker Model Selection

This project uses one governed API layer and supports two AI backend patterns:

- Amazon Bedrock for managed foundation models and Bedrock Guardrails.
- Amazon SageMaker for customer-owned or open-source models that need full MLOps control.

## Selected Models for This Project

| Path | Selected Model | Runtime | Why This Model |
| --- | --- | --- | --- |
| Bedrock production baseline | Amazon Nova Pro | `apac.amazon.nova-pro-v1:0` | Strong price-performance for enterprise text reasoning, architecture Q&A, policy explanation, and governed assistant workflows. |
| Bedrock cost-optimized route | Amazon Nova Lite | `apac.amazon.nova-lite-v1:0` | Use for high-volume simple prompts, routing, summarization, and demos where cost matters more than highest reasoning quality. |
| Bedrock advanced reasoning option | Anthropic Claude Sonnet 4.6 | `anthropic.claude-sonnet-4-6` or available regional inference profile | Use when long-context reasoning, complex analysis, or code-heavy planning requires a stronger model and the higher token cost is acceptable. |
| SageMaker runtime smoke test | Custom lightweight endpoint | SageMaker real-time endpoint on `ml.m5.large` | Low-cost proof that the governance gateway can invoke SageMaker Runtime. |
| SageMaker LLM path after quota approval | Gemma 3 1B Instruct | JumpStart endpoint on `ml.g5.2xlarge` | Cost-conscious text-generation endpoint for custom-model operations. |
| SageMaker Llama-class path after quota approval | Llama3 8B SEA-Lion v2.1 Instruct | JumpStart endpoint on `ml.g5.4xlarge` | Stronger 8B text-generation endpoint when GPU quota and budget are approved. |

## Why Bedrock Nova Pro Is the Default

The ECS gateway is an enterprise AI governance API. Most requests are architecture questions, policy checks, implementation guidance, summarization, and governance explanations. These need good reasoning and consistent output, but they do not justify running a GPU endpoint 24/7.

Amazon Nova Pro is the default Bedrock model because:

- It is managed by Amazon Bedrock, so there is no endpoint infrastructure to run.
- It works through the Bedrock Converse API used by this app.
- It integrates directly with Bedrock Guardrails.
- It has much lower operational overhead than hosting a custom LLM.
- It gives a strong default path for enterprise GenAI adoption.

Use Nova Lite when the prompt is simple or when the workload is high-volume and cost-sensitive.

Use Claude Sonnet 4.6 only for workloads where long-context reasoning or advanced technical analysis is worth the higher cost. Confirm regional model access before using it because Bedrock model IDs and inference profiles can vary by Region.

## Why SageMaker Has Two Tracks

SageMaker is included to show the custom-model path. It should not be the default for this project because a real-time GPU endpoint can be expensive if left running.

For practical evidence, this project uses a custom smoke endpoint on `ml.m5.large`. It proves endpoint creation, SageMaker Runtime invocation, CloudWatch visibility, and cleanup without requiring GPU quota.

For LLM evidence after quota approval, use a supported JumpStart text-generation model in the target Region:

- Gemma 3 1B Instruct on `ml.g5.2xlarge` for a smaller text-generation endpoint.
- Llama3 8B SEA-Lion v2.1 Instruct on `ml.g5.4xlarge` for a stronger Llama-class endpoint.

The SageMaker path demonstrates:

- Customer-owned or open-weight model hosting.
- Custom inference containers.
- It demonstrates the SageMaker lifecycle: model artifact, endpoint config, endpoint, logs, scaling, Model Monitor, and Model Registry.
- It gives a clear contrast against Bedrock: the organization owns more of the runtime and operations.

Do not use a 70B-class model for this first demo unless there is a specific reason and budget approval. A 70B endpoint usually needs larger GPU infrastructure and changes the project from a governance demo into an infrastructure-heavy LLM hosting project.

## How SageMaker Works End to End

1. Training or model selection starts from customer data, open-source model weights, or a prebuilt JumpStart model.
2. The model artifact and inference container are stored in S3/ECR.
3. A SageMaker model resource points to the artifact, container, and execution role.
4. A model package can be registered in SageMaker Model Registry.
5. Approval gates promote the model from development to staging to production.
6. A SageMaker endpoint config defines instance type, count, variant, and traffic routing.
7. A SageMaker endpoint serves inference through SageMaker Runtime.
8. The ECS governance gateway invokes the endpoint using its task role.
9. CloudWatch captures endpoint logs and latency/error metrics.
10. Model Monitor can track data quality, drift, and model behavior for production workloads.

## Decision Matrix

| Requirement | Choose Bedrock | Choose SageMaker |
| --- | --- | --- |
| Managed foundation model with minimal operations | Yes | No |
| Built-in Bedrock Guardrails | Yes | No, use custom/app-side controls |
| Fast GenAI application delivery | Yes | Sometimes |
| Custom model weights or fine-tuned model hosting | Sometimes, depending on Bedrock support | Yes |
| Full MLOps workflow and Model Registry | Limited | Yes |
| Real-time low-latency custom inference | No | Yes |
| Pay per token instead of always-on endpoint | Yes | No for real-time endpoints |
| Deep endpoint/container/runtime control | No | Yes |

## Final Recommendation for This Project

Deploy the ECS governance platform in this order:

1. `AI_PROVIDER=demo` for safe local and architecture validation.
2. `AI_PROVIDER=bedrock` with `apac.amazon.nova-pro-v1:0` for the primary enterprise GenAI demo.
3. Optional: switch to `apac.amazon.nova-lite-v1:0` to show cost optimization.
4. Optional: connect `AI_PROVIDER=sagemaker` to the `ml.m5.large` smoke endpoint for low-cost SageMaker Runtime evidence.
5. After quota approval, replace the smoke endpoint with a supported JumpStart LLM endpoint.

This keeps the project professional: Bedrock shows the managed GenAI governance path, and SageMaker shows the enterprise MLOps/custom-model path.
