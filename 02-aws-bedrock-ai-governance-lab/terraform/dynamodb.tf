resource "aws_dynamodb_table" "ai_audit" {
  name         = "${var.project_name}-audit"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "request_id"

  attribute {
    name = "request_id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  tags = local.common_tags
}
