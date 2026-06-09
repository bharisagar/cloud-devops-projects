resource "aws_apigatewayv2_api" "http" {
  name          = var.project_name
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_vpc_link" "ecs" {
  name               = "${var.project_name}-vpc-link"
  security_group_ids = [aws_security_group.api_gateway_vpc_link.id]
  subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
}

resource "aws_apigatewayv2_integration" "ecs" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "HTTP_PROXY"
  integration_method     = "ANY"
  integration_uri        = aws_lb_listener.app.arn
  connection_type        = "VPC_LINK"
  connection_id          = aws_apigatewayv2_vpc_link.ecs.id
  payload_format_version = "1.0"
  timeout_milliseconds   = 29000
}

resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.ecs.id}"
}

resource "aws_apigatewayv2_route" "prompt" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "POST /prompt"
  target    = "integrations/${aws_apigatewayv2_integration.ecs.id}"
}

resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.ecs.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api.arn
    format = jsonencode({
      requestId       = "$context.requestId"
      routeKey        = "$context.routeKey"
      status          = "$context.status"
      integration     = "$context.integrationStatus"
      responseLength  = "$context.responseLength"
      responseLatency = "$context.responseLatency"
      sourceIp        = "$context.identity.sourceIp"
    })
  }
}
