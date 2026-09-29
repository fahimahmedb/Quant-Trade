# BOX OFFICE STRICT-TIMESTAMP REPLAY — state

REAL_CAPITAL_AUTHORIZED = FALSE. Research only. No orders were placed.
BRANCH: `claude/relaxed-johnson-mqca45`. This is the harness-assigned single branch; `research/box-office-strict-replay-2026-09-30` was not created.
STATUS: DONE
PHASE: CP5 done — report + state pushed
CURRENT_HEAD: the commit that last touched this file (`git log -1 -- research/box_office/BOX_OFFICE_REPLAY_STATE_2026-09-30.md`)

```text
BOX_OFFICE_REPLAY              = NEGATIVE
BOX_OFFICE_RECEIPTS            = PROBABLE_RECENT_CANDIDATE (unchanged; receipts real)
BOX_OFFICE_REPRODUCIBLE_EDGE   = NOT_REPRODUCED (strict public-information taker rule negative in every U1 lane)
BOX_OFFICE_DECAY_STATE         = NOT_APPLICABLE_NO_RULE_EDGE (no rule-level edge in any quarter; volume -76% Q2->Q3)
REAL_CAPITAL_AUTHORIZED        = FALSE
```

## Summary

| Item | Value |
|---|---|
| Period | weekends Fri 2025-10-17 → 2026-09-25 (templated regime; note that it actually began on the 2025-10-10 weekend, and those 2 events fall outside the frozen period) |
| N events | U1 104 opening-weekend events (544 brackets) = 85 film-weekends; U2 72 nth-weekend events (349 brackets) = 67 film-weekends |
| N trades | market side: 454,188 taker fills pulled, 396,692 inside weekend windows. Replay: 189 event-level simulated entries under R1-E1 (U1+U2, all lanes), 266 with executable evidence |
| PIT coverage (U1, strict figure / executable / traded) | A 25/20/18 · B 54/47/39 · C 43/36/34 · D 64/53/27 (of 85) |
| Net by lane (U1, R1-E1, mean / $, 95% CI) | A −53.3% [−87, −11] · B −31.7% [−60, −1] · C −12.0% [−41, +20] · D −22.0% [−50, +9]. Medians −100 / −100 / +10 / +7%. Fees 0.4–1.3% / $ |
| Robustness | same sign under E2, E3 (+1¢), +15/+180 min, +REVISABLE, fee-all, no-cap, R2 margin (D R2 −0.3%, n 7) |
| Flip accounting | signal-bracket≠final: A 70%, B 44%, C 30%, D 17% of mapped events. Among traded (cheap) entries: 72 / 62 / 44 / 41% |
| Quarterly decay (U1 R1-E1) | A −58/−58/−75/+4% · B −22/+5/−50/−53% · C −34/−31/+6/−12% · D −73/−34/−7/+6% (Q4'25→Q3'26). No significant trend (\|z\| ≤ 1.74). Absorption was already fast at regime start |
| Recent quarter (2026Q3) | U1 A +3.9% (n 3), B −53.0% (n 10), C −12.0% (n 6), D +6.2% (n 8, CI [−59, +94]). Noise, not an edge |
| Capacity | YES-buy taker USD in the first 60 min after an anchor: median $6–$94. From anchor to next anchor: $0.4k–$5.3k. Median U1 weekend taker volume $104k (Q2) → $28k (Q3), about −76% |
| Largest uncertainty | the strict observer is hours behind the first public print (label-window-end availability; Wayback blocked). A sub-hour "first print" speed variant is untested and unverifiable historically |
| Candidate rule surviving | NONE |
| Exploratory only | U2-D (nth-weekend Sunday estimate) +6.4% (n 26, CI [−19, +34]); U2-C R2 +29% (n 6). Not survivors |
| Cheapest prospective falsification | only for the untested speed variant: 8 weekends of paper capture, with 2-min polling of first-print timestamps plus book snapshots at T+2/5/15/60 min. Falsify if the T+5 ask is ≥ fair value after the lane flip rate. Not recommended ahead of other rails (capacity ≈ tens to hundreds of $ per release) |
| REAL_CAPITAL_AUTHORIZED | FALSE |

## Checkpoints

| CP | Content | State |
|---|---|---|
| CP1 | universe, news archives, pre-registration (`e9dbf11`) | DONE |
| CP2 | taker trades (`data/trades_window.json.gz`) | DONE |
| CP3 | PIT releases: digests, 6-worker adjudication, QA, `data/pit_releases.csv`. Addenda 1 and 2 frozen before P&L | DONE |
| CP4 | replay primary + sensitivities: `data/replay_trades*.csv`, `data/replay_summary*.json`, `data/absorption_market_only.json` | DONE |
| CP5 | report `BOX_OFFICE_STRICT_TIMESTAMP_REPLAY_2026-09-30.md` + this state | DONE |

## Resume protocol (if anything must be re-run)

Check out the branch. `cd research/box_office/scripts && python3 replay.py` reproduces the primary run from the frozen data. Add `--rev`, `--offset=15`, `--offset=180` or `--fee-all` for the sensitivities. Do not edit the pre-registration; any new rule is EXPLORATORY.

## Process notes

- A digest-writer bug (file re-truncated per weekend) was caught by the first adjudication worker. The digests were regenerated and every part was re-adjudicated. No output from the corrupted files was used.
- The lane-A Variety window was narrowed to Friday-published posts, so pre-weekend tracking no longer counts as a post-previews signal. This was done before any P&L.
- One malformed event (In the Grey, id 478038, duplicate zero-volume listings) was excluded mechanically.

## NEXT_ACTION

Record SPI-1/E7-F as `REPLAY_NEGATIVE` in the research registry and stop spending on slow-public-information box-office rules. Revisit only if a new market mechanism appears (e.g. new bracket templates, a fee change, or a resolution-source change) or if a first-print capture rail already exists for other markets.
