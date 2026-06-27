terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

resource "aws_s3_bucket" "logs" {
  bucket = "day-10-risky-logs-demo"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_security_group" "web" {
  name        = "day-10-open-web"
  description = "Demo security group with risky SSH exposure"

  ingress {
    description = "Risky SSH from internet"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = var.project
  }
}

resource "aws_iam_policy" "wildcard_admin" {
  name = "day-10-wildcard-admin-demo"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_db_instance" "demo" {
  identifier           = "day-10-demo-db"
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  username             = "demo_user"
  password             = "ChangeMe12345!"
  skip_final_snapshot  = true
  storage_encrypted    = false
  publicly_accessible  = false
}
