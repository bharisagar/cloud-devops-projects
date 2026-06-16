output "api_endpoint" {
  description = "API Gateway endpoint for the enterprise AI governance gateway."
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "ecr_repository_url" {
  description = "ECR repository URL for the governance gateway container image."
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.this.name
}

output "ecs_service_name" {
  description = "ECS service name."
  value       = aws_ecs_service.app.name
}

output "audit_table_name" {
  description = "DynamoDB audit table."
  value       = aws_dynamodb_table.audit.name
}

output "guardrail_id" {
  description = "Amazon Bedrock Guardrail ID."
  value       = aws_bedrock_guardrail.ai_governance.guardrail_id
}

output "dashboard_name" {
  description = "CloudWatch dashboard name."
  value       = aws_cloudwatch_dashboard.governance.dashboard_name
}

output "evidence_bucket" {
  description = "S3 bucket used for CloudTrail and governance evidence."
  value       = aws_s3_bucket.governance_evidence.id
}

output "governance_rules_s3_uri" {
  description = "Governance rules S3 URI used by ECS when enabled."
  value       = local.governance_rules_s3_uri
}
