# Quant System State

This file is the compact current state of the whole Quant project. It is updated at meaningful
milestones from actual evidence, not from intentions.

Read `QUANT_NORTH_STAR.md` before interpreting this file. `CHIEF_BRIEF.md` is generated
automatically from persistent state and carries the live numbers.

## Architectural state

Quant System V1 is implemented end to end in persistent paper/shadow mode. The planes named in
`SYSTEM_ARCHITECTURE.md` all exist in code, hold persistent state and are connected by the
Control Plane clock rather than by a script that runs them in order.

Package layout mirrors the planes:

| Module | Plane |
| --- | --- |
| `src/quant/clock.py`, `state.py`, `events.py`, `paths.py` | Control Plane |
| `src/quant/dataplane/` | Data Plane |
| `src/quant/factory/` | Research Factory |
| `src/quant/desk/` | Capital Desk |
| `src/quant/book/` | Persistent Book |
| `src/quant/learning/` | Learning / Memory |
| `src/quant/status/` | Status surface and Chief Brief |

The PR #7 and PR #9 primitives are reused rather than replaced: `ResearchTicket` carries research
lifecycle, and `PersistentQueue` / `ResearchTask` are now the Control Plane's durable work queue.

## What exists today

- a whole-system clock with boot/resume, durable run history, heartbeat, watchdog, pause/resume,
  fault isolation and bounded retry;
- a Data Plane with adapters, validation, fingerprints, committed provenance sidecars,
  availability tracking and dependency unblocking;
- a Research Factory with declared lanes, a discovery/validation/shadow point-in-time partition,
  a versioned strategy lifecycle, a multiple-testing budget and dead-work protection;
- the `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK` chain as six distinct, traced, stateful
  functions over an `OpportunityTicket`;
- two persistent ledgers: the authoritative capital Book and a zero-authority evaluation ledger;
- a learning loop that scores the system's own rejections and raises `BuildTask` capability gaps;
- a status surface and `CHIEF_BRIEF.md` rendered only from persistent state;
- 56 tests, an end-to-end restart demonstration with 27 assertions, and JSON schemas for the
  persistent state objects generated from the dataclasses with a drift test.

## Current data frontier

The repository is no longer data-starved for cross-sectional work. A real, credential-free
multi-asset panel is ingested, validated and committed:

- `us_sector_etf_daily`: 30,168 bars, 12 symbols, 2016-09-12 to 2026-09-11, 2,514 aligned
  sessions, from the public Yahoo Finance chart endpoint;
- `nasdaq_composite_daily`: the historical index export, normalized into the same schema.

Recorded caveats include that adjusted closes are restated retroactively for corporate actions,
that the endpoint is undocumented with no availability guarantee, and that consolidated daily
bars are not the venue-level quotes a real execution model would eventually need.

This acquisition unblocked the `statistical_arbitrage` lane, which the previous opportunity map
had ranked second and blocked for want of "a synchronized multi-asset point-in-time panel".

Three lanes remain genuinely blocked and are represented as blocked work with named dependencies
and open `BuildTask` records: `factor_residual`, `insider_filings`, `volatility_surface`.

## Current research evidence

Two lanes ran on the new panel. The second was promoted automatically by the first lane's
diagnosis, not by a human supplying the next idea.

Windows: discovery 2016-09-12 to 2022-03-08, validation 2022-03-09 to 2025-03-11, and a shadow
window from 2025-03-12 reserved for the desk and never visible to research.

| Expression | OOS net | OOS gross | Costs | Turnover | Beta | t | required t |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `xs_momentum_l21_z0.5_h1_b0` | -13.16% | -2.79% | 11.28% | 75x/yr | -0.070 | -0.97 | 3.08 |
| `xs_momentum_l21_z0.5_h5_b0.05` | -7.27% | -2.61% | 4.90% | 33x/yr | -0.063 | -0.49 | 3.20 |

**Both are rejected.** No strategy holds a tradable lifecycle state, so the capital Book has
never taken a position.

What the evidence actually says:

1. On the discovery window every one of the 24 declared daily expressions was gross-positive or
   near-flat and net-negative after 5bp one-way costs, at 92x to 410x annual turnover. The
   binding constraint was implementation, not signal direction.
2. The structural response — a holding period and a no-trade band — worked *mechanically*:
   turnover fell from 75x to 33x per year and modelled costs fell from 11.3% to 4.9%. It did not
   rescue the strategy, because out of sample the residual signal was gross-negative too.
3. Neither result is close to significant. After 36 declared expressions on one dataset the
   Bonferroni-adjusted bar is t >= 3.20; the best reached -0.49. These results are
   indistinguishable from search luck, in the unprofitable direction.
4. Beta attribution is reported on every result. Both expressions ran at |beta| < 0.07 against a
   benchmark that returned +35.9% over the same window, so essentially none of the outcome is
   disguised market exposure — the dollar-neutral construction did its job.

The honest conclusion: cross-sectional sector relative value, as expressed here, is not a source
of edge on this dataset, and the failure is not merely a cost problem.

## Current economic state

- Capital Book: NAV 1,000,000 USD, unchanged since inception, 0 fills, 0 positions, 378 sessions
  marked. `NO_TRADE` held for the entire shadow window because nothing was validated.
- Evaluation ledger (zero authority, counterfactual only): NAV 983,622, -1.64% over 378 sessions
  and 2,690 modelled fills, with 3,073 USD of modelled commission.
- Desk tickets: 451 booked, 301 no-trade, 2 risk-vetoed, 2 blocked.

Decision quality: both rejections were scored against what they would actually have done. Both
came out **UNDETERMINED** — the counterfactual loss is real but below the materiality band and
statistically indistinguishable from zero, so the system does not claim its rejections were
vindicated. There were no false rejects.

## Whole-system maturity

| Plane | State |
| --- | --- |
| Control Plane / Clock | **Implemented.** Boot/resume, due-work routing across planes, durable run history, heartbeat, watchdog, fault isolation, bounded retry, pause/resume, dead-work protection. |
| Data Plane | **Implemented for daily bars.** Registry, adapters, validation, fingerprints, committed provenance, availability-driven unblocking. No intraday, no point-in-time fundamentals, no corporate-action history. |
| Research Factory | **Implemented for one family.** Declared lanes, discovery/validation separation, adversarial falsification, multiple-testing budget, evidence-driven follow-up promotion. Breadth is still narrow: one signal family on one asset class. |
| Capital Desk | **Implemented.** Six distinct traced stages over an `OpportunityTicket`, execution modelled at the next open with spread, commission, square-root impact and ADV capacity truncation. |
| Persistent Book | **Implemented.** Durable fills, realized/unrealized P&L, NAV history, per-strategy attribution, restart-safe. Verified by tests and by the restart demonstration. |
| Learning | **Implemented for research and rejections.** Lessons, lane priorities, counterfactual scoring, `BuildTask` capability gaps. Decay and retirement transitions exist but have never fired, because no strategy has been tradable. |
| Build Plane | **Represented.** Capability gaps are first-class records; execution is still a human-triggered agent task. |
| Status UI | **Implemented as a text surface.** Every field is read from persistent state; nothing is mocked. |

## Known limitations

- One symbol is assumed to be owned by one strategy within a ledger; multi-strategy netting on
  the same symbol is not implemented.
- Cash earns no financing return, and shorts pay no borrow. Both are modelled as zero and are
  material to a real bankroll.
- The `DECAYING` and `RETIRED` transitions are implemented and tested but have never run on real
  evidence.
- The evaluation ledger's materiality band is a fixed fraction of initial capital rather than of
  capital actually at risk.
- The status surface is a text rendering, not an interactive control UI.

## Highest-value next actions

1. **Breadth, not depth.** One signal family on nine ETFs is too narrow a search to conclude
   anything about the Research Factory. The next lane should be structurally independent, not
   another parameterisation of the residual.
2. **Cost realism as a first-class model.** Costs decided both results. The execution model
   should be calibrated against something better than an assumed spread.
3. **A dataset that unblocks a ranked lane.** `factor_residual` and `insider_filings` are ranked
   above anything currently executable and are blocked purely on data.
4. **Exercise the decay path.** Until a strategy is tradable, `SHADOW -> ACTIVE_SHADOW ->
   DECAYING -> RETIRED` is untested against real evidence.

## Human boundary currently reached?

No. Nothing in the current frontier requires human authority. The blocked lanes need datasets
that are free but not yet written adapters for; the next research lane is choosable from
evidence. The system is `IDLE` with a named next action, not finished.
