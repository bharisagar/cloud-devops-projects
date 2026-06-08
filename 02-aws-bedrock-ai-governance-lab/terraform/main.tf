provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  common_tags = {
    Project      = var.project_name
    Application  = "bedrock-ai-governance"
    Environment  = var.environment
    Team         = var.team_name
    CostCenter   = var.cost_center
    Owner        = var.owner
    Purpose      = "aws-ai-governance-lab"
    CostGoverned = "true"
  }
}
