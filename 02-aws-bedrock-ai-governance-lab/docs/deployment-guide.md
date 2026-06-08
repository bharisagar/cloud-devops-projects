# Deployment Guide

## 1. Enable Model Access

Open Amazon Bedrock in your target region and enable access to the model configured in Terraform.

## 2. Configure Terraform Variables

Copy the example variables file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Update the region, project name, and model ID if needed.

## 3. Deploy Infrastructure

```bash
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

## 4. Run Tests

```bash
terraform output api_endpoint
cd ../tests
python run_governance_tests.py --endpoint <api-endpoint>
```

## 5. Capture Evidence

Use `screenshots/README.md` as the evidence checklist.

## 6. Cleanup

```bash
terraform destroy
```
