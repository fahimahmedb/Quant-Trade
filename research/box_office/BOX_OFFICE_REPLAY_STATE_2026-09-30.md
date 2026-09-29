# BOX OFFICE STRICT-TIMESTAMP REPLAY — state / checkpoint file

REAL_CAPITAL_AUTHORIZED = FALSE. Research only.
BRANCH: `claude/relaxed-johnson-mqca45` (the harness-assigned single branch; `research/box-office-strict-replay-2026-09-30` was not created)
STATUS: IN_PROGRESS
PHASE: CP1 — universe + news archives + pre-registration frozen; replay not yet run

## Resume protocol (after a token or session cut)

1. `git fetch origin claude/relaxed-johnson-mqca45 && git checkout claude/relaxed-johnson-mqca45`, then read this file and `PREREGISTRATION_BOX_OFFICE_REPLAY_2026-09-30.md`. **The pre-registration is frozen: do not edit its rules.** Anything added after it is EXPLORATORY.
2. Find the last checkpoint marked DONE below and continue from the next one. Every checkpoint writes its outputs under `research/box_office/data/` and is committed and pushed immediately.
3. Scripts run from any working directory (`cd research/box_office/data` first). Raw inputs are frozen as `*.json.gz`; do not re-fetch them unless a file is missing, because the live APIs drift.

## Checkpoints

| CP | Content | Output | State |
|---|---|---|---|
| CP1 | Box-office universe (226 events since 2025-10-01), Variety + Deadline box-office archives (WP REST API, `date_gmt`/`modified_gmt`), pre-registration | `data/events_full.json.gz`, `data/variety_bo.json.gz`, `data/deadline_bo.json.gz`, `scripts/*.py`, pre-reg | DONE |
| CP2 | Contemporaneous taker trades for every bracket of U1+U2 (data-api `/trades`, takerOnly) | `data/trades_u.json.gz` | TODO |
| CP3 | PIT info table: per film-weekend × release, with value, source, availability time and strictness flag | `data/pit_releases.csv` | TODO |
| CP4 | Replay lanes A–D × R1/R2 × E1/E2/E3, quarterly decay, flips, capacity | `data/replay_trades.csv`, `data/replay_summary.json` | TODO |
| CP5 | Report + final state + verdict | `BOX_OFFICE_STRICT_TIMESTAMP_REPLAY_2026-09-30.md`, this file | TODO |

## Facts established so far (CP1)

- Fees: Polymarket docs say taker fee = C × rate × p × (1−p). The culture rate is 0.05 with a 25% maker rebate, under Fee Structure V2 dated 2026-03-30 in the changelog. Per market, the `feesEnabled`/`feeSchedule` fields decide; markets from before the rollout show `feesEnabled=False`.
- Templated regime: gamma shows templated events already on the 2025-10-10 weekend (Tron: Ares Lower Strikes, Soul on Fire), a week before Agent 7's 2025-10-14 T0. They are outside the frozen period.
- U1 candidates: 104 resolved 3-day opening events (siblings included). U2 candidates: 72 resolved 3-day nth-weekend events.
- PIT sources:
  - Variety posts carry an exact `date_gmt`. They cover only about half the weekends (26 previews posts, 27 Saturday posts in 12 months), and Sunday posts are often modified on Monday (REVISABLE).
  - Deadline keeps one re-dated article per weekend, with labelled sections (FRIDAY AM / MIDDAY / PM, SATURDAY AM, SUNDAY AM, MONDAY AM). Some sections are overwritten by later write-throughs, so those releases are lost.
- The Wayback Machine (`web.archive.org`) is blocked by the environment egress policy. `archive.org/wayback/available` works but returns no content.
