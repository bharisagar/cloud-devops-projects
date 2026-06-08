provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = "sandbox"
    Purpose     = "aws-ai-governance-lab"
  }
}
