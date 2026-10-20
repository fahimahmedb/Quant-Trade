#!/usr/bin/env bash
set -euo pipefail

REPO="fahimahmedb/Quant-Trade"
BRANCH="blue/master-v2-2026-09-20"

command -v git >/dev/null 2>&1 || { echo "git is required" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl is required" >&2; exit 1; }

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  gh auth setup-git >/dev/null 2>&1 || true
fi

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t quant-cleanup)"
trap 'rm -rf "$TMP"' EXIT INT TERM

URL="https://github.com/${REPO}.git"
if command -v ssh >/dev/null 2>&1 && GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=5' git ls-remote "git@github.com:${REPO}.git" HEAD >/dev/null 2>&1; then
  URL="git@github.com:${REPO}.git"
fi

echo "Cloning ${REPO}..."
git clone --no-single-branch "$URL" "$TMP/repo"
cd "$TMP/repo"
git fetch origin --prune --tags
git checkout -B "$BRANCH" "origin/$BRANCH"

if ! git push --dry-run origin "HEAD:refs/heads/$BRANCH" >/dev/null 2>&1; then
  echo "GitHub write authentication is unavailable. Nothing was deleted." >&2
  exit 1
fi

echo "Generating cleanup plan..."
PLAN_FILE="$TMP/branch-cleanup-plan-20261020.tsv" bash scripts/repository_hygiene_20261020.sh
cp "$TMP/branch-cleanup-plan-20261020.tsv" ./branch-cleanup-plan-20261020.tsv

echo "Applying verified cleanup..."
PLAN_FILE="$TMP/branch-cleanup-plan-20261020.tsv" APPLY=1 bash scripts/repository_hygiene_20261020.sh | tee "$TMP/cleanup-execution-20261020.log"

git fetch origin --prune --tags
COUNT="$(git branch -r | grep -v -- '->' | wc -l | tr -d ' ')"

echo
echo "Repository hygiene pass complete."
echo "Remaining remote branches: $COUNT"
echo "The engine archives unique/diverged tips before deleting their branch refs and skips refs that move during execution."
echo "Keep the terminal output as the execution receipt."
