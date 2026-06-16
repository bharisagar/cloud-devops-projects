provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
    Workload    = "EnterpriseAIGovernance"
  }

  availability_zones = slice(data.aws_availability_zones.available.names, 0, length(var.private_subnet_cidrs))

  private_subnets = {
    for index, cidr in var.private_subnet_cidrs : index => {
      cidr = cidr
      az   = local.availability_zones[index]
    }
  }

  interface_endpoints = toset([
    "bedrock-runtime",
    "ecr.api",
    "ecr.dkr",
    "logs",
    "sts"
  ])

  container_image = var.container_image != "" ? var.container_image : "${aws_ecr_repository.app.repository_url}:latest"
  alarm_actions   = [for topic in aws_sns_topic.alerts : topic.arn]

  governance_rules_key    = "governance-policy/governance-rules.json"
  managed_rules_s3_uri    = "s3://${aws_s3_bucket.governance_evidence.id}/${local.governance_rules_key}"
  governance_rules_s3_uri = var.governance_rules_s3_uri != "" ? var.governance_rules_s3_uri : (var.publish_governance_rules_to_s3 ? local.managed_rules_s3_uri : "")
}
