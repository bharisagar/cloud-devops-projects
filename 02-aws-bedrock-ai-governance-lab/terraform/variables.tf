variable "aws_region" {
  description = "AWS region for the governance lab."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
  default     = "bedrock-ai-governance-lab"
}

variable "environment" {
  description = "Environment tag used for governance and cost allocation."
  type        = string
  default     = "sandbox"
}

variable "team_name" {
  description = "Team tag used for ownership and chargeback reporting."
  type        = string
  default     = "platform-engineering"
}

variable "cost_center" {
  description = "Cost center tag used for AI workload cost accountability."
  type        = string
  default     = "learning-lab"
}

variable "owner" {
  description = "Owner tag used to identify who is responsible for the workload."
  type        = string
  default     = "bharisagar"
}

variable "bedrock_model_id" {
  description = "Approved Bedrock model ID for this application. Enable model access before deploying."
  type        = string
  default     = "apac.amazon.nova-micro-v1:0"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 14
}

variable "monthly_budget_limit_usd" {
  description = "Monthly sandbox budget limit in USD for this AI governance lab."
  type        = number
  default     = 5
}

variable "budget_alert_email" {
  description = "Email address for AWS Budget alerts. Leave empty to skip creating the budget."
  type        = string
  default     = ""
}
