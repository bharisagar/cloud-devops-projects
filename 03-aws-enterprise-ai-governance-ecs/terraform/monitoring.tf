resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/ecs/${var.project_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/apigateway/${var.project_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "bedrock_invocations" {
  name              = "/aws/bedrock/${var.project_name}/invocations"
  retention_in_days = var.log_retention_days
}

resource "aws_bedrock_model_invocation_logging_configuration" "this" {
  count = var.enable_bedrock_invocation_logging ? 1 : 0

  logging_config {
    cloudwatch_config {
      log_group_name = aws_cloudwatch_log_group.bedrock_invocations.name
      role_arn       = aws_iam_role.bedrock_logging[0].arn
    }

    s3_config {
      bucket_name = aws_s3_bucket.governance_evidence.id
      key_prefix  = "bedrock-invocations/"
    }

    text_data_delivery_enabled = true
  }
}

resource "aws_sns_topic" "alerts" {
  count = var.alarm_email != "" ? 1 : 0

  name = "${var.project_name}-alerts"
}

resource "aws_sns_topic_subscription" "alerts_email" {
  count = var.alarm_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

resource "aws_cloudwatch_metric_alarm" "alb_latency" {
  alarm_name          = "${var.project_name}-alb-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = var.latency_alarm_seconds
  alarm_description   = "ALB target response time is above the agreed AI API latency threshold."
  alarm_actions       = local.alarm_actions

  dimensions = {
    LoadBalancer = aws_lb.internal.arn_suffix
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.project_name}-alb-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "AI gateway target returned too many 5xx responses."
  alarm_actions       = local.alarm_actions

  dimensions = {
    LoadBalancer = aws_lb.internal.arn_suffix
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_cpu" {
  alarm_name          = "${var.project_name}-ecs-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "ECS AI gateway CPU utilization is high."
  alarm_actions       = local.alarm_actions

  dimensions = {
    ClusterName = aws_ecs_cluster.this.name
    ServiceName = aws_ecs_service.app.name
  }
}

resource "aws_cloudwatch_log_metric_filter" "prompt_requests" {
  name           = "${var.project_name}-prompt-requests"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.event_type = \"prompt_completed\" }"

  metric_transformation {
    name      = "PromptRequests"
    namespace = "EnterpriseAIGovernance/${var.project_name}"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "blocked_prompts" {
  name           = "${var.project_name}-blocked-prompts"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.event_type = \"prompt_completed\" && $.action = \"blocked\" }"

  metric_transformation {
    name      = "BlockedPrompts"
    namespace = "EnterpriseAIGovernance/${var.project_name}"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "failed_prompts" {
  name           = "${var.project_name}-failed-prompts"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.event_type = \"prompt_failed\" }"

  metric_transformation {
    name      = "FailedPrompts"
    namespace = "EnterpriseAIGovernance/${var.project_name}"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "critical_policy_blocks" {
  name           = "${var.project_name}-critical-policy-blocks"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.event_type = \"prompt_completed\" && $.action = \"blocked\" && $.rule_severity = \"critical\" }"

  metric_transformation {
    name      = "CriticalPolicyBlocks"
    namespace = "EnterpriseAIGovernance/${var.project_name}"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "blocked_prompt_spike" {
  alarm_name          = "${var.project_name}-blocked-prompt-spike"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "BlockedPrompts"
  namespace           = "EnterpriseAIGovernance/${var.project_name}"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  treat_missing_data  = "notBreaching"
  alarm_description   = "Blocked chatbot prompts exceeded the expected demo or production threshold."
  alarm_actions       = local.alarm_actions

  depends_on = [aws_cloudwatch_log_metric_filter.blocked_prompts]
}

resource "aws_cloudwatch_metric_alarm" "critical_policy_block" {
  alarm_name          = "${var.project_name}-critical-policy-block"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CriticalPolicyBlocks"
  namespace           = "EnterpriseAIGovernance/${var.project_name}"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  alarm_description   = "A critical governance policy blocked a chatbot prompt."
  alarm_actions       = local.alarm_actions

  depends_on = [aws_cloudwatch_log_metric_filter.critical_policy_blocks]
}

resource "aws_cloudwatch_dashboard" "governance" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "API latency and target errors"
          region = var.aws_region
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.internal.arn_suffix],
            [".", "HTTPCode_Target_5XX_Count", ".", "."]
          ]
          stat = "Average"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "AI governance prompt decisions"
          region = var.aws_region
          metrics = [
            ["EnterpriseAIGovernance/${var.project_name}", "PromptRequests"],
            [".", "BlockedPrompts"],
            [".", "FailedPrompts"],
            [".", "CriticalPolicyBlocks"]
          ]
          stat   = "Sum"
          period = 300
        }
      },
      {
        type   = "log"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "Latest governed chatbot requests"
          region = var.aws_region
          query  = "SOURCE '${aws_cloudwatch_log_group.app.name}' | fields @timestamp, request_id, tenant_id, provider, action, latency_ms | filter event_type = 'prompt_completed' | sort @timestamp desc | limit 20"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 6
        properties = {
          title  = "ECS service CPU and memory"
          region = var.aws_region
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.this.name, "ServiceName", aws_ecs_service.app.name],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
          stat = "Average"
        }
      }
    ]
  })
}
