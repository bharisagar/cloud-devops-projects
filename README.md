# Real DevOps Projects

This folder contains portfolio-grade DevOps projects connected to the DevOpsGrade website. The goal is to keep every project practical: architecture, code, deployment steps, troubleshooting notes, and interview talking points.

## Project Index

| # | Project | Status | Focus |
| --- | --- | --- | --- |
| 01 | Private VPC ECS Fargate Platform | Complete | AWS networking, ECS, VPC endpoints, cost optimization |
| 02 | Terraform AWS Foundation Module | Planned | Terraform modules, remote state, IAM, VPC standards |
| 03 | GitHub Actions CI/CD for Containers | Planned | Docker build, scan, ECR push, ECS deploy |
| 04 | EKS GitOps Application Platform | Planned | EKS, Argo CD, Helm, ingress, sealed secrets |
| 05 | Kubernetes Observability Stack | Planned | Prometheus, Grafana, Loki, Alertmanager |
| 06 | Docker Image Optimization Factory | Planned | BuildKit, SBOM, vulnerability scanning |
| 07 | DevSecOps Quality Gate Pipeline | Planned | SonarQube, Checkov, Trivy, Gitleaks |
| 08 | AWS AI Governance Blueprint | Planned | Bedrock guardrails, IAM, audit evidence |
| 09 | AWS Cost and Tagging Automation | Planned | Cost Explorer, tags, budgets, scheduled reporting |
| 10 | Backup and Disaster Recovery Automation | Planned | AWS Backup, restore testing, RTO/RPO |
| 11 | Incident Runbook Automation | Planned | CloudWatch, SSM automation, Kubernetes runbooks |

## How These Projects Are Written

Each project should include:

- `README.md` with problem, architecture, implementation, validation, and cleanup.
- Terraform, Kubernetes, or automation code that can be reviewed safely.
- No hard-coded credentials, account IDs, private domains, or client names.
- A troubleshooting section based on real failure modes.
- Cost and security notes so the project feels production-aware.

## Safety

These projects are learning references. Review cost-impacting resources before running `terraform apply`, especially NAT gateways, load balancers, EKS clusters, RDS instances, and cross-region backups.
