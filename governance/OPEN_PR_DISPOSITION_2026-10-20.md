# OPEN PR DISPOSITION — 2026-10-20

Authority: repository-hygiene preparation for the V1 -> V2 transition.

Purpose: remove stale PRs from the active project surface without erasing their commits or scientific/governance meaning. Closing a PR is not deletion of its commits and is not a scientific verdict. Exact head tips are preserved by the branch-cleanup archive policy before branch refs are later removed.

## Current disposition

All open PRs observed during the cleanup audit are historical/non-current and are closed as repository-routing noise. Their content remains reconstructable through Git history and, for branch tips later removed, archive tags plus the cleanup receipt.

| PR | Head | Exact observed head | Disposition | Reason |
|---|---|---|---|---|
| #21 | `claude/new-session-z4pdlx` | `0f9cb618997173155860afe6941e02cf20833481` | CLOSE / ARCHIVE | governance proposal from September; not current routing authority |
| #22 | `team/weather-v4-a2-coordination-2026-10-08` | `5a992b031ee2ecf996fc9c258f02907ee807a5af` | CLOSE / ARCHIVE | coordination channel explicitly marked `NE PAS FUSIONNER`; historical mailbox, not integration authority |
| #23 | `builder/f1-decision-integrity-repair-2026-10-08` | `9f1d5ba92cf808dd2d6020d2918116947d8ed1d9` | CLOSE / ARCHIVE | bounded historical F1 repair; evidence must remain reconstructable |
| #24 | `builder/f1-persistent-stage-a-2026-10-08` | `a0a07c12a8fbb6e9bff59fd19bbed0da06c15040` | CLOSE / ARCHIVE | historical acquisition/evidence step in stacked F1 chain |
| #25 | `builder/f1-stage-a-execution-2026-10-09` | `0b0f5b416f7c958b763216450d5889feea692cc3` | CLOSE / ARCHIVE | historical Stage A result/selection evidence |
| #26 | `builder/f1-sealed-stage-b-capture-2026-10-09` | `ea9d2d0e0e057199bb168249c963acbc88e89de5` | CLOSE / ARCHIVE / SCIENTIFIC_MEMORY | preserves the negative Stage B economic result; closing must never be read as erasing the rejection |
| #27 | `research/f2-primary-terms-decision-2026-10-09` | `e7344cfda865b987e57c0d0ad8eb37f4f164cf9e` | CLOSE / ARCHIVE | F2 permission decision is historical bounded evidence |
| #28 | `research/technical-signals-literature-2026-10-10` | `e42d4924a33efa78bab97939d654424cc1501fb8` | CLOSE / ARCHIVE | frozen exploratory EURUSD proxy harness; no current execution authority |
| #29 | `builder/live-lab-3d-full-build-20261015` | `6076774f52ca2e619caaab57fb6a278f47608349` | CLOSE / ARCHIVE | isolated UX/3D experiment; useful historical implementation reference but not the V2 trunk |

## Safety interpretation

- `CLOSE` means remove from the active review queue.
- `ARCHIVE` means preserve exact head reachability before eventual branch-ref deletion.
- `SCIENTIFIC_MEMORY` means the result remains part of project knowledge, including negative results.
- No PR in this table is being merged by this cleanup.
- No close action grants economic, prospective, real-capital or live-trading authority.

## Future rule

The one-shot cleanup script must dynamically discover currently open PR head branches and protect them from branch deletion. This table only disposes the nine PRs observed at this checkpoint; a new PR opened later is not implicitly covered by this decision.
