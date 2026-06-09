# Bedrock vs SageMaker

## Simple Explanation

Amazon Bedrock is best when the customer wants managed foundation models without managing model infrastructure.

Amazon SageMaker is best when the customer owns the ML lifecycle: data preparation, training, tuning, model registry, deployment, monitoring, and custom endpoint operations.

In many enterprises, the best answer is not one or the other. A governed AI platform may use both:

- Bedrock for GenAI assistants, summarization, Q&A, content generation, and guardrails.
- SageMaker for custom predictive models, domain-specific models, model registry, batch inference, and full MLOps.

## How SageMaker Works End to End

1. Data is prepared from S3, data lake, warehouse, or feature store.
2. Training jobs run on managed SageMaker infrastructure.
3. Experiments track training parameters, metrics, and artifacts.
4. A model artifact is stored in S3.
5. The model is registered in SageMaker Model Registry.
6. An approval step promotes the model to staging or production.
7. The model is deployed as real-time, serverless, asynchronous, or batch inference.
8. Applications invoke the SageMaker endpoint through SageMaker Runtime.
9. Model Monitor, CloudWatch, and logs track data quality, latency, errors, and drift.
10. Pipelines automate retraining, evaluation, approval, and deployment.

## Decision Matrix

| Requirement | Prefer Bedrock | Prefer SageMaker |
| --- | --- | --- |
| Use managed foundation models quickly | Yes | No |
| Avoid model hosting infrastructure | Yes | No |
| Built-in GenAI guardrails | Yes | No, use custom controls around endpoint |
| Bring your own trained model | Sometimes, depending on import support | Yes |
| Full MLOps lifecycle | Limited | Yes |
| Model registry and approval workflow | Limited | Yes |
| Custom training jobs | No | Yes |
| Batch predictions | Bedrock batch for supported FMs | SageMaker Batch Transform for ML workloads |
| Tight custom inference container control | No | Yes |

## Model Choice Recommendation

For this demo:

- Use `demo` mode for stakeholder walkthrough without model cost.
- Use Bedrock with Amazon Nova Lite or another approved low-cost text model for the GenAI path.
- Use SageMaker only when you want to demonstrate customer-owned model hosting or MLOps workflow.

For a customer:

- If the use case is text generation, summarization, chatbot, or document Q&A, start with Bedrock.
- If the use case is fraud scoring, churn prediction, forecasting, or a trained domain model, use SageMaker.
- If the customer wants both, keep the ECS governance gateway as the common policy and audit layer.

## Why ECS Helps the Comparison

With ECS, the application layer stays the same. Only the backend provider changes:

- `AI_PROVIDER=bedrock` calls Bedrock Converse API.
- `AI_PROVIDER=sagemaker` calls SageMaker Runtime.

This lets architects compare governance, latency, operations, and cost without changing the customer-facing API.
