#!/usr/bin/env bash
# Fast-rail checkpoint: persist every agent worktree's unmerged work to GitHub.
#
# Agents run in .claude/worktrees/* (local, ephemeral). When a usage limit or a
# container reclaim kills them, their commits and uncommitted files are lost.
# This script turns each worktree's work (commits + uncommitted + untracked,
# excluding raw caches and large files) into a patch under
# research/fast_rail/wip/<worktree>.patch, then commits and pushes the main
# branch. Idempotent: unchanged patches produce no commit.
#
#   bash scripts/fast_rail_checkpoint.sh            # checkpoint + push
#   CHECKPOINT_NO_PUSH=1 bash scripts/fast_rail_checkpoint.sh
# Resume a worktree's work: git apply research/fast_rail/wip/<name>.patch
set -u
ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
cd "$ROOT" || exit 0
OUT="research/fast_rail/wip"
mkdir -p "$OUT"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
for wt in .claude/worktrees/*/; do
  [ -d "$wt" ] || continue
  name="$(basename "$wt")"
  base="$(git merge-base HEAD "$(git -C "$wt" rev-parse HEAD)" 2>/dev/null)" || continue
  # Skip worktrees whose commits are already merged and that have no local edits.
  if git merge-base --is-ancestor "$(git -C "$wt" rev-parse HEAD)" HEAD \
     && [ -z "$(git -C "$wt" status --porcelain)" ]; then
    rm -f "$OUT/$name.patch"; continue
  fi
  # Mark untracked files (except raw caches / files > 20 MB) as intent-to-add.
  git -C "$wt" ls-files --others --exclude-standard -z | while IFS= read -r -d '' f; do
    case "$f" in */raw/*|*.pyc) continue;; esac
    [ "$(stat -c %s "$wt/$f" 2>/dev/null || echo 0)" -gt 20000000 ] && continue
    git -C "$wt" add -N -- "$f"
  done
  git -C "$wt" diff --binary "$base" -- . ':(exclude)*/raw/*' ':(exclude)STATE.md' \
    > "$OUT/$name.patch.tmp"
  if [ -s "$OUT/$name.patch.tmp" ]; then mv "$OUT/$name.patch.tmp" "$OUT/$name.patch"
  else rm -f "$OUT/$name.patch.tmp" "$OUT/$name.patch"; fi
done
git add -A -- "$OUT" FAST_RAIL_STATE.md research/fast_rail/registry.jsonl 2>/dev/null
if ! git diff --cached --quiet; then
  git commit -q -m "fast-rail: automatic checkpoint of agent worktrees" \
    -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >/dev/null
fi
[ -n "${CHECKPOINT_NO_PUSH:-}" ] || git push -q origin "$BRANCH" >/dev/null 2>&1 || true
exit 0
