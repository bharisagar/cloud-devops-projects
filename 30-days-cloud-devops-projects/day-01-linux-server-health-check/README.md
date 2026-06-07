# Day 1: Linux Server Health Check Automation

## What We Are Building

Today we build a simple server health check script.

This is not a fancy project, but it is one of the most practical starting points in DevOps. Before Kubernetes, Terraform, CI/CD, or cloud architecture, an engineer should understand what is happening on a machine.

When I troubleshoot any server, I usually start with these questions:

- Is CPU under pressure?
- Is memory almost full?
- Is disk usage dangerous?
- Is the expected process running?
- Is the service port listening?
- Is the machine reachable on the network?
- Is there enough information to explain the issue to someone else?

This project turns those checks into a repeatable script.

## Why This Project Matters

A lot of beginners directly jump into Kubernetes and Terraform. That is exciting, but when something fails, the first clues still come from Linux basics.

For example:

- A container can crash because the host is out of disk.
- A deployment can fail because a port is already used.
- A pipeline can fail because the runner does not have enough memory.
- An EC2 instance can look healthy in AWS but still have a full root volume.

DevOps is not only about creating infrastructure. It is about operating systems with confidence.

## Theory: How a Server Tells You It Is in Trouble

Every server has a few basic signals. If you can read these signals, troubleshooting becomes much easier.

### CPU

CPU tells you how much processing pressure the machine is under. High CPU is not always bad. A build server, video processor, or batch worker may use high CPU normally. The problem starts when CPU stays high and the application becomes slow.

### Memory

Memory pressure can cause applications to slow down, restart, or get killed by the operating system. On Linux, memory also includes cache and buffers, so do not panic just because "free" memory looks low. Learn to look at used, available, and swap together.

### Disk

Disk issues are very common in real incidents. Logs, Docker images, old backups, and temporary files can fill a server. Once disk is full, applications may fail to write logs, databases may stop, and deployments may break.

### Process

A service can only respond if the process is running. A process check is a simple but powerful validation after deployments and restarts.

### Port

Even if the process is running, the service may not be listening on the expected port. Port checks help confirm whether traffic can actually reach the application.

### Network

Network checks confirm whether the server can reach external systems like GitHub, package registries, APIs, or cloud endpoints. Many DevOps issues are not code issues. They are DNS, routing, proxy, firewall, or connectivity issues.

## Architecture

```mermaid
flowchart LR
  user["Engineer"] --> script["Health Check Script"]
  script --> cpu["CPU Check"]
  script --> memory["Memory Check"]
  script --> disk["Disk Check"]
  script --> process["Process Check"]
  script --> network["Network Check"]
  script --> report["Terminal Report"]
```

## Folder Structure

```text
day-01-linux-server-health-check/
├── README.md
├── architecture.mmd
├── sample-output.txt
├── scripts/
│   ├── server-health-check.sh
│   └── server-health-check.ps1
└── screenshots/
    └── README.md
```

## Sample Expected Screenshot

This is a sample expected-output reference, not real evidence from a laptop run. Use it to understand what success should look like, then capture your own screenshot.

![Sample expected output](./screenshots/sample-output.svg)

## Prerequisites

For Linux, macOS, Git Bash, or WSL:

```bash
bash --version
```

For Windows PowerShell:

```powershell
$PSVersionTable.PSVersion
```

## Run on Linux, WSL, or Git Bash

```bash
cd 30-days-cloud-devops-projects/day-01-linux-server-health-check
chmod +x scripts/server-health-check.sh
./scripts/server-health-check.sh
```

Optional: check a specific process and port.

```bash
PROCESS_NAME=node PORT=3000 ./scripts/server-health-check.sh
```

## Run on Windows PowerShell

```powershell
cd C:\bari_sagar\devops-real-projects\30-days-cloud-devops-projects\day-01-linux-server-health-check
.\scripts\server-health-check.ps1
```

Optional:

```powershell
.\scripts\server-health-check.ps1 -ProcessName node -Port 3000
```

## What to Capture as Evidence

Take screenshots of:

1. The script running successfully.
2. Disk, memory, and CPU output.
3. A process check that passes.
4. A process check that fails.
5. Your `sample-output.txt` or terminal output.

## Break It Intentionally

Run a check for a process that does not exist.

```bash
PROCESS_NAME=this-process-does-not-exist ./scripts/server-health-check.sh
```

You should see a warning. This is good. A useful health check does not hide problems.

## Common Troubleshooting

### Permission denied

Run:

```bash
chmod +x scripts/server-health-check.sh
```

### `ss` command not found

Some systems do not include `ss`. Try:

```bash
netstat -tuln
```

The script already falls back where possible.

### PowerShell script blocked

Run PowerShell as your user and allow the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Interview Explanation

You can explain this project like this:

> I built a server health check automation script that collects CPU, memory, disk, process, and port status. The goal was to make basic Linux troubleshooting repeatable. This is useful before deployments, during incidents, and while validating servers after changes.

## Next Improvement

Add log file output:

```bash
./scripts/server-health-check.sh | tee health-report.log
```

In a production setup, this kind of script can be scheduled using cron and integrated with Slack, email, CloudWatch, or Prometheus exporters.
