# CP3 — maintenance compatibility after a durable automatic wake

The automatic queue-refill transaction succeeded at commit
`ad8dd8d20e02259dd590c85aa5f27fb8269b5cfe`; its task/event/receipt remain durable.
Actual OCI journal observation at 2026-10-20T00:14:43.719409Z then showed that
same service invocation ended with a failure after publication. Therefore a
healthy completed automatic service wake and final H24 RUNNING are not claimed.
Observation SHA256: `e95e575529c73f8fa2ed724db223f7f935e3a5d9d4d35d1ed598b73c91749d3b`.

The explicit maintenance invocation included `git gc --no-detach`. Git 2.43,
Ubuntu 24.04's baseline, does not support that option. Its exact option table is
verifiable at https://raw.githubusercontent.com/git/git/v2.43.0/builtin/gc.c.
The build executor's Git 2.52 accepts it, explaining why modern-Git tests alone
do not establish target compatibility. A separate Oracle detail probe retains
the actual VM version and final worker error; that proof must be checked before
declaring this the complete live repair.

The bounded fix removes the new option. Explicit `git gc` without `--auto`
already runs synchronously; the existing stable cache lock, two-week prune
retention and once-daily successful maintenance marker are preserved.
The existing real-Git restart test now exercises maintenance under the Git 2.43
option boundary, checks successful compaction and verifies it does not run twice
within the daily interval. It also verifies the completed task stays completed.
No extra test-discovery count or scientific result changes are required.

Builder validation: 52 tests PASS across queue replenishment, worker crash/race/
freeze recovery, current corpus/ASML preflight and economic readiness integration.
Exact-release Oracle/general CI and actual target deployment remain required.
The already-installed release is still `f138c980c94eea313fd77532c20857da5c02d3fe`;
the repair code SHA is the commit containing this checkpoint. No current pointer
or timer is silently changed by a builder Git push. All four authorities stay
false. Preserve the failed attempt; requalify the repaired release before launch.
