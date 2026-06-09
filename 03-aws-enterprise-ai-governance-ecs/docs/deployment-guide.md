# Deployment Guide

## Prerequisites

- AWS CLI configured with a sandbox profile.
- Terraform `>= 1.6`.
- Docker Desktop or another local Docker engine.
- Permission to create VPC, ECS, ECR, API Gateway, ALB, IAM, DynamoDB, CloudWatch, CloudTrail, S3, Budgets, and Bedrock Guardrails.
- Bedrock model access enabled if using `AI_PROVIDER=bedrock`.

## 1. Review Variables

```bash
cd terraform
copy terraform.tfvars.example terraform.tfvars
```

For first deployment, keep:

```hcl
ai_provider = "demo"
app_policy_mode = "monitor"
```

## 2. Create ECR Repository

```bash
terraform init
terraform validate
terraform apply -target=aws_ecr_repository.app
```

Get the repository:

```bash
terraform output ecr_repository_url
```

## 3. Build and Push Container

PowerShell:

```powershell
$env:AWS_PROFILE="bedrock-governance"
$region="ap-south-1"
$repo="<ecr_repository_url>"
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin ($repo -replace "/.*$", "")
docker build -t enterprise-ai-governance-ecs:latest ..\app
docker tag enterprise-ai-governance-ecs:latest "$repo`:latest"
docker push "$repo`:latest"
```

Git Bash:

```bash
export AWS_PROFILE=bedrock-governance
region=ap-south-1
repo="<ecr_repository_url>"
aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$(echo "$repo" | cut -d/ -f1)"
docker build -t enterprise-ai-governance-ecs:latest ../app
docker tag enterprise-ai-governance-ecs:latest "$repo:latest"
docker push "$repo:latest"
```

## 4. Deploy Full Platform

```bash
terraform plan -out=tfplan
terraform apply tfplan
```

Get the API endpoint:

```bash
terraform output api_endpoint
```

## 5. Test

```bash
cd ..\tests
python run_governance_tests.py --endpoint <api_endpoint>
```

## 6. Switch to Bedrock Mode

After the local policy and audit path works, switch the managed model path to Amazon Nova Pro:

```hcl
ai_provider = "bedrock"
bedrock_model_id = "apac.amazon.nova-pro-v1:0"
```

Use `apac.amazon.nova-lite-v1:0` only when the requirement is a lower-cost route for simple or high-volume prompts.

Then:

```bash
terraform plan -out=tfplan
terraform apply tfplan
```

## 7. Cleanup

```bash
cd terraform
terraform destroy
```

If S3 bucket deletion fails, empty the evidence bucket and run destroy again.
