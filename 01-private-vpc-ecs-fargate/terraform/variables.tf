variable "aws_region" {
  description = "AWS region used for the project."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name prefix for all resources."
  type        = string
  default     = "private-vpc-ecs-demo"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "container_port" {
  description = "Container port exposed by the application."
  type        = number
  default     = 3000
}

variable "desired_count" {
  description = "Desired number of ECS tasks."
  type        = number
  default     = 1
}
