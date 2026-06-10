resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_subnet" "private" {
  for_each = local.private_subnets

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.project_name}-private-${each.value.az}"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.project_name}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "api_gateway_vpc_link" {
  name        = "${var.project_name}-api-vpc-link-sg"
  description = "API Gateway VPC Link egress to internal ALB"
  vpc_id      = aws_vpc.this.id
}

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Internal ALB ingress from API Gateway VPC Link"
  vpc_id      = aws_vpc.this.id
}

resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_name}-ecs-tasks-sg"
  description = "ECS task ingress from internal ALB and egress to AWS PrivateLink"
  vpc_id      = aws_vpc.this.id
}

resource "aws_security_group" "vpc_endpoints" {
  name        = "${var.project_name}-vpce-sg"
  description = "Interface endpoint ingress from ECS tasks"
  vpc_id      = aws_vpc.this.id
}

resource "aws_security_group_rule" "api_gateway_to_alb" {
  type                     = "egress"
  description              = "Forward API Gateway traffic to ALB"
  security_group_id        = aws_security_group.api_gateway_vpc_link.id
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "alb_from_api_gateway" {
  type                     = "ingress"
  description              = "API Gateway VPC Link to ALB"
  security_group_id        = aws_security_group.alb.id
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.api_gateway_vpc_link.id
}

resource "aws_security_group_rule" "alb_to_ecs" {
  type                     = "egress"
  description              = "Forward ALB traffic to ECS tasks"
  security_group_id        = aws_security_group.alb.id
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.ecs_tasks.id
}

resource "aws_security_group_rule" "ecs_from_alb" {
  type                     = "ingress"
  description              = "Internal ALB to ECS app"
  security_group_id        = aws_security_group.ecs_tasks.id
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "ecs_to_https" {
  type              = "egress"
  description       = "ECS tasks to AWS HTTPS endpoints through PrivateLink and gateway endpoints"
  security_group_id = aws_security_group.ecs_tasks.id
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "vpc_endpoints_from_ecs" {
  type                     = "ingress"
  description              = "ECS tasks to AWS service endpoints"
  security_group_id        = aws_security_group.vpc_endpoints.id
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.ecs_tasks.id
}

resource "aws_security_group_rule" "vpc_endpoints_egress" {
  type              = "egress"
  description       = "Endpoint return traffic"
  security_group_id = aws_security_group.vpc_endpoints.id
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = [var.vpc_cidr]
}

resource "aws_vpc_endpoint" "interface" {
  for_each = local.interface_endpoints

  vpc_id              = aws_vpc.this.id
  service_name        = "com.amazonaws.${var.aws_region}.${each.value}"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = [for subnet in aws_subnet.private : subnet.id]
  security_group_ids  = [aws_security_group.vpc_endpoints.id]

  tags = {
    Name = "${var.project_name}-${each.value}-vpce"
  }
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  tags = {
    Name = "${var.project_name}-s3-vpce"
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  tags = {
    Name = "${var.project_name}-dynamodb-vpce"
  }
}

resource "aws_lb" "internal" {
  name               = substr("${var.project_name}-alb", 0, 32)
  internal           = true
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [for subnet in aws_subnet.private : subnet.id]

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-internal-alb"
  }
}
