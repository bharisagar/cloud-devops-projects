# 30 Days Cloud DevOps Projects

This is the day-by-day learning path. Days 1-14 cover local foundations, AWS, Terraform, observability, AI quality, and a deployed browser app. Days 15-30 add local security, Kubernetes, delivery, infrastructure, cost, and recovery exercises. The later labs use synthetic data unless a README explicitly describes an optional cluster step.

## Days 1-30

| Day | Project | Outcome |
| --- | --- | --- |
| [Day 1](./day-01-linux-server-health-check/README.md) | Linux Server Health Check Automation | Create a script that collects CPU, memory, disk, process, and network status. |
| [Day 2](./day-02-git-github-workflow/README.md) | Git and GitHub Workflow Project | Practice branches, commits, PR-style thinking, and release notes using a small static app. |
| [Day 3](./day-03-dockerize-node-app/README.md) | Dockerize a Node.js App | Build and run a containerized API with health checks. |
| [Day 4](./day-04-docker-compose-app-with-db/README.md) | Docker Compose App with Database | Run an app and PostgreSQL together using Compose networking. |
| [Day 5](./day-05-nginx-reverse-proxy-docker/README.md) | Nginx Reverse Proxy with Docker | Route traffic through Nginx to backend containers. |
| [Day 6](./day-06-github-actions-docker-ci/README.md) | GitHub Actions CI for Docker App | Run test and Docker build checks automatically on GitHub. |
| [Day 7](./day-07-push-docker-image-to-registry/README.md) | Push Docker Image to Registry | Tag and publish a Docker image to DockerHub or AWS ECR. |
| [Day 8](./day-08-aws-cloud-foundation-setup/README.md) | AWS Cloud Foundation Setup | Verify AWS identity, create cost guardrails, and store evidence in a private encrypted S3 bucket. |
| [Day 9](./day-09-aws-security-audit-dashboard/README.md) | AWS Security Audit Dashboard | Audit IAM, S3, security groups, CloudTrail, and budget guardrails with a local dashboard and evidence reports. |
| [Day 10](./day-10-terraform-policy-guardrails/README.md) | Terraform Policy-as-Code Guardrail Platform | Scan Terraform plans for risky infrastructure and block unsafe deployments with reports and a dashboard. |
| [Day 11](./day-11-observability-ai-incident-summary/README.md) | Observability Pipeline with AI Incident Summary | Correlate logs, metrics, and traces into an incident summary with root cause, evidence, and next actions. |
| [Day 12](./day-12-evalops-ai-quality-gate/README.md) | EvalOps Quality Gate for AI Incident Summaries | Score AI-generated incident summaries against golden expectations and block low-quality output before it reaches responders. |
| [Day 13](./day-13-rag-devops-runbook-assistant/README.md) | Local RAG DevOps Runbook Assistant | Retrieve cited runbook guidance from local markdown knowledge and produce an evidence-backed incident response plan. |
| [Day 14](./day-14-hospital-voice-translator/README.md) | Hospital Voice Translation Assistant | Convert Kannada patient phrases into English, Tamil, and Telugu speech output with GitHub Actions CI/CD deployment. |
| [Day 15](./day-15-secret-exposure-drill/README.md) | Secret Exposure Drill | Detect synthetic literal credentials and plan a response. |
| [Day 16](./day-16-dependency-policy/README.md) | Dependency Policy Gate | Check a sample inventory for license and age violations. |
| [Day 17](./day-17-kubernetes-first-deployment/README.md) | First Kubernetes Deployment | Render a Deployment and internal Service. |
| [Day 18](./day-18-kubernetes-health-rollout/README.md) | Kubernetes Health and Rollout Controls | Add probes, resource limits, and rolling update policy. |
| [Day 19](./day-19-kustomize-environments/README.md) | Environment Overlays with Kustomize | Render staging and production variants from one base. |
| [Day 20](./day-20-gitops-drift/README.md) | GitOps Drift Detection | Compare desired and observed workload snapshots. |
| [Day 21](./day-21-canary-analysis/README.md) | Canary Release Analysis | Gate promotion on sample error and latency metrics. |
| [Day 22](./day-22-release-quality-gate/README.md) | Release Quality Gate | Combine build, test, security, policy, and approval signals. |
| [Day 23](./day-23-artifact-integrity/README.md) | Artifact Integrity Check | Verify a release payload against its SHA-256 digest. |
| [Day 24](./day-24-terraform-drift-review/README.md) | Terraform Drift Review | Detect infrastructure differences in synthetic snapshots. |
| [Day 25](./day-25-cloud-cost-forecast/README.md) | Cloud Cost Forecast | Project month-end spend and compare it with a budget. |
| [Day 26](./day-26-backup-restore-verification/README.md) | Backup Restore Verification | Compare restored records with source data. |
| [Day 27](./day-27-chaos-experiment/README.md) | Bounded Chaos Experiment | Evaluate a failure drill against recovery and impact limits. |
| [Day 28](./day-28-capacity-planning/README.md) | Capacity Planning | Estimate replicas from peak load and measured throughput. |
| [Day 29](./day-29-disaster-recovery-tabletop/README.md) | Disaster Recovery Tabletop | Check observed recovery against RTO and RPO. |
| [Day 30](./day-30-capstone-readiness/README.md) | Cloud DevOps Readiness Capstone | Run local labs together and summarize unresolved gates. |

## Learning Rule

Every project should leave proof:

- Commands you ran.
- Output you saw.
- Screenshots you captured.
- Mistakes you fixed.
- A short explanation in your own words.

That is how a project becomes interview evidence instead of just another folder in GitHub.
