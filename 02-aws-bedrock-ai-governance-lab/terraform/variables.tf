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
