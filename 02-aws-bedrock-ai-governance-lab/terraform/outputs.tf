output "api_endpoint" {
  description = "POST prompts to this endpoint."
  value       = "${aws_apigatewayv2_api.http.api_endpoint}/prompt"
}

output "guardrail_id" {
  description = "Amazon Bedrock Guardrail ID."
  value       = aws_bedrock_guardrail.ai_governance.guardrail_id
}

output "audit_table_name" {
  description = "DynamoDB table for AI audit records."
  value       = aws_dynamodb_table.ai_audit.name
}

output "governance_log_bucket" {
  description = "S3 bucket for governance logs and evidence."
  value       = aws_s3_bucket.governance_logs.id
}

output "cost_governance_tags" {
  description = "Tags used for AI workload cost allocation."
  value       = local.common_tags
}

output "monthly_budget_name" {
  description = "AWS Budget name when budget_alert_email is configured."
  value       = length(aws_budgets_budget.ai_governance_lab) > 0 ? aws_budgets_budget.ai_governance_lab[0].name : "not-created"
}
