# AGENT 7 — EDGE ARCHAEOLOGY / DECAY — state file

Date: 2026-09-29 (UTC). External research + public-API measurement + validation-latency audit only.
**REAL_CAPITAL_AUTHORIZED = FALSE. LIVE_TRADING_AUTHORIZED = FALSE.** No orders, wallets, credentials, bots or strategy code.

STATUS: DONE
PHASE: COMPLETE (deliverable, data, scripts, independent integrity review applied, pushed)
BRANCH: `claude/exciting-planck-uq6rir` (harness-assigned; used instead of `research/agent7-edge-archaeology-decay-2026-09-29`; no other branch created)
CURRENT_HEAD: the commit that last touched this file (verify `git log -1` = `git rev-parse origin/claude/exciting-planck-uq6rir`)

Deliverable: `research/recus_2026-09/agent7_edge_archaeology_decay.md`. Data + scripts: `research/recus_2026-09/agent7_data/`.

## CASES_COMPLETED (12 case cards + 7 controls)

| ID | Case | Terminal status |
|---|---|---|
| E7-A | Polymarket Weather | B DECAY_COMPARABLE_TO_VALIDATION |
| E7-B | polymm / b00k13 esports MM | C REAL_BUT_NOT_ACTIONABLE |
| E7-C1 | Polymarket liquidity rewards (T4) | H INACCESSIBLE_FOR_SMALL_QUANT (incumbent rent on a persistent, discretionary subsidy) |
| E7-C2 | Polymarket maker rebates | H (the "13× collapse" is a single-recipient discontinuity) |
| E7-D | Settlement liquidity 0.999 | A DURABLE_BEYOND_VALIDATION (premium tick-floored; economics tail-dominated) |
| E7-E | NegRisk / complete-set arbitrage | C |
| E7-F | Box office | D PERSISTENCE_UNKNOWN (no decay measured in 12 months) |
| E7-G | Tweet counts (+ mentions sub-control) | C (large 2025 edge); residual E |
| E7-H | Hyperliquid HLP | C |
| E7-I | Kalshi maker economics | H (US-only) |
| E7-J | Numerai Classic legacy → v3 | F MECHANISM_CHANGED_NEW_EXPERIMENT_REQUIRED |
| E7-K | Metaculus AI benchmark | E CURRENTLY_DECAYING_BUT_STILL_TESTABLE |
| X1–X7 | 39.59 M$ arb (G), closed-P&L stars (G), HL small MM (H), HL user vaults (G), passive LP (G), mentions (C), funding carry (C) | — |

REAL_BUT_NOT_ACTIONABLE (C) count: 6.

## SOURCES_CHECKED
- Quant: `QUANT_NORTH_STAR.md`; reorientation checkpoint `0f8f2d1`; Agents 1–6 at the mission-named heads (deliverables + state files); Weather V1 spec `726070a`, Astra `e1cf4ca`, Fable V2 memo `5760ffa` (latency facts only); fast rail `claude/new-session-0ydmkg` (`TWO_SPEED_RESEARCH_PROPOSAL.md`, `FAST_RAIL_STATE.md`, `registry.jsonl`); repo git history.
- Public data (MEASURED): Hyperliquid `vaultDetails`; Polygon logs of Polymarket rebate payers (13 dates); Polymarket `data-api` (activity, trades, closed-positions), `user-pnl-api`, gamma events/markets, CLOB `prices-history` (152 box-office events; 1,223 NYC/London weather events; 1,499 markets / 29,160 near-certain fills in 8 windows); Numerai GraphQL `roundDetails` (rounds 250–1365).
- External archaeology (three bounded workstreams): Polymarket docs/changelog/help centre; arXiv 2508.03474, 2608.00666, 2605.31431, 2510.14435, 2111.09192, 2208.06046; Kalshi replication repo; GitHub first-commit dates of public repos (polymm, poly-maker, poly-market-maker, neg-risk-ctf-adapter, uma-ctf-adapter, clob-client, simmer-sdk, metac-bot-template, numerai docs); press (The Block, CoinDesk, Decrypt, DL News, Cryptopolitan, KuCoin/Odaily); practitioner blogs (kacho.io). Wayback Machine unreachable.

## KEY_EMPIRICAL_FINDINGS
1. Statistical latency (months–years) dominates engineering latency (hours–weeks) by ≈ 10×; Quant's own fast rail recorded the same ("le goulot est le forward").
2. Receipt-first discovery is late: median edge age at discovery ≈ 20 months; principal decay already happened before discovery in 5 of 8 dated cases.
3. Decay onset preceded the first detailed public disclosure in 6 of 6 measurable competitive cases (median lead ≈ 6 months, range 2–11): disclosure is lagging/endogenous; no case shows publication-caused decay.
4. HLP return half-life 5.1 months (95% CI 4.0–7.2); elasticity to vault size −0.98 (dilution).
5. The Polymarket rebate "13× collapse" is one non-trading recipient (165.3 M$, 2026-01-16 → 09-10); all other recipients' pool −30% in September.
6. Box office: no absorption speed-up over 12 months; Sunday estimates priced within ≈ 3 h; prospective validation ≈ 9–22 months for +10%/$.
7. Weather: launch-quarter favourite bias (−30% to −35%, ECE 0.038) gone by 2025Q3; NYC same-month Brier 0.769 → 0.664; first-cohort decay from 2025-05; ≥ 4 venue-mechanics changes in 8 months.
8. Settlement ≥ 0.999: gross = tick floor (0.100%) in all 8 windows over 21 months; pooled naive-window net −0.115% from in-play sports "0.999" losers.
9. Numerai v3 begins at round ≈ 1343 (2026-08-28); payout rules changed 5 times in 5.6 years.
10. Tweet-count family volume −87% from its 2026-01 peak.

## OPEN_UNCERTAINTIES
- Weather forecast-skill decay not measured (deliberately outside the Weather rail); only NYC/London measured.
- Box office: structural delay vs undiscovered niche not discriminable with 12 months.
- Settlement: true post-determination tail rate (disputes/flips) and newcomer queue share.
- Cause of the dominant rebate recipient's stop; exact dynamic-tick activation date; January-2026 rebate share (Wayback unreachable).
- SF = 2 in the decay-aware gate is a derived heuristic, not calibrated.
- Gamma `volume` is unaudited (used for direction only).

## NEXT_ACTION
BEST_NEXT_DECAY_AWARE_RESEARCH_ACTION: run A4's strict-timestamp box-office replay over the full templated regime (2025-10-14 → now), reported per quarter, as both falsification and decay series. Pre-registered follow-ups already owned by others: A6 cohort C (2026-10-29), Numerai first 20 v3 rounds, A5 settlement census (restrict to post-determination fills). No further Agent 7 action.
