resource "aws_s3_bucket" "governance_logs" {
  bucket_prefix = "${var.project_name}-logs-"
  tags          = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "governance_logs" {
  bucket                  = aws_s3_bucket.governance_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "governance_logs" {
  bucket = aws_s3_bucket.governance_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "governance_logs" {
  bucket = aws_s3_bucket.governance_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}
