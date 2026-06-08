resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = var.log_retention_days
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "bedrock_invocations" {
  name              = "/aws/bedrock/${var.project_name}/invocations"
  retention_in_days = var.log_retention_days
  tags              = local.common_tags
}

resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.governance_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AWSCloudTrailAclCheck"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:GetBucketAcl"
        Resource  = aws_s3_bucket.governance_logs.arn
      },
      {
        Sid       = "AWSCloudTrailWrite"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.governance_logs.arn}/AWSLogs/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      },
      {
        Sid       = "AmazonBedrockLogsWrite"
        Effect    = "Allow"
        Principal = { Service = "bedrock.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.governance_logs.arn}/bedrock-invocations/AWSLogs/${data.aws_caller_identity.current.account_id}/BedrockModelInvocationLogs/*"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
          }
        }
      }
    ]
  })
}

resource "aws_cloudtrail" "governance" {
  name                          = "${var.project_name}-trail"
  s3_bucket_name                = aws_s3_bucket.governance_logs.id
  include_global_service_events = true
  is_multi_region_trail         = false
  enable_logging                = true

  depends_on = [aws_s3_bucket_policy.cloudtrail]
  tags       = local.common_tags
}

resource "aws_bedrock_model_invocation_logging_configuration" "this" {
  logging_config {
    cloudwatch_config {
      log_group_name = aws_cloudwatch_log_group.bedrock_invocations.name
      role_arn       = aws_iam_role.bedrock_logging.arn
    }

    s3_config {
      bucket_name = aws_s3_bucket.governance_logs.id
      key_prefix  = "bedrock-invocations/"
    }

    text_data_delivery_enabled = true
  }
}
