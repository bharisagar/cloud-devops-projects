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
| Day 12 | EvalOps Quality Gate for AI Incident Summaries | Complete | EvalOps, AI output scoring, quality gates, hallucination checks |
| Day 13 | Local RAG DevOps Runbook Assistant | Complete | RAG, runbook retrieval, citations, incident response |
| Day 14 | Hospital Voice Translation Assistant | Complete | Speech-to-text, translation UX, text-to-speech, GitHub Pages CI/CD |
| Day 15 | [Secret Exposure Response Dashboard](./30-days-cloud-devops-projects/day-15-secret-exposure-drill/README.md) | Complete | Local app, redacted reports, tests, CI, screenshots |
| Day 16 | [Dependency Policy Gate](./30-days-cloud-devops-projects/day-16-dependency-policy/README.md) | Complete | Local dashboard, policy reports, tests, CI, screenshots |
| Day 17 | [First Kubernetes Deployment](./30-days-cloud-devops-projects/day-17-kubernetes-first-deployment/README.md) | Starter lab | Deployment and Service manifests |
| Day 18 | [Kubernetes Health and Rollout Controls](./30-days-cloud-devops-projects/day-18-kubernetes-health-rollout/README.md) | Starter lab | Probes, resource limits, rollout strategy |
| Day 19 | [Environment Overlays with Kustomize](./30-days-cloud-devops-projects/day-19-kustomize-environments/README.md) | Starter lab | Staging and production overlays |
| Day 20 | [GitOps Drift Detection](./30-days-cloud-devops-projects/day-20-gitops-drift/README.md) | Starter lab | Desired versus observed state |
| Day 21 | [Canary Release Analysis](./30-days-cloud-devops-projects/day-21-canary-analysis/README.md) | Starter lab | Error and latency release gates |
| Day 22 | [Release Quality Gate](./30-days-cloud-devops-projects/day-22-release-quality-gate/README.md) | Starter lab | Build, test, security, and approval checks |
| Day 23 | [Artifact Integrity Check](./30-days-cloud-devops-projects/day-23-artifact-integrity/README.md) | Starter lab | SHA-256 payload verification |
| Day 24 | [Terraform Drift Review](./30-days-cloud-devops-projects/day-24-terraform-drift-review/README.md) | Starter lab | Infrastructure state comparison |
| Day 25 | [Cloud Cost Forecast](./30-days-cloud-devops-projects/day-25-cloud-cost-forecast/README.md) | Starter lab | Budget forecasting |
| Day 26 | [Backup Restore Verification](./30-days-cloud-devops-projects/day-26-backup-restore-verification/README.md) | Starter lab | Restored data comparison |
| Day 27 | [Bounded Chaos Experiment](./30-days-cloud-devops-projects/day-27-chaos-experiment/README.md) | Starter lab | Recovery and impact limits |
| Day 28 | [Capacity Planning](./30-days-cloud-devops-projects/day-28-capacity-planning/README.md) | Starter lab | Replica sizing from peak load |
| Day 29 | [Disaster Recovery Tabletop](./30-days-cloud-devops-projects/day-29-disaster-recovery-tabletop/README.md) | Starter lab | RTO and RPO checks |
| Day 30 | [Cloud DevOps Readiness Capstone](./30-days-cloud-devops-projects/day-30-capstone-readiness/README.md) | Starter lab | Cross-project readiness review |

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
|   |-- day-11-observability-ai-incident-summary/
|   |-- day-12-evalops-ai-quality-gate/
|   |-- day-13-rag-devops-runbook-assistant/
|   |-- day-14-hospital-voice-translator/
|   |-- day-15-secret-exposure-drill/
|   |-- day-16-dependency-policy/
|   |-- day-17-kubernetes-first-deployment/
|   |-- day-18-kubernetes-health-rollout/
|   |-- day-19-kustomize-environments/
|   |-- day-20-gitops-drift/
|   |-- day-21-canary-analysis/
|   |-- day-22-release-quality-gate/
|   |-- day-23-artifact-integrity/
|   |-- day-24-terraform-drift-review/
|   |-- day-25-cloud-cost-forecast/
|   |-- day-26-backup-restore-verification/
|   |-- day-27-chaos-experiment/
|   |-- day-28-capacity-planning/
|   |-- day-29-disaster-recovery-tabletop/
|   `-- day-30-capstone-readiness/
|-- .github/
|   `-- workflows/
|       |-- day-06-docker-ci.yml
|       |-- day-07-publish-image.yml
|       `-- day-14-hospital-voice-translator-pages.yml
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

The early projects include `screenshots/README.md` evidence checklists. For Days 15-30, each project README names the output to capture.

Good screenshots include:

- Terminal command success.
- Browser output.
- Docker container running.
- GitHub Actions workflow result.
- Error screenshot and fix screenshot.

Do not upload secrets, access keys, private IPs from office systems, customer names, or internal URLs.

## Safety Notes

- Days 1-7 are designed to run locally. Day 8 begins the AWS foundation with IAM identity verification, budget guardrails, and secure S3 evidence storage. Day 9 adds read-only security audit reporting. Day 10 reviews Terraform plans locally before any cloud changes are applied. Day 11 uses local synthetic telemetry to teach observability and incident response without cloud cost. Day 12 evaluates local AI incident summaries without cloud cost. Day 13 retrieves local runbook guidance without cloud cost. Day 14 runs as a static browser app and deploys through GitHub Pages CI/CD. Days 15-30 are local labs with synthetic data; Days 17-19 can optionally be applied to a learning Kubernetes namespace.
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
