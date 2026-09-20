# REPOSITORY HYGIENE EXECUTION RUNBOOK — 2026-09-20

Authority: Blue / Mission Control.
Organizational audit: `governance/BLUE_ORGANIZATIONAL_AUDIT_2026-09-20.md`.
Deletion authority: `governance/BRANCH_DELETE_READY_INDEX_2026-09-20.md`.
Default migration review: `governance/DEFAULT_BRANCH_MIGRATION_REVIEW_2026-09-20.md`.

Status:
`RUNBOOK = PREPARED / NOT_EXECUTED`

## 1. Purpose

Execute the already-approved repository namespace cleanup from an authenticated admin/development shell.

This runbook is **not** a P0 deployment operation.

It must not mutate:
- `/opt/quant`;
- `/opt/quant-releases/**`;
- `/var/lib/quant-p0/**`;
- systemd P0 state;
- deployment authority;
- target-host qualification evidence.

Use the administrative/development clone, currently expected under:
`/mnt/quant-data/quant/Quant-Trade`

## 2. Allowed operations

This runbook may:
- fetch/prune Git refs in the admin clone;
- read GitHub repository metadata;
- change the repository default branch using GitHub admin API/CLI;
- delete only refs in the exact current `BRANCH_DELETE_READY_INDEX`;
- record evidence.

It may not:
- force-move a branch as a substitute for deletion;
- delete a branch whose SHA moved;
- delete a protected branch;
- delete the current default branch;
- delete an unlisted branch;
- amend P0/P14D/Product governance;
- modify the qualifying P0 release.

## 3. Required tools / authority

Required:
- authenticated `git` remote write permission;
- authenticated `gh` with repository administration permission for default-branch mutation;
- Python 3.

If `gh repo edit ... --default-branch` is not authorized:
`STOP / DEFAULT_MIGRATION_NOT_EXECUTABLE`

Do not work around missing admin permission by moving refs.

## 4. Phase A — read-only preflight

From the admin clone:

```bash
set -euo pipefail

REPO="fahimahmedb/Quant-Trade"
ADMIN="/mnt/quant-data/quant/Quant-Trade"
BLUE="blue/master-v2-2026-09-20"
INDEX="governance/BRANCH_DELETE_READY_INDEX_2026-09-20.md"

cd "$ADMIN"

test "$(pwd -P)" != "/opt/quant"
test -f QUANT_NORTH_STAR.md

git fetch origin --prune --tags

echo "===== AUTH ====="
gh auth status

echo "===== REMOTE ====="
git remote -v

echo "===== LIVE BLUE ====="
git rev-parse "origin/$BLUE"

echo "===== WORKTREE ====="
git status --short

echo "===== DEFAULT BEFORE ====="
gh repo view "$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name'

echo "===== OPEN PRS ====="
gh pr list --repo "$REPO" --state open --json number,title

echo "===== OPEN ISSUES ====="
gh issue list --repo "$REPO" --state open --json number,title

echo "===== BRANCH COUNT BEFORE ====="
gh api "repos/$REPO/branches?per_page=100" --paginate --jq '.[].name' | tee /tmp/quant-branches-before.txt | wc -l
```

Expected current high-level state at preparation time:
- default = `claude/nasdaq-trading-model-design-h3mp4n`;
- open PRs = 0;
- open issues = 0 after organizational audit;
- live branches = 74 after creation of the frozen v4 and independent Astra v4 refs.

If the live state differs, do not assume failure. Record the delta and re-evaluate before mutation.

## 5. Phase B — parse and validate the delete-ready authority

The source of truth is the committed index, not a copied chat list.

```bash
python3 - "$INDEX" > /tmp/quant-delete-ready.tsv <<'PY'
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text()
rows = re.findall(
    r'^\| `[^\`]+\` \| `([^\`]+)\` \| `([0-9a-f]{40})\` \|$',
    text,
    flags=re.M,
)

if len(rows) != 34:
    raise SystemExit(f"DELETE_INDEX_COUNT_MISMATCH expected=34 got={len(rows)}")

for branch, sha in rows:
    print(f"{sha}\t{branch}")
PY

cat /tmp/quant-delete-ready.tsv
```

Now verify **all** refs before deleting **any**:

```bash
python3 - <<'PY'
import json
import subprocess
import urllib.parse

REPO = "fahimahmedb/Quant-Trade"
DEFAULT = subprocess.check_output(
    ["gh", "repo", "view", REPO, "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
    text=True,
).strip()

rows = []
with open("/tmp/quant-delete-ready.tsv") as fh:
    for raw in fh:
        sha, branch = raw.rstrip("\n").split("\t", 1)
        rows.append((sha, branch))

failures = []

for expected, branch in rows:
    remote = subprocess.check_output(
        ["git", "ls-remote", "--heads", "origin", f"refs/heads/{branch}"],
        text=True,
    ).strip()

    if not remote:
        failures.append((branch, "MISSING"))
        continue

    actual = remote.split()[0]
    if actual != expected:
        failures.append((branch, f"SHA_MISMATCH expected={expected} actual={actual}"))
        continue

    if branch == DEFAULT:
        failures.append((branch, "IS_DEFAULT"))
        continue

    encoded = urllib.parse.quote(branch, safe="")
    payload = subprocess.check_output(
        ["gh", "api", f"repos/{REPO}/branches/{encoded}"],
        text=True,
    )
    protected = bool(json.loads(payload).get("protected"))

    if protected:
        failures.append((branch, "PROTECTED"))

if failures:
    for branch, reason in failures:
        print(f"DELETE_PREFLIGHT_FAIL {branch} {reason}")
    raise SystemExit(1)

print(f"DELETE_PREFLIGHT_OK count={len(rows)}")
PY
```

Required result:
`DELETE_PREFLIGHT_OK count=34`

Anything else:
`STOP / RE-REVIEW`

## 6. Phase C — migrate repository default branch

Only after the read-only preflight is clean:

```bash
CURRENT_DEFAULT="$(gh repo view "$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name')"

echo "DEFAULT_BEFORE=$CURRENT_DEFAULT"

if [ "$CURRENT_DEFAULT" != "$BLUE" ]; then
    gh repo edit "$REPO" --default-branch "$BLUE"
fi

NEW_DEFAULT="$(gh repo view "$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name')"

echo "DEFAULT_AFTER=$NEW_DEFAULT"
test "$NEW_DEFAULT" = "$BLUE"
```

This changes repository navigation/admin metadata only.

It does not move Blue, P0 or Product refs.

## 7. Phase D — re-run delete preflight after default migration

Default migration changes one deletion safety condition.

Re-run Phase B exactly.

Do not skip it.

Required:
`DELETE_PREFLIGHT_OK count=34`

## 8. Phase E — physical deletion

Only after all 34 passed together:

```bash
set -euo pipefail

mkdir -p /tmp/quant-cleanup-evidence
LOG="/tmp/quant-cleanup-evidence/delete-$(date -u +%Y%m%dT%H%M%SZ).log"

while IFS=$'\t' read -r expected branch; do
    actual="$(git ls-remote --heads origin "refs/heads/$branch" | awk '{print $1}')"

    if [ "$actual" != "$expected" ]; then
        echo "ABORT_MOVED branch=$branch expected=$expected actual=${actual:-MISSING}" | tee -a "$LOG"
        exit 1
    fi

    echo "DELETE_BEGIN branch=$branch sha=$expected" | tee -a "$LOG"

    git push origin --delete "$branch" 2>&1 | tee -a "$LOG"

    remaining="$(git ls-remote --heads origin "refs/heads/$branch" | awk '{print $1}')"

    if [ -n "$remaining" ]; then
        echo "DELETE_VERIFY_FAIL branch=$branch remaining=$remaining" | tee -a "$LOG"
        exit 1
    fi

    echo "DELETE_OK branch=$branch sha=$expected" | tee -a "$LOG"
done < /tmp/quant-delete-ready.tsv

echo "DELETE_BATCH_COMPLETE" | tee -a "$LOG"
echo "LOG=$LOG"
```

The batch is intentionally fail-fast.

If a later deletion fails after earlier deletions succeeded:
- preserve the log;
- do not recreate deleted refs merely to make the batch look atomic;
- classify the remaining branch and continue only after Blue reviews the partial result.

## 9. Phase F — post-cleanup verification

```bash
git fetch origin --prune

echo "===== DEFAULT ====="
gh repo view "$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name'

echo "===== OPEN PRS ====="
gh pr list --repo "$REPO" --state open --json number,title

echo "===== OPEN ISSUES ====="
gh issue list --repo "$REPO" --state open --json number,title

echo "===== REMAINING BRANCHES ====="
gh api "repos/$REPO/branches?per_page=100" --paginate --jq '.[].name' \
  | tee /tmp/quant-branches-after.txt

echo "BRANCH_COUNT_AFTER=$(wc -l < /tmp/quant-branches-after.txt)"

echo "===== DELETE-READY SURVIVORS ====="
cut -f2 /tmp/quant-delete-ready.tsv | while read -r branch; do
    if grep -Fxq "$branch" /tmp/quant-branches-after.txt; then
        echo "UNEXPECTED_SURVIVOR $branch"
    fi
done

echo "===== CURRENT BLUE ====="
git ls-remote --heads origin "refs/heads/$BLUE"
```

If no concurrent branch creation occurs after this runbook revision, 74 - 34 = **40** branches should remain.

Do not use the count alone as proof. The exact branch list is authoritative.

## 10. Phase G — P0 non-mutation witness

This cleanup should never touch P0, but record that fact operationally:

```bash
echo "===== P0 SERVICE STATE (READ ONLY) ====="
systemctl show quant-sec-capture.service --no-pager \
  --property=ActiveState,SubState,Result,MainPID,InvocationID || true

echo "===== P0 MOUNT VIEW (READ ONLY) ====="
findmnt /opt/quant || true
findmnt /var/lib/quant-p0 || true

echo "No P0 start/restart/reset-failed/authorization/rematerialization executed by repository cleanup."
```

Do not issue service mutations from this runbook.

## 11. Branches explicitly NOT authorized for deletion by this batch

Current v4 refs are not in the delete-ready batch and must survive:
- `blue/p0-gate-a-v4-frozen-2026-09-20`;
- `astra/p0-gate-a-v4-independent-audit-2026-09-20`;
- `builder/p0-effective-unit-digest-stability-v4-2026-09-20`.


Among others:
- `claude/restaurant-stock-management-mvp-6oq43e` — retained by explicit owner request;
- `blue/master-v2-2026-09-20`;
- Builder v4;
- frozen Gate A v3;
- final Astra v3 audit;
- P14D long-horizon method branch;
- canonical Forward/Economic;
- integration-readiness;
- divergent falsifier/audit refs;
- stale former default branch itself, until a separate post-migration retirement decision;
- unique Product/recovery/scientific evidence refs.

## 12. Post-execution durable handoff

After execution Blue must commit a handoff containing:

- UTC execution interval;
- default before/after;
- Blue HEAD used for authority;
- delete index blob SHA;
- list/count deleted;
- any failures/partial execution;
- branch count/list after;
- open PR/issue counts;
- statement that P0 runtime/state was not mutated;
- evidence log digest if copied into a restricted evidence location.

Then update:
- `CURRENT_GOVERNANCE_STATE_2026-09-20.md`;
- `BRANCH_AUTHORITY_REGISTRY_2026-09-20.md`;
- `BRANCH_CLEANUP_PLAN_2026-09-20.md`;
- default-migration status.

## 13. Separate future action — branch protection

Do not mix platform-protection changes into the deletion batch.

After cleanup is complete, Blue should separately review branch/ruleset protection for critical retained refs.
