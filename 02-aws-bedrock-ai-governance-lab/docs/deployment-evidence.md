# Deployment Evidence

These screenshots were captured from a real sandbox deployment of the AWS Bedrock AI Governance Lab.

Sensitive account details and full ARNs are redacted. The resources were destroyed after screenshots were captured to avoid ongoing AWS cost.

## Evidence Summary

| Evidence | What It Shows |
| --- | --- |
| Terraform outputs | API endpoint, audit table, governance log bucket, and guardrail ID created by Terraform. |
| Terraform state list | Terraform-managed AWS resources before cleanup. |
| API Gateway console and CLI | HTTP API created with `POST /prompt` route. |
| Lambda console | Lambda AI application connected to API Gateway. |
| Bedrock Guardrail console and CLI | Guardrail created with restricted professional advice policy and `READY` status. |
| Governance test results | Prompt injection and restricted advice blocked by Guardrails. |
| S3 CloudTrail evidence | CloudTrail governance logs delivered to S3. |

## 1. Terraform Outputs

<img src="../screenshots/evidence/01-terraform-outputs.png" alt="Terraform outputs for deployed AWS Bedrock AI Governance Lab" width="900">

## 2. Terraform State

<img src="../screenshots/evidence/02-terraform-state-list.png" alt="Terraform state list showing created AWS resources" width="900">

## 3. API Gateway Console

<img src="../screenshots/evidence/03-api-gateway-console.png" alt="API Gateway console showing deployed HTTP API" width="900">

## 4. API Gateway Route

<img src="../screenshots/evidence/04-api-gateway-route-cli.png" alt="AWS CLI output showing POST /prompt API Gateway route" width="900">

## 5. Lambda Application

<img src="../screenshots/evidence/05-lambda-console.png" alt="Lambda console showing AI application function with API Gateway trigger" width="900">

## 6. Bedrock Guardrail Console

<img src="../screenshots/evidence/06-bedrock-guardrail-console.png" alt="Amazon Bedrock Guardrail console showing ready guardrail" width="900">

## 7. Bedrock Guardrail Policy

<img src="../screenshots/evidence/07-bedrock-guardrail-cli.png" alt="AWS CLI output showing Bedrock Guardrail restricted advice policy" width="900">

## 8. Governance Test: Quota Handling and Prompt Injection

<img src="../screenshots/evidence/08-governance-tests-quota-and-blocked.png" alt="Governance test output showing quota handling and prompt injection guardrail response" width="900">

## 9. Governance Test: Restricted Advice Blocked

<img src="../screenshots/evidence/09-governance-tests-restricted-advice.png" alt="Governance test output showing restricted advice blocked by guardrail" width="900">

## 10. S3 CloudTrail Evidence

<img src="../screenshots/evidence/10-s3-cloudtrail-evidence.png" alt="S3 console showing CloudTrail governance evidence logs" width="900">

## Cleanup Evidence

After capturing these screenshots, Terraform destroy was run. The versioned S3 log bucket had to be emptied before the final destroy could complete.

Final verification:

- `terraform state list` returned no resources.
- `terraform output` returned no outputs.
- Lambda lookup returned `Function not found`.
