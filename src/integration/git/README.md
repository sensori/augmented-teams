# 🧩 Git Sync Integration

This module handles automated and manual Git synchronization for the Augmented Teams GPT repository.

## 🚀 How It Works
- Keeps the repo up to date automatically (via GitHub Actions).
- Allows manual upload from GPT sessions ("please store this / upload my change").
- Avoids requiring users to install Git locally.

## 🧠 Files
- `git_sync.py` — Python helper for syncing and committing code.
- `.github/workflows/git-sync.yaml` — Workflow that runs every 6 hours and can also be manually triggered.

## 🧰 Manual Use
To commit GPT-generated changes manually:
```bash
python src/integration/git/git_sync.py
```

## ☁️ Automated Use
The GitHub Action:
- Pulls latest changes
- Runs sync logic
- Commits and pushes updates
- Runs every 6 hours or on manual trigger
