variable "aws_region" {
  description = "AWS region for the demo."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
  default     = "enterprise-ai-governance-ecs"
}

variable "environment" {
  description = "Environment tag."
  type        = string
  default     = "sandbox"
}

variable "owner" {
  description = "Owner tag."
  type        = string
  default     = "barisagar"
}

variable "cost_center" {
  description = "Cost center tag for cost allocation."
  type        = string
  default     = "learning-ai-governance"
}

variable "vpc_cidr" {
  description = "CIDR block for the private AI governance VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs for ECS, ALB, API Gateway VPC Link, and VPC endpoints."
  type        = list(string)
  default     = ["10.40.10.0/24", "10.40.20.0/24"]
}

variable "container_image" {
  description = "Container image URI. If empty, Terraform uses the project ECR repository with the latest tag."
  type        = string
  default     = ""
}

variable "desired_count" {
  description = "Initial ECS task count."
  type        = number
  default     = 1
}

variable "task_cpu" {
  description = "Fargate task CPU units."
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "Fargate task memory in MiB."
  type        = number
  default     = 1024
}

variable "min_task_count" {
  description = "Minimum autoscaling task count."
  type        = number
  default     = 1
}

variable "max_task_count" {
  description = "Maximum autoscaling task count."
  type        = number
  default     = 4
}

variable "ai_provider" {
  description = "AI provider used by the container: demo, bedrock, or sagemaker."
  type        = string
  default     = "demo"
}

variable "app_policy_mode" {
  description = "Application-side policy behavior: monitor or enforce."
  type        = string
  default     = "monitor"
}

variable "bedrock_model_id" {
  description = "Bedrock model or inference profile ID."
  type        = string
  default     = "apac.amazon.nova-lite-v1:0"
}

variable "sagemaker_endpoint_name" {
  description = "Optional SageMaker endpoint name when ai_provider is sagemaker."
  type        = string
  default     = ""
}

variable "audit_ttl_days" {
  description = "Number of days to retain DynamoDB audit records."
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days."
  type        = number
  default     = 14
}

variable "enable_container_insights" {
  description = "Enable ECS Container Insights."
  type        = bool
  default     = true
}

variable "enable_bedrock_invocation_logging" {
  description = "Enable account-level Bedrock invocation logging. Only enable if no other logging config owns this account/region."
  type        = bool
  default     = false
}

variable "latency_alarm_seconds" {
  description = "ALB target response time alarm threshold in seconds."
  type        = number
  default     = 3
}

variable "alarm_email" {
  description = "Optional email for CloudWatch alarm notifications."
  type        = string
  default     = ""
}

variable "create_budget" {
  description = "Create a sandbox AWS Budget."
  type        = bool
  default     = true
}

variable "monthly_budget_usd" {
  description = "Sandbox monthly budget limit."
  type        = string
  default     = "20"
}

variable "budget_alert_email" {
  description = "Email for AWS Budget notifications."
  type        = string
  default     = ""
}
