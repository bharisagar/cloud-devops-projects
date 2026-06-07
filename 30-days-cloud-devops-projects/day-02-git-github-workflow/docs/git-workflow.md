# Git Workflow Notes

## Daily Flow

```bash
git switch main
git pull
git checkout -b feature/small-clear-change
git status
git diff
git add .
git commit -m "Describe the change"
git push -u origin feature/small-clear-change
```

## My Rule

One branch should tell one story.

Do not mix:

- Dockerfile fixes
- Terraform refactor
- README rewrite
- unrelated formatting

If everything is mixed, review becomes difficult and rollback becomes risky.

## Useful Commands

```bash
git branch
git status
git diff
git log --oneline --decorate --graph -10
git restore <file>
```

## Production Habit

Before pushing infrastructure changes, always read the diff. This habit catches mistakes early, especially in Terraform, Kubernetes YAML, GitHub Actions, and shell scripts.
