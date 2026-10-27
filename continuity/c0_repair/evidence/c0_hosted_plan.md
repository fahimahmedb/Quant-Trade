# C0 repair hosted exact-head plan

FACT: inspected child branch `codex/c0-confirmation-repair-20261027` at `d19b1237636d2311cd42f97f0b02feb55168347b`. No tracked files changed by this investigation.

## Achievable trigger and observation

Existing `.github/workflows/wave2-c2-c0-qualification.yml` triggers only on `builder/convergence-wave2-canonical-20261021` or workflow_dispatch. Most other dedicated qualification workflows are likewise pinned to other branches. The broad SEC gate includes builder/blue/astra, not codex, and PR triggers are irrelevant absent an authorized PR. Their absence on the child branch does not establish that GitHub Actions is unavailable.

Recommended smallest CI-only addition before freeze: `.github/workflows/c0-confirmation-repair-qualification.yml` with only `push.branches: [codex/c0-confirmation-repair-20261027]`, no paths filter, `permissions: contents: read`, one Ubuntu job and Python 3.12. Do not add pull_request, schedule, deployment, release, runtime state mutation, repository writes, workflow dispatch, secrets or capital hooks. `actions/checkout@v4` with exact `ref: ${{ github.sha }}` and `fetch-depth: 0`; `actions/setup-python@v5` version 3.12 follows repository standards. No test dependencies beyond stdlib needed for unittest suites. Set `PYTHONPATH=${{ github.workspace }}/src:${{ github.workspace }}` and `PYTHONDONTWRITEBYTECODE=1`.

Normal Git push of a commit containing this workflow to the named child branch should trigger it. This is a test/CI change within the repair mission; source branch remains frozen. Push normal fast-forward only. Avoid `[skip ci]` or other CI skip strings in candidate/attestation commit messages; no paths filter ensures evidence-only final attestation triggers the second exact-head run.

FACT: unlike PR-only `github_fetch_commit_workflow_runs`, the available generic `mcp__codex_apps__github_fetch` supports unfiltered event-independent GitHub Actions collection GETs. Tested successfully:

`https://api.github.com/repos/fahimahmedb/Quant-Trade/actions/runs?head_sha=d19b1237636d2311cd42f97f0b02feb55168347b&per_page=100`

Returned HTTP/tool success, JSON `total_count=0, workflow_runs=[]`. This is a point-in-time exact-SHA collection observation, not a forecast for future push runs and not proof hosted execution is unavailable. `github_get_commit_combined_status` returned `statuses=[]`; status contexts alone do not enumerate all check runs and cannot prove no Actions runs.

After candidate push use the generic URL with candidate exact SHA, inspect `workflow_runs` and select this workflow `path`, `head_branch`, `event=push`, exact `head_sha`, run ID/status/conclusion. `total_count` above page length requires pagination; latest first page does not establish exhaustive history. Then GET `/actions/runs/<run_id>` through generic fetch for full run identity/status. Available dedicated connectors can fetch run jobs, job logs, artifacts and artifact ZIPs. Do not call PR-only wrapper to assert push-run absence. No dispatch connector is available, but normal push avoids needing dispatch authority. No browser or token workaround is needed.

## Minimal job obligations

1. Record `GITHUB_SHA`, actual `git rev-parse HEAD`, Python version, run ID/attempt, branch, event, start clock. Require actual HEAD == GITHUB_SHA and `github.ref == refs/heads/codex/c0-confirmation-repair-20261027`.
2. Require source d19 SHA ancestry, fixed W2 ancestry, and remote frozen one-shot source branch remains at d19 SHA. The workflow can `git ls-remote origin refs/heads/codex/verified-autonomous-continuity-oneshot-20261027` without checking out/mutating that branch.
3. Before tests compare Git trees against d19 for production-state paths: `research/research_os/artifacts`, `assessments`, `events`, `hypotheses`, `legacy`, `receipts`, `runtime`, `sources`, `tasks` and `research/edge_lab` (if mission scope forbids any changes there). Git diff must be empty. This validates state identity without inspecting protected outcomes. Also compare `QUANT_NORTH_STAR.md` blob equality.
4. Run targeted existing C0 suite `python -m unittest tests.test_wave2_c2_scientific_adjudication -v`, root's exact new C0 repair test module(s), preserved selected hostile attack command, ordinary `python -m unittest discover -s tests -p 'test_*.py' -v`, Research OS `python -m unittest discover -s research/research_os/tests -p 'test_*.py' -v`. Root must bind actual new module names explicitly; do not use a pattern that can silently collect zero targeted tests. If the source mission has a reusable qualification runner, run it to align local/hosted commands.
5. Execute each command with captured stdout/stderr in `$RUNNER_TEMP/c0-qualification/`. Each record contains COMMAND, ENVIRONMENT, HEAD_SHA, START_TIME, END_TIME, RESULT, FAILURES, LOG_REF, EXIT_CODE; retain all failures and propagate nonzero job exit. Never classify a stale/unknown failure as PASS to make hosted green. Run suites even when another fails using an aggregation runner, then fail job at the end.
6. Always check actual HEAD still equals GITHUB_SHA and `git status --porcelain` empty after tests. Verify state-path tree identities again (or full worktree clean suffices for no local tracked mutation, but both is clearer). Compare source frozen remote again.
7. Emit test-only receipt with exact run identity/commit, command results, state equality, authority unchanged, no production writes and no outcome access; receipt must not claim whole-suite PASS unless all required commands succeeded. Write logs/receipt outside checkout. Upload with `actions/upload-artifact@v4`, `if: always()`, artifact name includes `${{ github.sha }}` and `${{ github.run_id }}`; `if-no-files-found: error`.

## Two-stage finalization

Candidate commit includes product changes, test logic, CI workflow, draft evidence/handoff. Require clean worktree, push/fetch exact remote SHA, run local+hosted same SHA. Evidence-only final attestation commit contains candidate conclusion and run IDs. Do not change workflow/tests/product in the attestation. Run local again and push attestation, observe new push-triggered run with final exact SHA. Fetch remote after conclusion and require remote head == final SHA; no post-final-run commits. Final run identity may remain external.

## Limits

Adding the trigger proves only workflow definition. Hosted availability becomes FACT only once push creates an observable run; qualification PASS requires completed successful exact-head run and all gates. GitHub Actions policy, billing/capacity, push app identity suppressing workflows or permissions may still block launch. If no run appears after bounded observation, report HOSTED_EXACT_HEAD_QUALIFICATION=NOT_AVAILABLE/UNKNOWN with exact timestamps and unfiltered query evidence, not PASS. If run starts but fails, retain the exact failing command/invariant and apply repair-scope/freeze law.
