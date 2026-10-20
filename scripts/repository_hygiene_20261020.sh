#!/usr/bin/env bash
set -euo pipefail

# Quant-Trade repository hygiene — 2026-10-20
#
# Default mode is DRY RUN. To mutate remote refs:
#   APPLY=1 bash scripts/repository_hygiene_20261020.sh
#
# The script never deletes a unique/diverged branch tip unless that exact tip is
# first preserved by a verified archive tag. Branches that move after planning
# are skipped.

EXPECTED_REPO="fahimahmedb/Quant-Trade"
REMOTE="${REMOTE:-origin}"
APPLY="${APPLY:-0}"
STAMP="20261020"
PLAN_FILE="${PLAN_FILE:-branch-cleanup-plan-${STAMP}.tsv}"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

command -v git >/dev/null 2>&1 || fail "git is required"
git rev-parse --git-dir >/dev/null 2>&1 || fail "run from a Git clone"

remote_url="$(git remote get-url "$REMOTE" 2>/dev/null || true)"
case "$remote_url" in
  *github.com:fahimahmedb/Quant-Trade.git|*github.com/fahimahmedb/Quant-Trade.git|*github.com/fahimahmedb/Quant-Trade)
    ;;
  *)
    fail "remote '$REMOTE' does not look like ${EXPECTED_REPO}: ${remote_url:-<missing>}"
    ;;
esac

printf 'Refreshing remote refs and tags...\n'
git fetch "$REMOTE" --prune --tags

tmpdir="$(mktemp -d 2>/dev/null || mktemp -d -t quant-hygiene)"
trap 'rm -rf "$tmpdir"' EXIT INT TERM

keep_file="$tmpdir/keep.txt"
cat >"$keep_file" <<'EOF'
blue/master-v2-2026-09-20
builder/oracle-economic-loop-recovery-20261019
audit/forensic-checkpoint-20261019
builder/research-os-aggressive-architecture-20261015
builder/research-factory-core-v2
research/edge-lab-continuous
research/legacy-economic-reconciliation-20261015
research/design-v1
codex/test
builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08
claude/restaurant-stock-management-mvp-6oq43e
EOF

# Dynamically protect whatever the clone currently identifies as origin/HEAD.
origin_head="$(git symbolic-ref --quiet --short "refs/remotes/${REMOTE}/HEAD" 2>/dev/null || true)"
if [ -n "$origin_head" ]; then
  default_branch="${origin_head#${REMOTE}/}"
  if ! grep -Fqx "$default_branch" "$keep_file"; then
    printf '%s\n' "$default_branch" >>"$keep_file"
  fi
fi

branches_file="$tmpdir/branches.tsv"
: >"$branches_file"
while IFS=$'\t' read -r ref sha; do
  branch="${ref#refs/remotes/${REMOTE}/}"
  [ "$branch" = "HEAD" ] && continue
  printf '%s\t%s\n' "$branch" "$sha" >>"$branches_file"
done < <(git for-each-ref --format='%(refname)%09%(objectname)' "refs/remotes/${REMOTE}")

[ -s "$branches_file" ] || fail "no remote branches found"

# Resolve retained branch tips that actually exist.
keep_existing="$tmpdir/keep-existing.tsv"
: >"$keep_existing"
while IFS= read -r keep_branch; do
  [ -z "$keep_branch" ] && continue
  keep_ref="refs/remotes/${REMOTE}/${keep_branch}"
  if git show-ref --verify --quiet "$keep_ref"; then
    keep_sha="$(git rev-parse "$keep_ref")"
    printf '%s\t%s\n' "$keep_branch" "$keep_sha" >>"$keep_existing"
  else
    printf 'NOTE: keep branch does not currently exist: %s\n' "$keep_branch" >&2
  fi
done <"$keep_file"

[ -s "$keep_existing" ] || fail "none of the keep branches exist; refusing cleanup"

printf 'branch\texpected_sha\tclassification\twitness_or_archive\n' >"$PLAN_FILE"

while IFS=$'\t' read -r branch sha; do
  if grep -Fqx "$branch" "$keep_file"; then
    printf '%s\t%s\tKEEP\t%s\n' "$branch" "$sha" "$branch" >>"$PLAN_FILE"
    continue
  fi

  witness=""
  while IFS=$'\t' read -r keep_branch keep_sha; do
    if git merge-base --is-ancestor "$sha" "$keep_sha" >/dev/null 2>&1; then
      witness="$keep_branch"
      break
    fi
  done <"$keep_existing"

  if [ -n "$witness" ]; then
    printf '%s\t%s\tABSORBED\t%s\n' "$branch" "$sha" "$witness" >>"$PLAN_FILE"
  else
    short_sha="$(printf '%s' "$sha" | cut -c1-12)"
    archive_tag="archive/${STAMP}/tip-${short_sha}"
    printf '%s\t%s\tARCHIVE_THEN_DELETE\t%s\n' "$branch" "$sha" "$archive_tag" >>"$PLAN_FILE"
  fi
done <"$branches_file"

keep_count="$(awk -F '\t' 'NR>1 && $3=="KEEP" {n++} END {print n+0}' "$PLAN_FILE")"
absorbed_count="$(awk -F '\t' 'NR>1 && $3=="ABSORBED" {n++} END {print n+0}' "$PLAN_FILE")"
archive_count="$(awk -F '\t' 'NR>1 && $3=="ARCHIVE_THEN_DELETE" {n++} END {print n+0}' "$PLAN_FILE")"
total_count="$(awk 'END {print NR-1}' "$PLAN_FILE")"
unique_archive_tags="$(awk -F '\t' 'NR>1 && $3=="ARCHIVE_THEN_DELETE" {print $4}' "$PLAN_FILE" | sort -u | wc -l | tr -d ' ')"

printf '\nPlan written to %s\n' "$PLAN_FILE"
printf 'Remote branches observed : %s\n' "$total_count"
printf 'KEEP                     : %s\n' "$keep_count"
printf 'ABSORBED delete-ready    : %s\n' "$absorbed_count"
printf 'ARCHIVE_THEN_DELETE      : %s\n' "$archive_count"
printf 'Unique archive tags      : %s\n' "$unique_archive_tags"

if [ "$APPLY" != "1" ]; then
  printf '\nDRY RUN ONLY. Review %s.\n' "$PLAN_FILE"
  printf 'To apply: APPLY=1 bash scripts/repository_hygiene_20261020.sh\n'
  exit 0
fi

printf '\nAPPLY=1: beginning fail-closed remote cleanup.\n'

# Archive tags are created lazily and verified before each corresponding branch
# deletion. Multiple branches with the same tip naturally reuse one tag.
while IFS=$'\t' read -r branch expected_sha classification witness; do
  [ "$branch" = "branch" ] && continue
  [ "$classification" = "KEEP" ] && continue

  current_sha="$(git ls-remote --heads "$REMOTE" "refs/heads/${branch}" | awk 'NR==1 {print $1}')"
  if [ -z "$current_sha" ]; then
    printf 'SKIP_MISSING\t%s\t%s\n' "$branch" "$expected_sha"
    continue
  fi
  if [ "$current_sha" != "$expected_sha" ]; then
    printf 'SKIP_CHANGED\t%s\tplanned=%s\tcurrent=%s\n' "$branch" "$expected_sha" "$current_sha"
    continue
  fi

  if [ "$classification" = "ABSORBED" ]; then
    # Refresh the witness and re-prove ancestry immediately before deletion.
    if ! git fetch "$REMOTE" "refs/heads/${witness}:refs/remotes/${REMOTE}/${witness}" --quiet 2>/dev/null; then
      printf 'SKIP_WITNESS_FETCH_FAILED\t%s\t%s\n' "$branch" "$witness"
      continue
    fi
    witness_sha="$(git rev-parse "refs/remotes/${REMOTE}/${witness}")"
    if ! git merge-base --is-ancestor "$expected_sha" "$witness_sha" >/dev/null 2>&1; then
      printf 'SKIP_NO_LONGER_ABSORBED\t%s\t%s\n' "$branch" "$witness"
      continue
    fi
  elif [ "$classification" = "ARCHIVE_THEN_DELETE" ]; then
    archive_tag="$witness"
    remote_tag_sha="$(git ls-remote --tags "$REMOTE" "refs/tags/${archive_tag}" | awk '!/\^\{\}$/ && NR==1 {print $1}')"

    if [ -n "$remote_tag_sha" ] && [ "$remote_tag_sha" != "$expected_sha" ]; then
      printf 'SKIP_ARCHIVE_TAG_COLLISION\t%s\t%s\tremote=%s\n' "$branch" "$archive_tag" "$remote_tag_sha"
      continue
    fi

    if [ -z "$remote_tag_sha" ]; then
      if git show-ref --verify --quiet "refs/tags/${archive_tag}"; then
        local_tag_sha="$(git rev-parse "refs/tags/${archive_tag}")"
        if [ "$local_tag_sha" != "$expected_sha" ]; then
          git tag -d "$archive_tag" >/dev/null
        fi
      fi
      if ! git show-ref --verify --quiet "refs/tags/${archive_tag}"; then
        git tag "$archive_tag" "$expected_sha"
      fi
      if ! git push "$REMOTE" "refs/tags/${archive_tag}:refs/tags/${archive_tag}" >/dev/null; then
        printf 'SKIP_ARCHIVE_PUSH_FAILED\t%s\t%s\n' "$branch" "$archive_tag"
        continue
      fi
    fi

    verified_tag_sha="$(git ls-remote --tags "$REMOTE" "refs/tags/${archive_tag}" | awk '!/\^\{\}$/ && NR==1 {print $1}')"
    if [ "$verified_tag_sha" != "$expected_sha" ]; then
      printf 'SKIP_ARCHIVE_VERIFY_FAILED\t%s\t%s\texpected=%s\tgot=%s\n' "$branch" "$archive_tag" "$expected_sha" "${verified_tag_sha:-<missing>}"
      continue
    fi
  else
    printf 'SKIP_UNKNOWN_CLASSIFICATION\t%s\t%s\n' "$branch" "$classification"
    continue
  fi

  # Final branch-tip check immediately before deletion.
  final_sha="$(git ls-remote --heads "$REMOTE" "refs/heads/${branch}" | awk 'NR==1 {print $1}')"
  if [ "$final_sha" != "$expected_sha" ]; then
    printf 'SKIP_CHANGED_AT_DELETE\t%s\tplanned=%s\tcurrent=%s\n' "$branch" "$expected_sha" "${final_sha:-<missing>}"
    continue
  fi

  if git push "$REMOTE" ":refs/heads/${branch}" >/dev/null; then
    printf 'DELETED\t%s\t%s\t%s\n' "$branch" "$expected_sha" "$classification"
  else
    printf 'DELETE_FAILED\t%s\t%s\t%s\n' "$branch" "$expected_sha" "$classification"
  fi
done <"$PLAN_FILE"

printf '\nCleanup pass complete. Refresh and count remaining branches:\n'
printf '  git fetch %s --prune --tags\n' "$REMOTE"
printf '  git branch -r | grep -v -- "->" | wc -l\n'
printf '\nPreserve %s as the durable execution receipt before any second cleanup pass.\n' "$PLAN_FILE"
