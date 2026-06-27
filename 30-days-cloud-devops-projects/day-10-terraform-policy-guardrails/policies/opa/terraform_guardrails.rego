package terraform.guardrails

default allow = false

required_tags := {"Project", "Owner", "Environment", "CostCenter"}
sensitive_ports := {22, 3389, 3306, 5432, 6379, 9200}

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_security_group"
  ingress := resource.values.ingress[_]
  cidr := ingress.cidr_blocks[_]
  cidr == "0.0.0.0/0"
  msg := sprintf("Security group %s allows ingress from the internet.", [resource.address])
}

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_security_group"
  ingress := resource.values.ingress[_]
  cidr := ingress.cidr_blocks[_]
  cidr == "0.0.0.0/0"
  sensitive_ports[ingress.from_port]
  msg := sprintf("Security group %s exposes sensitive port %v.", [resource.address, ingress.from_port])
}

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_iam_policy"
  contains(resource.values.policy, "\"Action\":\"*\"")
  contains(resource.values.policy, "\"Resource\":\"*\"")
  msg := sprintf("IAM policy %s grants wildcard admin permissions.", [resource.address])
}

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_db_instance"
  resource.values.storage_encrypted == false
  msg := sprintf("RDS instance %s has storage_encrypted disabled.", [resource.address])
}

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_instance"
  block := resource.values.root_block_device[_]
  block.encrypted == false
  msg := sprintf("EC2 instance %s has an unencrypted root volume.", [resource.address])
}

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  missing := required_tags - {tag | resource.values.tags[tag]}
  count(missing) > 0
  msg := sprintf("Resource %s is missing required tags: %v.", [resource.address, missing])
}

deny[msg] {
  change := input.resource_changes[_]
  change.change.actions[_] == "delete"
  msg := sprintf("Terraform plan deletes %s.", [change.address])
}

allow {
  count(deny) == 0
}
