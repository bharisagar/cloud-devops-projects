output "account_id" {
  description = "AWS account ID used by Terraform."
  value       = data.aws_caller_identity.current.account_id
}

output "ecr_repository_url" {
  description = "Push the sample Docker image to this ECR repository."
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name."
  value       = aws_ecs_service.app.name
}

output "alb_dns_name" {
  description = "Public ALB DNS name for the application."
  value       = aws_lb.app.dns_name
}

output "private_subnet_ids" {
  description = "Private subnet IDs used by ECS tasks."
  value       = aws_subnet.private[*].id
}

output "vpc_endpoint_ids" {
  description = "Interface VPC endpoints used by private ECS tasks."
  value       = { for name, endpoint in aws_vpc_endpoint.interface : name => endpoint.id }
}
