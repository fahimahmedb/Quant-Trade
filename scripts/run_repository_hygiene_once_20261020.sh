#!/usr/bin/env bash
set -euo pipefail

REPO="fahimahmedb/Quant-Trade"
BRANCH="blue/master-v2-2026-09-20"
STAMP="20261020"
PROTECT_NEW_WORK_SINCE="2026-10-20T02:05:00Z"
KNOWN_STALE_PRS="21 22 23 24 25 26 27 28 29"

fail() { echo "ERROR: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || fail "$1 is required"; }

need git
need curl
need python3

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  gh auth setup-git >/dev/null 2>&1 || true
fi

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t quant-cleanup)"
trap 'rm -rf "$TMP"' EXIT INT TERM
mkdir -p "$TMP/receipt"

URL="https://github.com/${REPO}.git"
if command -v ssh >/dev/null 2>&1 && GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=5' git ls-remote "git@github.com:${REPO}.git" HEAD >/dev/null 2>&1; then
  URL="git@github.com:${REPO}.git"
fi

echo "[1/8] Cloning ${REPO}..."
git clone --no-single-branch "$URL" "$TMP/repo"
cd "$TMP/repo"
git fetch origin --prune --tags
git checkout -B "$BRANCH" "origin/$BRANCH"

if ! git push --dry-run origin "HEAD:refs/heads/$BRANCH" >/dev/null 2>&1; then
  fail "GitHub write authentication is unavailable. Nothing was deleted. Authenticate git/gh and rerun the same command."
fi

echo "[2/8] Capturing current repository state..."
git ls-remote --heads origin | awk '{sub("refs/heads/", "", $2); print $2 "\t" $1}' | sort >"$TMP/receipt/branches-before.tsv"
BEFORE="$(wc -l <"$TMP/receipt/branches-before.tsv" | tr -d ' ')"
echo "Branches before cleanup: $BEFORE"

# Dynamically protect work created after the cleanup package was prepared.
# This is deliberately independent of branch naming so a new V2 branch cannot be
# accidentally archived/deleted simply because it was not known when CP11 was written.
echo "[3/8] Protecting new work and new open-PR heads..."
python3 - "$PROTECT_NEW_WORK_SINCE" "$TMP/receipt/branches-before.tsv" >"$TMP/recent-keep.txt" <<'PY'
import datetime, subprocess, sys
cutoff=datetime.datetime.fromisoformat(sys.argv[1].replace('Z','+00:00')).timestamp()
for line in open(sys.argv[2], encoding='utf-8'):
    branch, sha=line.rstrip('\n').split('\t')
    try:
        ts=int(subprocess.check_output(['git','show','-s','--format=%ct',sha], text=True).strip())
    except Exception:
        continue
    if ts >= cutoff:
        print(branch)
PY

OPEN_JSON="$TMP/open-prs.json"
curl -fsSL -H 'Accept: application/vnd.github+json' \
  "https://api.github.com/repos/${REPO}/pulls?state=open&per_page=100" >"$OPEN_JSON" \
  || fail "Could not read current open PRs; cleanup stopped before mutation."

python3 - "$OPEN_JSON" "$KNOWN_STALE_PRS" >"$TMP/pr-keep.txt" <<'PY'
import json, sys
stale={int(x) for x in sys.argv[2].split()}
for pr in json.load(open(sys.argv[1], encoding='utf-8')):
    if int(pr['number']) not in stale:
        print(pr['head']['ref'])
PY

cat "$TMP/recent-keep.txt" "$TMP/pr-keep.txt" | sed '/^$/d' | sort -u >"$TMP/dynamic-keep.txt"
cp "$TMP/dynamic-keep.txt" "$TMP/receipt/dynamic-protected-branches.txt"
echo "Dynamic additional keep refs: $(wc -l <"$TMP/dynamic-keep.txt" | tr -d ' ')"

# The destructive engine already lives in the repository and was separately reviewed.
# Work on a temporary copy and inject only the dynamic safety keeps into its static
# here-doc. The repository copy itself is not modified by this bootstrap.
cp scripts/repository_hygiene_20261020.sh "$TMP/engine.sh"
python3 - "$TMP/engine.sh" "$TMP/dynamic-keep.txt" >"$TMP/engine-patched.sh" <<'PY'
import sys
engine=open(sys.argv[1], encoding='utf-8').read()
extra=[x.strip() for x in open(sys.argv[2], encoding='utf-8') if x.strip()]
marker='claude/restaurant-stock-management-mvp-6oq43e\nEOF\n'
if marker not in engine:
    raise SystemExit('cleanup engine keep-set marker not found; refusing mutation')
insert='claude/restaurant-stock-management-mvp-6oq43e\n' + ''.join(x+'\n' for x in extra) + 'EOF\n'
sys.stdout.write(engine.replace(marker, insert, 1))
PY
chmod +x "$TMP/engine-patched.sh"

# Best-effort close the already-disposed stale PRs if gh is available. This is not
# required for branch safety: their head commits are still handled by archive policy.
: >"$TMP/receipt/stale-pr-close.log"
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  for n in $KNOWN_STALE_PRS; do
    state="$(gh pr view "$n" --repo "$REPO" --json state --jq .state 2>/dev/null || true)"
    if [ "$state" = "OPEN" ]; then
      if gh pr close "$n" --repo "$REPO" >/dev/null 2>&1; then
        echo "CLOSED $n" >>"$TMP/receipt/stale-pr-close.log"
      else
        echo "CLOSE_FAILED $n" >>"$TMP/receipt/stale-pr-close.log"
      fi
    else
      echo "NOT_OPEN $n" >>"$TMP/receipt/stale-pr-close.log"
    fi
  done
else
  echo "gh unavailable/not authenticated; stale PR close skipped" >>"$TMP/receipt/stale-pr-close.log"
fi

echo "[4/8] Generating exhaustive cleanup plan (no mutation)..."
PLAN="$TMP/receipt/branch-cleanup-plan-${STAMP}.tsv"
PLAN_FILE="$PLAN" bash "$TMP/engine-patched.sh"

KEEP="$(awk -F '\t' 'NR>1 && $3=="KEEP"{n++}END{print n+0}' "$PLAN")"
ABSORBED="$(awk -F '\t' 'NR>1 && $3=="ABSORBED"{n++}END{print n+0}' "$PLAN")"
ARCHIVE="$(awk -F '\t' 'NR>1 && $3=="ARCHIVE_THEN_DELETE"{n++}END{print n+0}' "$PLAN")"
echo "Plan: KEEP=$KEEP ABSORBED=$ABSORBED ARCHIVE_THEN_DELETE=$ARCHIVE"
[ "$KEEP" -ge 5 ] || fail "Resolved keep set is unexpectedly small; cleanup stopped."

echo "[5/8] Applying verified cleanup..."
LOG="$TMP/receipt/cleanup-execution-${STAMP}.log"
PLAN_FILE="$PLAN" APPLY=1 bash "$TMP/engine-patched.sh" | tee "$LOG"

echo "[6/8] Verifying final branch state..."
git fetch origin --prune --tags
git ls-remote --heads origin | awk '{sub("refs/heads/", "", $2); print $2 "\t" $1}' | sort >"$TMP/receipt/branches-after.tsv"
AFTER="$(wc -l <"$TMP/receipt/branches-after.tsv" | tr -d ' ')"
DELETED="$(grep -c '^DELETED' "$LOG" || true)"
FAILED="$(grep -c '^DELETE_FAILED' "$LOG" || true)"
SKIPPED="$(grep -Ec '^SKIP_CHANGED|^SKIP_CHANGED_AT_DELETE|^SKIP_NO_LONGER_ABSORBED' "$LOG" || true)"
TAGS="$(git ls-remote --tags origin "refs/tags/archive/${STAMP}/tip-*" | awk '!/\^\{\}$/' | wc -l | tr -d ' ')"

for required in \
  "$BRANCH" \
  builder/oracle-economic-loop-recovery-20261019 \
  audit/forensic-checkpoint-20261019 \
  builder/research-os-aggressive-architecture-20261015 \
  builder/research-factory-core-v2 \
  research/edge-lab-continuous \
  research/legacy-economic-reconciliation-20261015; do
  grep -Fq "${required}"$'\t' "$TMP/receipt/branches-after.tsv" \
    || fail "Required retained branch missing after cleanup: $required"
done

cat >"$TMP/receipt/EXECUTION_RECEIPT.md" <<EOF
# Repository Hygiene Execution Receipt — ${STAMP}

- branches before: **${BEFORE}**
- branches after: **${AFTER}**
- deleted branch refs: **${DELETED}**
- archive tags: **${TAGS}**
- concurrent-change safety skips: **${SKIPPED}**
- delete failures: **${FAILED}**

Unique/diverged tips were archived before branch deletion. Branches created after
\`${PROTECT_NEW_WORK_SINCE}\` and non-stale open-PR heads were dynamically protected.
The live Oracle V1 line and CP11 V2-source keep set were retained.

This cleanup grants no economic, prospective, real-capital or live-trading authority.
EOF

echo "[7/8] Publishing cleanup evidence back to GitHub..."
# Reacquire the latest routing branch before writing evidence so a concurrent doc
# update is not overwritten.
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"
DEST="governance/repository-hygiene/${STAMP}"
mkdir -p "$DEST"
cp "$TMP/receipt/"* "$DEST/"
cp "$TMP/receipt/EXECUTION_RECEIPT.md" governance/REPOSITORY_HYGIENE_EXECUTION_LATEST.md

git config user.name "Quant Repository Hygiene"
git config user.email "repository-hygiene@users.noreply.github.com"
git add "$DEST" governance/REPOSITORY_HYGIENE_EXECUTION_LATEST.md
if ! git diff --cached --quiet; then
  git commit -m "governance: record repository hygiene execution ${STAMP} [skip ci]"
  if ! git push origin "HEAD:refs/heads/$BRANCH"; then
    git pull --rebase origin "$BRANCH"
    git push origin "HEAD:refs/heads/$BRANCH"
  fi
fi
RECEIPT_SHA="$(git rev-parse HEAD)"

echo "[8/8] Final verification complete."
echo
echo "============================================================"
echo "QUANT-TRADE REPOSITORY HYGIENE COMPLETE"
echo "Branches: $BEFORE -> $AFTER"
echo "Deleted refs: $DELETED"
echo "Archive tags: $TAGS"
echo "Race-safety skips: $SKIPPED"
echo "Delete failures: $FAILED"
echo "Receipt commit: $RECEIPT_SHA"
echo "Receipt: $DEST/EXECUTION_RECEIPT.md"
echo "============================================================"

if [ "$FAILED" -gt 0 ] || [ "$SKIPPED" -gt 0 ]; then
  echo "Some refs were conservatively skipped; the committed log identifies them for a later second pass."
fi
