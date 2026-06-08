data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../app/lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "ai_app" {
  function_name    = var.project_name
  role             = aws_iam_role.lambda.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      AUDIT_TABLE_NAME          = aws_dynamodb_table.ai_audit.name
      BEDROCK_MODEL_ID          = var.bedrock_model_id
      BEDROCK_GUARDRAIL_ID      = aws_bedrock_guardrail.ai_governance.guardrail_id
      BEDROCK_GUARDRAIL_VERSION = aws_bedrock_guardrail_version.ai_governance.version
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
  tags       = local.common_tags
}
