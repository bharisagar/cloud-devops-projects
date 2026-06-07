#!/usr/bin/env bash
set -euo pipefail

PROCESS_NAME="${PROCESS_NAME:-node}"
PORT="${PORT:-3000}"
TARGET_HOST="${TARGET_HOST:-github.com}"

line() {
  printf '%s\n' '----------------------------------------'
}

section() {
  printf '\n[%s]\n' "$1"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

echo '========================================'
echo ' Bhari Sagar - Server Health Check'
echo '========================================'
printf 'Hostname        : %s\n' "$(hostname)"
printf 'Date            : %s\n' "$(date '+%Y-%m-%d %H:%M:%S')"
printf 'Kernel          : %s\n' "$(uname -sr)"

section "CPU"
if command_exists uptime; then
  printf 'Load Average    : %s\n' "$(uptime | awk -F'load average:' '{print $2}' | xargs)"
fi
if command_exists nproc; then
  printf 'CPU Cores       : %s\n' "$(nproc)"
fi

section "Memory"
if command_exists free; then
  free -h | awk 'NR==1 || NR==2 {print}'
else
  echo "free command not available"
fi

section "Disk"
df -h / | awk 'NR==1 || NR==2 {print}'

section "Top Processes"
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 6 || true

section "Process Check"
if pgrep -x "$PROCESS_NAME" >/dev/null 2>&1; then
  printf '%s            : running\n' "$PROCESS_NAME"
else
  printf '%s            : not running\n' "$PROCESS_NAME"
fi

section "Port Check"
if command_exists ss; then
  if ss -tuln | grep -q ":${PORT} "; then
    printf '%s            : listening\n' "$PORT"
  else
    printf '%s            : not listening\n' "$PORT"
  fi
elif command_exists netstat; then
  if netstat -tuln | grep -q ":${PORT} "; then
    printf '%s            : listening\n' "$PORT"
  else
    printf '%s            : not listening\n' "$PORT"
  fi
else
  echo "Neither ss nor netstat is available"
fi

section "Network"
if ping -c 1 "$TARGET_HOST" >/dev/null 2>&1; then
  printf '%s      : reachable\n' "$TARGET_HOST"
else
  printf '%s      : not reachable\n' "$TARGET_HOST"
fi

line
echo "Result          : health check completed"
