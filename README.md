# 30 Days Cloud DevOps Projects

This repository is a practical Cloud and DevOps project roadmap by Bhari Sagar.

The goal is simple: do not just read DevOps. Build it, break it, fix it, document it, and keep evidence.

I created this repo for learners who want project-based practice across Linux, Git, Docker, CI/CD, AWS, Terraform, Kubernetes, observability, security, and real production thinking. Every project is written in a way a beginner can follow, but the explanations are also shaped by the kind of issues engineers face in real work.

## Current Status

| Day | Project | Status | Main Skill |
| --- | --- | --- | --- |
| Day 1 | Linux Server Health Check Automation | Complete | Linux, Bash, PowerShell, troubleshooting |
| Day 2 | Git and GitHub Workflow Project | Complete | Git workflow, branches, PR thinking |
| Day 3 | Dockerize a Node.js App | Complete | Dockerfile, image build, container run |
| Day 4 | Docker Compose App with Database | Complete | Compose, app + Postgres, networking |
| Day 5 | Nginx Reverse Proxy with Docker | Complete | Reverse proxy, upstreams, containers |
| Day 6 | GitHub Actions CI for Docker App | Complete | CI pipeline, test, Docker build |
| Day 7 | Push Docker Image to Registry | Complete | DockerHub/ECR publishing, tags |
| Day 8 | AWS Cloud Foundation Setup | Complete | AWS IAM, CLI, S3 evidence, budget guardrails |
| Day 9 | AWS Security Audit Dashboard | Complete | IAM audit, S3 risk, security groups, CloudTrail, dashboard evidence |
| Day 10 | Terraform Policy-as-Code Guardrail Platform | Complete | Terraform plans, policy-as-code, risk scoring, deployment gates |
| Day 11 | Observability Pipeline with AI Incident Summary | Complete | Logs, metrics, traces, SLOs, incident intelligence |
| Day 12-30 | Coming next | Planned | EvalOps, RAG, AI PR review, Kubernetes, monitoring |

## Repository Structure

```text
cloud-devops-projects/
|-- 30-days-cloud-devops-projects/
|   |-- day-01-linux-server-health-check/
|   |-- day-02-git-github-workflow/
|   |-- day-03-dockerize-node-app/
|   |-- day-04-docker-compose-app-with-db/
|   |-- day-05-nginx-reverse-proxy-docker/
|   |-- day-06-github-actions-docker-ci/
|   |-- day-07-push-docker-image-to-registry/
|   |-- day-08-aws-cloud-foundation-setup/
|   |-- day-09-aws-security-audit-dashboard/
|   |-- day-10-terraform-policy-guardrails/
|   `-- day-11-observability-ai-incident-summary/
|-- .github/
|   `-- workflows/
|       |-- day-06-docker-ci.yml
|       `-- day-07-publish-image.yml
|-- 01-private-vpc-ecs-fargate/
|-- 02-aws-bedrock-ai-governance-lab/
`-- 03-aws-enterprise-ai-governance-ecs/
```

The `30-days-cloud-devops-projects` folder is the structured learning path. The `01-private-vpc-ecs-fargate` folder is an advanced production-style project that will later map into the AWS/Terraform section of the roadmap.

## How to Study This Repo

For each day:

1. Read the concept section first.
2. Run the project locally.
3. Take screenshots for evidence.
4. Break one thing intentionally.
5. Fix it using the troubleshooting section.
6. Write your own short explanation in the project notes.
7. Push your version to GitHub.

The most important DevOps habit is not memorizing commands. It is learning how systems behave when something fails.

## Evidence for Students

Every day has a `screenshots/README.md` file with the project output and an evidence checklist.

Good screenshots include:

- Terminal command success.
- Browser output.
- Docker container running.
- GitHub Actions workflow result.
- Error screenshot and fix screenshot.

Do not upload secrets, access keys, private IPs from office systems, customer names, or internal URLs.

## Safety Notes

- Days 1-7 are designed to run locally. Day 8 begins the AWS foundation with IAM identity verification, budget guardrails, and secure S3 evidence storage. Day 9 adds read-only security audit reporting. Day 10 reviews Terraform plans locally before any cloud changes are applied. Day 11 uses local synthetic telemetry to teach observability and incident response without cloud cost.
- Docker-based days require Docker Desktop on Windows or Docker Engine on Linux.
- AWS/Terraform days should be run in a personal sandbox AWS account only.
- Always destroy paid cloud resources after testing.

## Advanced Project Already Available

| Project | Focus |
| --- | --- |
| [Private VPC ECS Fargate Platform](./01-private-vpc-ecs-fargate/README.md) | AWS ECS, private subnets, VPC endpoints, CloudWatch, ECR, cost optimization |
| [AWS Bedrock AI Governance Lab](./02-aws-bedrock-ai-governance-lab/README.md) | Amazon Bedrock, Guardrails, AI governance, IAM, audit logging, CloudTrail |
| [AWS Enterprise AI Governance Platform on ECS](./03-aws-enterprise-ai-governance-ecs/README.md) | API Gateway, ECS Fargate, private VPC Link, Bedrock, SageMaker-ready provider design, audit, monitoring, security, cost governance |

The private VPC ECS Fargate project solves a real-world class of `ResourceInitializationError` issues where tasks in private subnets cannot reach ECR, CloudWatch Logs, S3, or Secrets Manager.
