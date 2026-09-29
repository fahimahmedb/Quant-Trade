# Box Office strict-timestamp replay: pre-registration (frozen before any P&L computation)

Frozen: 2026-09-29 ~22:55 UTC, committed **before** trades were joined to information releases or any return was computed.
The rules below come from public release mechanics, bracket mechanics and Agent 4's hypothesis (SPI-1). None was chosen from historical P&L.
Anything added after this commit is labelled **EXPLORATORY**.

REAL_CAPITAL_AUTHORIZED = FALSE. Research only. No orders placed.

## 1. Universe (mechanical)

- Source: gamma `events?tag_slug=box-office` ∪ `events?series_slug=box-office-openings`, created on or after 2025-10-01 (`scripts/fetch_events.py`, `build_universe.py`, `parse_universe.py`).
- **U1 (primary):** negRisk bracket events on one film's **3-day opening weekend** (Fri–Sun, dates parsed from the rules text). The weekend Friday falls in the frozen period **2025-10-17 → 2026-09-25**. Each event must be resolved with exactly one winning bracket, and every bracket must parse. Sibling events ("Lower/Higher Strikes") are included. The unit of inference is the **film-weekend**: siblings are clustered and averaged, so each film-weekend gets equal weight.
- **U2 (secondary):** nth-weekend 3-day bracket events, same period and filters. Lanes B/C/D only (no previews).
- Excluded by construction and listed in the report: 4/5-day openings, opening-day, total-gross, #1-film, other non-bracket events, and unresolved or ambiguous events (e.g. Primetime still open; "Michael" 5th weekend closed without a 0/1 resolution). Also excluded are the two templated events on the 2025-10-10 weekend (Tron: Ares Lower Strikes, Soul on Fire), which fall before the frozen period.

## 2. Public information releases (point-in-time)

| Release | Public mechanics | Sources |
|---|---|---|
| T_thursday_preview | Studios/Comscore report Thursday previews Friday morning; press prints them with an updated 3-day projection | Deadline "FRIDAY AM" section; Variety "…in Previews" post |
| T_friday_actual | Friday estimate incl. previews + 3-day projection, Friday afternoon/evening PT | Deadline "FRIDAY MIDDAY/AFTERNOON/PM/NIGHT" sections |
| T_saturday_estimate | Friday actual + revised 3-day projection, Saturday morning PT | Deadline "SATURDAY AM/…" sections; Variety Saturday post |
| T_sunday_studio_estimate | Studio 3-day estimates, Sunday morning PT | Deadline "SUNDAY AM" section; Variety Sunday post |
| T_final_actual | Monday actuals | Deadline "MONDAY" section; The Numbers / BOM (resolution source) |
| T_resolution | Polymarket/UMA resolution | gamma outcomePrices |

Availability time (strict):
- **Variety post:** `date_gmt`. The content counts as known at anchor t only if `modified_gmt ≤ t` (STRICT). Otherwise it is flagged REVISABLE and used only when a Deadline section of the same release agrees within 2% (CORROBORATED).
- **Deadline section:** Deadline re-dates and rewrites one article per weekend but keeps labelled earlier sections. The availability time is the **end** of the labelled window, in PT: `AM` → 12:00 PT; `MIDDAY/AFTERNOON` → 17:00 PT; `PM/NIGHT/EVENING` → 23:59 PT; a bare day label → 23:59 PT that day. A section overwritten by a later write-through is **lost**: no value is invented, and the release is counted as missing PIT coverage.
- Value = the film's 3-day figure stated in that release (point, or midpoint of a stated range). A later revised value is never used for an earlier release.
- Wayback Machine is blocked by this environment's egress policy, so no snapshot-based revision history is available.

## 3. Lanes and fixed anchors (America/New_York)

| Lane | Signal (latest release available at anchor) | Entry anchor | Fallback |
|---|---|---|---|
| A previews → Friday | post-previews 3-day projection | **Fri 16:00 ET** | none (no trade) |
| B Friday actual → Saturday | Friday midday/PM 3-day projection | **Sat 09:00 ET** | none |
| C Saturday estimate → Sunday | Saturday-AM 3-day projection | **Sat 16:00 ET** | none |
| D Sunday estimate → final | Sunday studio estimate | **Sun 16:00 ET** | none |

Every entry is held to resolution (primary economics). A mark-to-next-anchor absorption diagnostic is reported but not used for the verdict.
Robustness anchors (reported, never selected): entry at +15 min and +180 min relative to the primary anchor.

## 4. Rule family (small, predeclared)

- **R1 buy-implied (primary):** at the anchor, buy YES of the bracket that contains the signal value W, in every event of the film-weekend. A value exactly on a boundary maps to the higher bracket (the market rule). No trade if the executable price is > 0.95.
- **R2 buy-implied-with-margin:** same as R1, but only when W lies ≥ 2.5% (of W) inside both bracket edges. This guards against estimate→final boundary flips.

## 5. Execution and fees

- **E1 (primary executable price):** VWAP of contemporaneous taker fills that *bought YES* of that bracket in (anchor, anchor+60 min]. This covers taker BUY on the YES token at p, and taker SELL on the NO token at q, read as YES at 1−q (a resting NO bid is an effective YES ask via mint matching). If the window is empty, extend to +180 min (flagged). If that is empty too, the trade is "no executable evidence" and counts against coverage, not as a return.
- **Fee:** taker fee = shares × rate × p × (1−p), with rate taken from the market's `feeSchedule` when `feesEnabled` (culture rate 0.05, Fee Structure V2 from 2026-03-30), else 0. Sensitivity: rate 0.05 on every trade.
- **Return per $:** (payoff − p − fee_per_share) / (p + fee_per_share), with payoff = 1 if the bracket resolved YES, else 0.
- **Capacity proxy:** USDC of YES-buy taker fills in (anchor, anchor+60 min] and in (anchor, next anchor].
- **Sensitivities:** E2 = the first YES-buy fill after the anchor; E3 = E1 + 0.01.

## 6. Statistics

Per lane × rule, all computed on film-weekend clusters:
- N, gross mean, fee mean, net mean, median, p25/p75, positive fraction, worst loss;
- concentration (the top-3 film-weekends' share of absolute net P&L);
- estimate→final flip rate (signal bracket ≠ resolved bracket);
- executable price at entry (median, share ≥ 0.85);
- capacity proxy;
- a 95% cluster bootstrap CI (10,000 draws, seed 20260930).

Quarterly: identical rule in 2025Q4 / 2026Q1 / 2026Q2 / 2026Q3, with no per-quarter tuning. Trends: Spearman ρ versus date for the entry price and net return.

## 7. Verdict rule (predeclared)

- **POSITIVE_FALSIFICATION_SURVIVOR:** some lane under R1-E1 has mean net > 0 with a Holm-adjusted (4 lanes) one-sided cluster-bootstrap p < 0.05, AND its 2026Q2+Q3 mean net > 0, AND the result survives E3 (+1¢).
- **NEGATIVE:** no lane under R1-E1 has a positive point estimate, OR every lane's 95% upper bound is < +3% per $.
- **INDETERMINATE_POWER_LIMITED:** neither of the above, with PIT+execution coverage ≥ 50% of U1 film-weekends in at least one lane.
- **INDETERMINATE_DATA_LIMITED:** coverage < 50% of U1 film-weekends in every lane.

## Addendum 1: value-extraction protocol (frozen 2026-09-29 ~23:45 UTC, still before any P&L)

This addendum makes §2–§3 operational; it changes none of their rules.
- Lane blocks: `scripts/digest_lanes.py` tags each source block with the lane it can feed.
  - Deadline sections: FRIDAY + AM → A; other FRIDAY → B; SATURDAY + AM → C; SUNDAY + AM → D. SATURDAY/SUNDAY PM sections become available after their anchor and are unused.
  - Variety posts: the lane whose anchor window (previous anchor, anchor] contains `date_gmt`. The post is flagged STRICT if `modified_gmt ≤ anchor`, else REVISABLE.
- Value: the film's own 3-day (Fri–Sun) figure in that block. A range gives its midpoint; "$X+ / north of $X" gives X (flag PLUS); "under $X" is unusable.
- Never used: comparables, daily grosses, previews amounts, global/overseas figures, running totals, budgets.
- Priority within a lane: (1) the Deadline section of that lane with the latest availability ≤ anchor, preferring its chart "3-day" line over prose when the two differ; (2) Variety STRICT; (3) Variety REVISABLE, flagged. The primary replay uses only (1)+(2). Sensitivity: (1)+(2)+(3).
- A "Saturday numbers" chart embedded inside a SUNDAY AM section is not a Sunday estimate, and is not usable for lane C, because it was only verifiably available at the Sunday label.
- Manual adjudication writes one row per film-weekend × lane to `data/adjudicated_part*.csv`. Rows with no usable release are kept with an empty value (NO_RELEASE). A random ≥10% of rows is re-checked by the lead against the digest.
