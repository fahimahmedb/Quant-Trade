# Box Office strict-timestamp replay: falsification of SPI-1 / E7-F

Date: 2026-09-30 (UTC). Research only. No orders were placed.
**REAL_CAPITAL_AUTHORIZED = FALSE.**
Branch: `claude/relaxed-johnson-mqca45`. Frozen rules: `PREREGISTRATION_BOX_OFFICE_REPLAY_2026-09-30.md`, committed at `e9dbf11`, before any P&L. Addendum 1 was committed at `acc469c` and Addendum 2 at `3e1e609`, both also before any P&L.
Inputs: Agent 4 `claude/magical-ramanujan-wsktyr@501093d` (SPI-1), Agent 7 `claude/exciting-planck-uq6rir@10c025d` (E7-F, M3).

```text
BOX_OFFICE_REPLAY = NEGATIVE
```

**Question.** Could a *new observer* using only information verifiably public at the time have earned positive net executable returns in Polymarket box-office brackets? The period is the templated regime, weekends of 2025-10-17 → 2026-09-25.

**Answer.** No. The pre-registered primary rule is to buy the bracket implied by the latest public figure and hold it to resolution. It has a **negative mean net return in all four opening-weekend lanes (A–D)**. The sign is the same under every pre-registered sensitivity: E2 first-fill price, E3 +1¢, +15 min and +180 min entry, Variety REVISABLE rows admitted, the 0.05 fee on all markets, no price cap, and the R2 boundary margin.

The loss mechanism is the one Agent 4 flagged:
- when the implied bracket is cheap (≤ 0.95), it is cheap because the figure sits near a bracket edge;
- the estimate→final revision (or a rounded press figure) then flips the bracket often enough to erase the carry.

When the figure is safely inside a bracket, the bracket already trades ≥ 0.95 by the anchor. There is nothing left to buy.

---

## 1. Universe (mechanical, no survivor selection)

- **Source.** gamma `tag_slug=box-office` ∪ `series_slug=box-office-openings`, 226 events created since 2025-10-01. Frozen as `data/events_full.json.gz` and `data/universe_raw.json.gz`.
- **U1, primary.** 3-day opening-weekend bracket events: **104 resolved events (544 brackets) = 85 resolvable film-weekends**. Sibling "Lower/Higher strikes" events are included, and the film-weekend is the unit of inference.
- **U2, secondary.** 3-day nth-weekend bracket events: **72 events (349 brackets) = 67 film-weekends**.
- **Excluded by rule:**
  - 4/5-day openings, opening-day, total-gross and #1-film events;
  - Primetime, which is still unresolved;
  - "Michael" 5th weekend, closed without a 0/1 resolution;
  - one malformed duplicate-listing event (In the Grey, id 478038; its sibling 481326 stays);
  - the two 2025-10-10 templated events (Tron: Ares Lower Strikes, Soul on Fire). They show that the template regime began one week before Agent 7's 2025-10-14 T0, and they fall outside the frozen period.
- **Market data.** Every contemporaneous **taker** fill on every bracket, from data-api `/trades` (takerOnly):
  - 454,188 fills over 1,000 markets;
  - 396,692 fills inside the Wed–Tue weekend windows (`data/trades_window.json.gz`);
  - two Avatar brackets hit the 10k offset cap, and their weekend window is still covered.
- **Fees.** The Polymarket docs give taker fee = C × rate × p × (1−p). Culture rate is 0.05 (Fee Structure V2, changelog 2026-03-30), applied per market from `feesEnabled`/`feeSchedule`. 48% of the replayed trades are fee-bearing. There is no maker fee. Taker rebates are ignored (conservative).

## 2. Point-in-time information timeline

| Release | Public mechanics | Strict source and availability time | U1 film-weekends with a strict figure |
|---|---|---|---|
| T_thursday_preview → A | previews + post-previews 3-day projection, Friday morning | Deadline "FRIDAY AM" section (available by Fri 12:00 PT); Variety post published Friday, STRICT if unmodified at anchor | 25 / 85 |
| T_friday_actual → B | Friday estimate + 3-day projection, Friday afternoon/evening | Deadline FRIDAY MIDDAY/AFTERNOON/PM sections (by 17:00 / 23:59 PT) | 54 / 85 |
| T_saturday_estimate → C | Friday actual + revised 3-day, Saturday morning | Deadline SATURDAY AM (by Sat 12:00 PT); Variety Saturday post, STRICT | 43 / 85 |
| T_sunday_studio_estimate → D | studio 3-day estimates, Sunday morning | Deadline SUNDAY AM (by Sun 12:00 PT); Variety Sunday post, STRICT | 64 / 85 |
| T_final_actual | Monday actuals | Deadline MONDAY section; The Numbers / BOM | used only via resolution |
| T_resolution | UMA / Polymarket | gamma outcomePrices | 85 / 85 |

- **Archives.** Deadline and Variety WordPress REST APIs, with `date_gmt` and `modified_gmt` for every post: 769 Deadline and 435 Variety box-office posts, frozen in `data/*_bo.json.gz`.
  - **Deadline** re-dates and rewrites one article per weekend, but keeps labelled earlier sections. A value's availability is the **end** of its labelled Pacific window. Sections overwritten by a later write-through are lost, and nothing is imputed.
  - **Variety** posts carry exact timestamps. A post is STRICT only if unmodified by the anchor.
- **Revision history is observable and matters.**
  - Variety's Sunday posts are routinely modified on Monday: median 7.9 h after publication, and 92% after one hour. Headlines are overwritten with Monday actuals. Example: Chainsaw Man was headlined "$18 Million" while the Sunday estimate was $17.2M.
  - Primary therefore uses only LABEL and STRICT rows, and REVISABLE rows appear only in the sensitivity run.
- **Extraction.**
  - `scripts/digest_lanes.py` produces lane-tagged snippets.
  - Six independent workers adjudicated them under pre-reg Addendum 1, giving `data/pit_releases.csv` (612 rows, 342 with a value).
  - QA: 340/342 values reproduce from the quoted span, and the 2 exceptions were checked valid. A random 12% sample was checked by hand with no error.
- **Wayback Machine** (`web.archive.org`) is blocked by this environment's egress policy, so there is no snapshot-level revision history. Coverage losses from this are counted, not filled.

## 3. Rules (frozen) and anchors

- **R1 (primary).** At the anchor, buy YES of the bracket containing the signal value W; an exact boundary maps up, per the market rules. Skip if the executable price is > 0.95. Hold to resolution.
- **R2.** Same as R1, but W must be ≥ 2.5% inside both bracket edges.
- **Anchors (ET):** A Fri 16:00, B Sat 09:00, C Sat 16:00, D Sun 16:00. Robustness entries at +15 min and +180 min.
- **E1 (primary) executable price.** VWAP of real **YES-buying taker fills** in (anchor, anchor+60 min]: BUY YES at p, or SELL NO at q read as YES at 1−q through mint matching. The window is extended to 180 min if empty, and there is no trade if it is still empty.
- **E2** is the first such fill; **E3** is E1 + 1¢.
- **Return per $** = (payoff − p − fee) / (p + fee), averaged within each film-weekend. There is a cluster bootstrap (10k draws, seed 20260930) and Holm correction over 4 lanes.

## 4. Results by lane (U1 opening weekends, R1-E1, film-weekend clusters)

| | A previews→Fri | B Friday→Sat | C Saturday est.→Sun | D Sunday est.→final |
|---|---|---|---|---|
| PIT signal / executable evidence / traded (of 85) | 25 / 20 / **18** | 54 / 47 / **39** | 43 / 36 / **34** | 64 / 53 / **27** (31 had a leg already > 0.95) |
| event-level trades | 21 | 40 | 35 | 29 |
| gross return / $ | −52.5% | −31.3% | −11.1% | −21.4% |
| fees / $ | 1.3% | 1.0% | 1.0% | 0.4% |
| **net mean / $** | **−53.3%** | **−31.7%** | **−12.0%** | **−22.0%** |
| 95% cluster-bootstrap CI | [−86.6, −10.9] | [−60.2, −1.0] | [−41.3, +20.3] | [−49.6, +9.3] |
| median | −100% | −100% | +10.3% | +7.0% |
| p25 / p75 | −100 / −100 | −100 / +37.4 | −100 / +37.9 | −100 / +15.5 |
| positive fraction | 27.8% | 38.5% | 55.9% | 59.3% |
| worst loss / best | −100% / +212% | −100% / +268% | −100% / +271% | −100% / +265% |
| concentration (top-3 share of \|P&L\|) | 25% | 14% | 19% | 29% |
| flip rate (signal bracket ≠ final), traded | 72% | 62% | 44% | 41% |
| flip rate, all mapped events (price-agnostic) | 70% | 44% | 30% | **17%** |
| median entry price | 0.24 | 0.45 | 0.46 | 0.82 |
| share of entries ≥ 0.85 | 6% | 10% | 12% | 44% |
| capacity proxy: YES-buy taker USD in first 60 min (median) | $6 | $19 | $23 | $94 |
| capacity proxy: YES-buy taker USD, anchor → next anchor (median) | $367 | $655 | $2,480 | $5,269 |
| Holm-adjusted one-sided p (mean > 0) | 1.0 | 1.0 | 1.0 | 1.0 |

Sensitivities (U1 net mean / $; each column is one of the pre-registered alternatives):

| Lane | E2 first fill | E3 +1¢ | +15 min | +180 min | +REVISABLE | fee 0.05 on all | no price cap | R2 margin 2.5% |
|---|---|---|---|---|---|---|---|---|
| A | −52.8% | −54.2% | −53.3% | −37.9% | −47.7% | −53.5% | −47.6% | −59.3% (n 13) |
| B | −30.4% | −33.0% | −31.0% | −36.5% | −31.7% | −32.7% | −21.8% | −19.0% (n 22) |
| C | −9.7% | −13.6% | −8.8% | −20.4% | −16.9% | −12.7% | −14.2% | −6.8% (n 16) |
| D | −20.1% | −23.3% | −22.9% | −14.5% | −21.2% | −22.3% | −7.9% (n 53) | −0.3% (n 7) |

**Secondary U2 (nth weekends), R1-E1:**
- B: −25.4% (n 22).
- C: +4.1% (n 16, CI [−34, +40]).
- D: +6.4% (n 26, CI [−19, +34], median +12.1%, positive 81%, the one −100% flip dominating).

Nothing reaches significance. U2-D and U2-C R2 (+29%, n 6) are **EXPLORATORY** observations, not survivors. Both are tiny, both fall in the secondary universe, and U2-D's 2026Q3 mean is −12%.

**Reading.**
1. **Lane A** (previews) is structurally a lottery. The post-previews projection lands in the final bracket only ~30% of the time, and the market's 0.24 median already overpays.
2. **Lanes B/C.** The market is *better* than the press projection: the traded implied bracket loses on 44–62% of film-weekends.
3. **Lane D.** Sunday estimates are right 83% of the time at event level, and the market knows it. In 31 of 53 film-weekends with executable evidence, at least one implied leg is already above 0.95 by Sun 16:00 ET, i.e. ~4 h after Deadline's label window. The residual cheap cases are boundary cases, and they flip 41% of the time.
4. **Estimate-accuracy vs P&L accounting.** A "correct estimate" is not a win. Examples: Dog Stars was estimated at $8M with the edge at 8, and the final was < 8; Young Washington was $20.8M with the final 18–20; Forgotten Island was $12.8M against a 13 line, and the final was 13–16.

## 5. Decay (the identical rule, per quarter; U1 R1-E1 net mean / $, n)

| Quarter | A | B | C | D | Median weekend taker volume, U1 (market-only) | Winner price at D anchor (market-only) |
|---|---|---|---|---|---|---|
| 2025Q4 | −57.7% (6) | −21.9% (7) | −33.6% (10) | −73.3% (4) | $73.8k | 0.97 |
| 2026Q1 | −58.4% (3) | +5.2% (10) | −31.0% (3) | −34.3% (9) | $120.6k | 0.87 |
| 2026Q2 | −74.9% (6) | −50.3% (12) | +6.1% (15) | −7.2% (6) | $103.7k | 0.96 |
| 2026Q3 | +3.9% (3) | −53.0% (10) | −12.0% (6) | +6.2% (8) | $28.4k | 0.81 |

- **Absorption time.** It is not shortening, because it was already short at the start. No lane has a significant trend: Spearman z for net is −0.19 to +1.47, and for entry price −1.74 to +0.53. This matches Agent 7's M3 finding of no absorption speed-up. There was nothing to decay *from*: the strict-timestamp rule is negative from 2025Q4 onward.
- **Return.** There is no rule-level return to decay. The quarterly signs are noise around a negative or ~0 mean, and no quarter is significantly positive.
- **Volume and capacity.** The median U1 weekend taker volume fell ≈ −76% from 2026Q2 to 2026Q3 ($104k → $28k). U2 went from $69k to $22k. The capacity proxy in the first 60 min after an anchor is tens to hundreds of dollars.
- **Recent quarters.** In 2026Q3, lanes A and D are positive on 3 and 8 film-weekends, with CIs spanning −100% to +200% and −59% to +94%. This is noise, and it is not a surviving edge.

## 6. Reconciliation with the receipts (Agent 4)

The receipts are real: the wallets are net-positive in `user-pnl`. The strict replay shows those gains are **not reproducible by a timestamp-verifiable public-information rule**. Plausible sources are outside this test:
1. **Speed inside the first hours.** The first public print (Deadline/X at ~6–9 AM PT) comes before our verifiable availability, which is the label-window end at noon PT. That speed is not verifiable here, and it is not a "slow public information" edge.
2. **Boundary judgement and two-sided making.** These wallets sell overpriced adjacent brackets, act as makers, and earn rebates. That is a different economic object from the public-information taker rule.
3. **Survivorship.** The receipts were selected from the leaderboard.

## 7. Largest uncertainties

1. **Timestamp conservatism.** A label-end availability of noon PT, plus a 1 h anchor gap, means the strict observer is hours behind the fastest public reader. The test says nothing about a sub-hour "first print" observer. That variant would be a speed edge, and it is not verifiable historically without Wayback or social-feed archives, both unavailable here.
2. **Power.** There are 18–39 traded film-weekends per U1 lane. The CIs are wide: C's upper bound is +20%, D's +9%. The verdict rests on every point estimate being negative, which is the pre-registered NEGATIVE clause, not on tight bounds.
3. **Execution proxy.** E1 comes from actual taker fills, not the book. Because first-hour fill volume is tiny (median $6–$94), some E1 prices rest on a handful of small prints. E2 and E3 give the same sign.
4. **PIT coverage.** Lane A covers only 25/85 film-weekends, which is data-limited on its own; the other lanes cover 43–64/85. Losses come from Deadline write-throughs overwriting Saturday sections and from digest truncation (17 rows). No value was imputed.

## 8. Candidate rule and cheapest prospective falsification

- **Surviving rule: none.** No lane or rule survives in U1, so nothing is proposed for a frozen prospective experiment on the slow-public-information hypothesis.
- **Only open variant: "first-print speed".** If Quant ever wants to test it, the cheapest check is a **paper-only capture** over 8 weekends of ~2–4 films each:
  - poll Deadline and Variety WP `modified_gmt` and the X/RSS first prints every 2 min;
  - snapshot Polymarket books (asks + depth) at T+2, 5, 15 and 60 min after each release;
  - falsify if the implied bracket's executable ask at T+5 min, net of fee and the historical flip rate for that lane (§4), is ≤ 0 in expectation.
- This is a speed or engineering edge with a capacity of tens to hundreds of dollars per release. Under the North Star, the expected value is ≈ nil at small size, so it is **not recommended ahead of other rails**.

## 9. Reproducibility

`research/box_office/scripts/`:
- `fetch_events.py`, `build_universe.py`, `parse_universe.py`: the universe;
- `fetch_news.py`: the archives;
- `fetch_trades.py`, `compact_trades.py`: the trades;
- `sections.py`, `digest_lanes.py`, `extract.py`, `merge_pit.py`: the PIT extraction;
- `replay.py [--rev|--offset=N|--fee-all]`: the replay;
- `absorption.py`: market-only diagnostics.

All data is frozen under `research/box_office/data/`. The replay is deterministic given the frozen files.
