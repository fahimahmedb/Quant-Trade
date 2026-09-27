# H-004 result: REJECT (signal)

Kalshi maker P&L from being the counterparty of every taker print. Measurement only: no quotes, no orders, no keys.

- **Frozen design** (`h004_config.py`, committed bf1be8d before any outcome was read). Weather = KXHIGH NY/CHI/MIA/AUS/DEN/LAX/PHIL. Other = KXINX, KXNASDAQ100, KXEURUSD, KXUSDJPY, KXWTI. Event dates 2025-09-25..2026-09-23, sampling every 7th day (52 dates).
- **Data**: `data/fast_rail/h004/`, 9.3 MB gz. It holds 7,992 settled markets and 2,325,555 prints from the public API (historical and live endpoints). `manifest.json` has the sha256 of each file, and every market record carries its URL, fetched_at and the sha256 of its raw pages.
- **Unit**: event-day = (series, date), weighted by contracts. Splits by date: discovery 29 dates, validation 15 dates, untouched 8 dates (2026-07-30..09-17, never loaded).
- **Fee**: the API reports `fee_type=quadratic` (taker fee only) for every series, so the actual maker fee is 0. We still charged 0.0175·P·(1−P) per contract, unrounded, and also tested 2× that fee.
- **Trials**: 4 (no reruns). required_t = 2.498.

| Expression | Discovery mean net (c) / t | Validation mean net (c) / t | Validation N |
|---|---|---|---|
| weather / settlement (best on discovery) | +0.75 / 4.87 | **−0.10 / −0.55** | 105 |
| weather / markout 300 s | +0.06 / 0.70 | −0.19 / −1.26 | 105 |
| other / settlement | +4.06 / 2.74 | −1.60 / −1.24 | 75 |
| other / markout 300 s | +3.74 / 2.47 | +0.15 / 0.15 | 66 |

Verdict on the best discovery expression (weather/settlement) in validation:
- Failed: t ≥ req, mean > 0, mean > 0 at 2× fee, both halves > 0 (−0.13c and −0.06c), top-decile share < 50% (it is 92%).
- Passed: capacity. 10% of printed maker notional is about $2.9M per month.
- Pooled over contracts (instead of the mean of per-event-day averages), validation is +$85k net over 20.2M contracts, about +0.42c per contract. Nearly all of it comes from a few event-days, and the equal-weight event-day mean is negative.

**Adverse selection** (validation, prints that have a causal prior mid):
- Weather: the half-spread proxy is 2.55c, but the 300 s markout is only 0.15c, so adverse selection takes about 2.4c (~94%) of the quoted edge.
- Other series: 1.85c proxy vs 0.12c markout.
- The discovery-period weather settlement edge (+0.75c) did not persist into Apr–Jul 2026.
- Markout is diagnostic only. Settlement P&L is the only realisable P&L.

**Queue-priority caveat**: being the counterparty of every print overstates what a new maker would earn. A newcomer sits at the back of the queue and gets a selected subset of fills, which is more toxic. A pass would only ever have been a "measurement CANDIDATE". This test failed even before that haircut.

**Residual risks**:
- Weekly sampling. The 7-day step rotates the weekday.
- The half-spread proxy (last taker-yes and last taker-no price within 600 s) is not a real book mid.
- Maker fee assumed rather than charged. It is 0 today, and a 0 fee does not rescue the validation.
- The equal-weight mean and the pooled figure disagree in sign, which is a sign of fat tails.

Reproduce: `python3 research/fast_rail/h004/fetch.py` (resumable, per-series atomic files), then `python3 research/fast_rail/h004/h004.py`, which writes `results.json`.
