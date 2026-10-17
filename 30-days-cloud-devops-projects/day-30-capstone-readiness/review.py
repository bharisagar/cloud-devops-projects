"""Run the local learning labs and summarize their sample outcomes."""
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PYTHON_LABS = [
    (15, "secret-exposure-drill", "scan.py", 1),
    (16, "dependency-policy", "check.py", 1),
    (20, "gitops-drift", "compare.py", 1),
    (21, "canary-analysis", "analyze.py", 1),
    (22, "release-quality-gate", "gate.py", 1),
    (23, "artifact-integrity", "verify.py", 0),
    (24, "terraform-drift-review", "drift.py", 1),
    (25, "cloud-cost-forecast", "forecast.py", 1),
    (26, "backup-restore-verification", "verify.py", 0),
    (27, "chaos-experiment", "evaluate.py", 1),
    (28, "capacity-planning", "plan.py", 1),
    (29, "disaster-recovery-tabletop", "assess.py", 1),
]


def main():
    unexpected = []
    unresolved = []
    for day, name, script, expected in PYTHON_LABS:
        folder = ROOT / f"day-{day:02d}-{name}"
        result = subprocess.run([sys.executable, script], cwd=folder, text=True, capture_output=True)
        outcome = "PASS" if result.returncode == 0 else "ACTION"
        print(f"Day {day:02d}: {outcome}")
        if result.returncode != expected:
            unexpected.append(f"Day {day:02d} returned {result.returncode}, expected sample result {expected}")
        if result.returncode != 0:
            unresolved.append(f"Day {day:02d}: {result.stdout.strip().splitlines()[-1] if result.stdout.strip() else result.stderr.strip()}")
    for day, name, path in [(17, "kubernetes-first-deployment", "."), (18, "kubernetes-health-rollout", "."), (19, "kustomize-environments", "overlays/staging"), (19, "kustomize-environments", "overlays/production")]:
        folder = ROOT / f"day-{day:02d}-{name}"
        try:
            result = subprocess.run(["kubectl", "kustomize", path], cwd=folder, text=True, capture_output=True)
            valid = result.returncode == 0 and "kind: Deployment" in result.stdout and "kind: Service" in result.stdout
        except FileNotFoundError:
            valid = False
        print(f"Day {day:02d} {path}: {'RENDERED' if valid else 'ERROR'}")
        if not valid:
            unexpected.append(f"Day {day:02d} {path} did not render")
    print(f"\nUnresolved sample gates: {len(unresolved)}")
    for item in unresolved:
        print(f"- {item}")
    for item in unexpected:
        print(f"UNEXPECTED {item}")
    print("Decision: NOT READY" if unresolved or unexpected else "Decision: READY FOR HUMAN REVIEW")
    return int(bool(unresolved or unexpected))


if __name__ == "__main__":
    sys.exit(main())
