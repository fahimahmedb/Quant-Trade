# F1 — CRYPTO-CARRY-001 — pre-registration and acquisition manifest

Status: **PROPOSED**, published before any outcome file is downloaded. Execution is blocked until (a) Codex's challenge window (`ATTENTE[EB2]`, 2026-10-08T16:30Z, plus one reminder) closes and (b) the harness is separately published, tested and frozen. Paper/shadow research only. No order, account, credential or capital.

Authority: Owner chat decision recorded in `Q30_OWNER_DECISION_2026-10-08.md` (public credential-free data for paper/shadow research); PR #22 comment `6061968640` (find a real edge); thresholds per `EDGE_SEARCH_BOARD_CLAUDE_ERRATUM_1_2026-10-08.md`.

## 1. Hypothesis and economic reason

H1: a long-spot / short-perpetual position held on a USDT-margined Binance perpetual while its trailing realised funding is high earns a **positive net return on capital** after fees, slippage, liquidation losses and the capital tied up in margin, in a window the project has never read.

Reason: levered retail longs pay funding to the short side; arbitrage capital is limited by margin and venue segmentation (He-Manela-Ross-von Wachter, arXiv 2212.06888; Schmeling-Schrimpf-Todorov). The paper reports the premium shrinking about 11% per year to 2024-03, and a secondary source (unverified) claims it turned negative in 2025. Both are reasons the sealed window is the real test.

Null: net mean daily return on capital ≤ 0 in the sealed window.

## 2. Data, source and terms

| Item | Value |
|---|---|
| Host | `https://data.binance.vision/` (public bucket, no credential) |
| Funding | `data/futures/um/monthly/fundingRate/{SYM}/{SYM}-fundingRate-{YYYY-MM}.zip` |
| Perp daily bars | `data/futures/um/monthly/klines/{SYM}/1d/{SYM}-1d-{YYYY-MM}.zip` |
| Spot daily bars | `data/spot/monthly/klines/{SYM}/1d/{SYM}-1d-{YYYY-MM}.zip` |
| Checksums | each zip has `{zip}.CHECKSUM` (sha256); verify before parsing |
| Symbol listing | S3 listing with `prefix=data/futures/um/monthly/fundingRate/` and `data/spot/monthly/klines/` (file and directory **names only**) |
| Terms | `ACQUISITION_TERMS_NOTES_2026-10-08.md`: CC BY-NC-SA 4.0, non-commercial research allowed, live proprietary trading prohibited. **A positive result cannot be promoted to live use on this dataset alone.** Raw files are not committed; manifests, hashes and derived statistics are. |
| User-Agent | `quant-research-paper-shadow/0.1` (no personal data) |
| Rate | at most 5 requests per second, sequential, retry with exponential backoff, stop on repeated 403/429 |

Universe candidates: symbols that appear in **both** listings with identical strings, quote asset USDT, excluding 1000-prefixed names with no identical spot string. Delisted symbols are included because the listing keeps them. The candidate list and its hash are published before any zip is downloaded.

## 3. Windows (fixed now)

- **Stage A, discovery:** funding and bars dated 2020-01-01..2023-12-31. Used only to select θ (below) and to prove the harness works.
- **Stage B, sealed test:** dates 2024-01-01..2026-09-30. **No Stage B file is downloaded or opened until Stage A has run, its result is published and its harness is frozen.** The harness reads Stage B once.
- 2026-10 is excluded (incomplete month).

## 4. Strategy (one rule, fixed; no parameter beyond θ)

Decision at 00:00 UTC of day t+1 using funding settled through the end of day t.

- Funding series: sum of realised funding-rate rows settled in each UTC day (rate × notional ratio 1; rows as published, any 1h/4h/8h interval handled by summing realised rows).
- Signal `s(i,t)` = mean of daily realised funding over days t−6..t, annualised ×365.
- Eligible at t: perp and spot daily bars exist for the previous 60 days, and the **spot** trailing-30-day median quote volume is at least 5,000,000 USDT (point-in-time, from the bars).
- Enter when eligible and `s ≥ θ`; exit when `s < θ/2` or not eligible. θ ∈ {5%, 10%, 20%} annualised (3 cells).
- Position: long spot, short perp, equal notional N. Capital per pair = (4/3)·N (spot fully paid plus 1/3 N margin held as idle USDT, zero interest).
- Weights: equal capital over active pairs, cap 10% of NAV per symbol; unused capital earns zero. NAV rebalanced daily to weights only on entry/exit (no daily rebalancing of drift, so no churn costs beyond entries/exits).
- Basis P&L: daily close-to-close of (spot return − perp return) on notional, plus funding received (or paid, if the sign reverses) on the notional.
- **Liquidation proxy:** if the perp daily **high** reaches 1.25 × the perp close on the entry day, the perp leg is closed at that level, the spot leg is sold at the next daily close, a 1% penalty on perp notional applies, and the symbol is barred for 30 days.
- **Costs (base):** spot taker 0.10%, perp taker 0.05% per side, plus slippage 2 bp per leg-side for the 20 symbols with the highest trailing-30-day spot volume that day and 10 bp otherwise. Entering and exiting each pay both legs. **Stress:** all fees and slippage ×2. These are ASSUMED standard-tier figures, not measured.
- No leverage on NAV beyond the margin structure above; no shorting spot (negative-funding carry is out of scope).

## 5. Statistic, gate and rejection rules

- Primary statistic: **net daily return on NAV** series `r_t` for the selected θ over the sealed window; annualised Sharpe and mean; t = mean / Newey-West standard error (7 lags).
- θ selection: the θ with the highest Stage A net Sharpe at base costs; ties → the larger θ. The sealed test is run for the selected θ **and the two others are reported** (they are not eligible to replace the selected cell).
- **Gate (family threshold, fixed):** `CONFIRMED` iff one-sided `t ≥ 2.539` (m = 3 cells, α_family = 0.05/3, `ERRATUM_1`) **and** the stress-cost mean is > 0 **and** at least half of the sealed calendar quarters have positive net return.
- Sealed window ≈ 1,004 days (2.75 years). Power statement (arithmetic, assumed i.i.d.): the minimum detectable annualised Sharpe at z = 2.539 is about 1.53; 80% power needs a true Sharpe of about 2.04. Target effect for exclusion: Sharpe 1.5 (below the literature's 2020–2024 figures, above zero).
- `REJECTED` iff not confirmed **and** the one-sided 95% upper bound `SR_hat + 1.645·(1/√T_years)` is below 1.5 (i.e. `SR_hat < ≈ 0.51`).
- Otherwise `INCONCLUSIVE_UNDERPOWERED`. No re-test at a laxer threshold; no extra cells.
- Non-gating reports: BTC/ETH only; per-year breakdown; share of P&L from the top 10 days; funding versus basis versus cost decomposition; maximum drawdown; number of liquidation events; Stage A versus Stage B Sharpe.

## 6. Integrity and harness requirements

1. Stage A and Stage B are separate harness runs. Stage B's candidate month list is published and hashed before any Stage B zip is fetched.
2. Every zip is checksum-verified; the manifest records URL, retrieval time (UTC), HTTP status, byte count, sha256 of the zip, row count and first/last timestamps; missing months are listed, never filled.
3. Raw-line date filtering **before** CSV parsing: no Stage B-dated row is parsed by Stage A.
4. The harness reads only the files named in the published manifest; the result directory is created beforehand; the result is written once in `x` mode; filesystem snapshots before/after; the persisted result is invalidated on any late repository mutation; `sys.dont_write_bytecode`; dependencies verified frozen.
5. Funding-interval switches (1h/4h/8h) are handled by summing realised rows; no annualisation of a single rate.
6. Universe selection uses only information dated ≤ t. No current exchange metadata is used.
7. Adversarial review by an independent agent before the single execution (Stage A and Stage B).
8. Negative results persist as `RESULT → LESSON → PRIORITY UPDATE → NEXT ACTION` in the work queue.

## 7. Known limits (disclosed)

Daily bars cannot represent intraday liquidation paths; the proxy is conservative on direction but coarse. Exchange-failure and withdrawal risk (FTX-type) are not in the sample. The effective sample is days, not symbols. A positive result is a research screen for shadow follow-up, not authority for the Book, and the dataset's licence forbids live proprietary use. A reversal expression (Codex P1) is **not** part of this registration.

---

# Revision 1 (supersedes any conflicting text above; written before any outcome data was read)

Source: independent adversarial review (no P0; ten P1 ambiguities, several P2). Arithmetic was re-verified: z = 2.539 / 2.773 (two-sided) / F2 2.128; window 1,004 days = 2.751 years; MDE Sharpe 1.53; 80% power needs 2.04; exclusion cutoff 0.51. Note from the review: power at a true Sharpe of 1.5 is only about 48%.

**R1. Funding-row timing.** The decision at the close of day t (00:00 UTC of day t+1) uses rows with timestamp ≤ that instant minus one second, i.e. through day t. A position entered at that instant earns only funding rows with timestamp **strictly greater** than the entry timestamp and **at or before** the exit timestamp. The 00:00:00 row at entry is not earned; the 00:00:00 row at exit is earned.

**R2. Portfolio mechanics.** Weight at entry = min(10%, 1/k) of current NAV, where k is the number of positions open after that day's entries; weights are **never resized**; the cap is checked at entry only. NAV compounds daily; days with no exposure are included in the return series with r = 0. Positions still open at 2026-09-30 are closed at that day's close with exit costs.

**R3. Ledger and liquidation.** Positions are held in coin quantities: spot quantity = perp quantity = q, fixed at entry, with perp notional N = weight × NAV × 3/4 (capital = 4/3 N). Daily P&L = q × (Δ spot close − Δ perp close) + funding, where funding = realised rate × q × that day's perp close (declared approximation of mark). Liquidation check starts with the first daily bar **after** the entry close, against `entry_perp_close × 1.25`. On a trigger day, perp P&L for that day is `−q × (1.25 × ref − previous perp close)` (replacing, not adding to, the close-to-close perp P&L), the spot leg is sold at that day's close with the spot fee and slippage, a 1% penalty on perp notional applies, and the symbol is barred for 30 days.

**R4. Standard error.** The gate uses `max(SE_NW(7 lags), SE_NW(21 lags))`. The reference distribution stays normal; it cannot be changed after observation.

**R5. Labels.** The "REJECTED" status is renamed `NOT_CONFIRMED_EXCLUDES_SR_1.5` and is computed with the same SE as the gate: `SR_hat + 1.645 · SE_SR < 1.5`, where `SE_SR = SE_mean / sd_daily × √365`. It means only that a Sharpe of 1.5 is excluded, not that no edge exists. Other outcomes: `CONFIRMED` (statistical screen against zero), `INCONCLUSIVE_UNDERPOWERED`.

**R6. Cash hurdle (reporting).** The gate remains a test against zero. The report headline also shows the mean excess over an assumed cash yield of 4.0% annualised (ASSUMED for 2024–2026, not verified), and states that a confirmed carry below that hurdle has no economic value after cost of capital. Any later discussion of promotion uses the excess figure.

**R7. Format safety.** Before freezing, the harness has unit tests with synthetic fixtures covering: second and microsecond/millisecond timestamps, files with and without header rows, funding intervals of 1/4/8 hours, missing days. It **fails closed**: an unrecognised timestamp magnitude, header, column count or checksum aborts the run without printing or persisting any statistic. An aborted run with no statistic is an infrastructure failure and is re-runnable after a fix published with its reason; any run that printed or persisted a statistic is an outcome read and is not re-runnable. No Stage B file is opened to inspect formats.

**R8. Warm-up.** The Stage B manifest lists the 2023-11 and 2023-12 funding and bar files as warm-up only. Trading is flat until 2024-01-01 and P&L counts only from that date.

**R9. Quarter criterion.** At least 6 of the 11 calendar quarters in the sealed window must have positive net return; a quarter with zero exposure counts as not positive.

**R10. Terms.** The primary Binance Vision terms text is re-read at freeze time and its sha256 recorded; the earlier "permitted non-commercial" reading comes from a summary and is not relied on until then. If the repository is public, derived statistics carry the CC BY-NC-SA attribution.

**P2 dispositions.** (a) Report the exposure fraction (share of days with at least one open position) for each cell; a cell with exposure under 10% of days in Stage B is flagged `DEGENERATE_EXPOSURE` and is not eligible for `CONFIRMED`. (b) The Bonferroni m = 3 is conservative (only the cell selected on Stage A is eligible, so 2.539 is not a required minimum for a single pre-selected cell); the stricter value is kept on purpose. (c) Exact string matching between spot and perp symbols can pair different assets after a rename or relaunch; the bias is disclosed, and 1000-prefixed names are excluded, which removes many high-funding memecoins. (d) A spot delisting while the perp lives is not modelled beyond the 30-day bar. (e) Only complete 7-day funding windows (7 daily sums) generate a signal. (f) The BNB fee discount is not assumed. (g) The claim that the premium turned negative in 2025 and the 11%/year shrinkage figure are literature claims not verified by this project's reviewers.

**R11. Implementation notes fixed before freezing (written before any outcome data was read).** (a) Funding rows are bucketed to the nearest minute (`slot = round(ts / 60 s) × 60 s`) to absorb millisecond jitter before applying R1; the decision-time signal for day t uses slots in `[D_{t−6}, D_{t+1})`, earned funding for day d uses slots in `(D_d, D_{d+1}]`. (b) New-entry weight = `min(10%, 1/k, available capital ÷ (NAV · new entries))`, where available capital = NAV − Σ entry capital of open positions; this prevents over-allocation when entries are staggered. (c) The liquidation day earns no funding (partial-day funding is not knowable). (d) Eligibility: both spot and perp daily bars exist for each of the previous 60 days, and the spot 30-day median quote volume is at least 5,000,000 USDT; the 20 highest-volume eligible symbols that day use the low slippage. (e) Sealed-window statistics use the days 2024-01-01..2026-09-30 inclusive, with 11 calendar quarters; `CONFIRMED` requires 6 of 11 positive quarters.
