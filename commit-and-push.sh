#!/bin/bash
# Run this script in your Terminal (outside Cursor) to commit and push to saiVerma898/FiverrGuy

set -e
cd "$(dirname "$0")"

# Ensure we're a git repo (init only if .git missing or broken)
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  git init
  git remote add origin https://github.com/saiVerma898/FiverrGuy.git
fi

# Ensure remote is set
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin https://github.com/saiVerma898/FiverrGuy.git
fi
git remote set-url origin https://github.com/saiVerma898/FiverrGuy.git

# Stage, commit, push
git add -A
git status
git commit -m "Initial commit: ComfyUI Serverless" || true
git branch -M main
git push -u origin main

echo "Done. Pushed to https://github.com/saiVerma898/FiverrGuy"
