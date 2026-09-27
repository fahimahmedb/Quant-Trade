# H-005 result: fade new Hyperliquid perp listings (verdict: REJECTED)

Paper/shadow research only. Data: HL public info API (meta incl. 56 delisted, daily candles,
hourly fundingHistory), raw gzipped with sha256 provenance in `data/fast_rail/h005/` (8.9 MB,
641 manifest lines). Data horizon: last candle 2026-09-21. Reproduce: `python3 research/fast_rail/h005/run.py`.

**Events.** Venue start = 2023-02-26 (first traded candle). 4 coins traded that day (ATOM, BTC, ETH,
MATIC) are excluded. Listing day = first candle with trades; the zero-volume index backfill that HL
shows before some coins' first trade is ignored (120 events carry such a prefix, mostly 2023 majors).
230 events: discovery 126 (2023-03-04..2024-04-29), validation 69 (2024-04-30..2025-06-10),
untouched 35 (2025-06-26..2026-09-08). No returns and no funding computed for the untouched set.

**Discovery (6 trials, conservative t = min(event t, listing-week clustered t)).** Every expression
had a negative mean: H7 none -6.2% (t -2.0), H7 btc -5.0%, H14 none -9.1% (t -2.1), H14 btc -4.3%
(t -1.0), H30 none -17.1% (t -2.7), H30 btc -7.7%. Medians are positive (+1..+13%); losses come from
squeezes. Best by t: **H14, long-BTC hedge**.

**Validation (H14 hedged, N=69, 37 listing weeks).** Mean net +6.4%/event (median +16.6%, hit 67%);
t_event 0.95, t_cluster 0.86 vs required_t 2.64 (trials 6, no reruns). 2x costs: +6.0%.
Halves: -2.7% / +15.2%. Top 10% of events = 98% of net P&L.
Unhedged short H14: +6.0% vs short-BTC same windows -0.7% (diff +6.6%, t 0.89).
Capacity: median 1% of median daily notional over hold = $42k; 77% of events >= $10k.
Worst event: GRASS (listed 2024-10-28) -262% hedged (gross short -290%); IP -235%, HYPE -90%.
Mean funding received by shorts: -0.56% (shorts paid on net).

| check | result |
|---|---|
| t >= required_t (2.64) | FAIL (0.86) |
| mean > 0 at 2x costs | pass |
| both validation halves > 0 | FAIL |
| top 10% < 50% of gains | FAIL (98%) |
| unhedged beats short BTC | pass (not significant) |
| capacity >= $10k at 1% ADV | pass (median) |

**Verdict: REJECTED.** The typical listing drifts down, but the distribution has unbounded right-tail
squeezes that dominate the mean in discovery and make validation fragile. A -262% event implies
liquidation for any unlevered-but-margined short; real outcomes would be capped at posted margin
with forced exit, which this model does not simulate.

Caveats: OI caps on new listings are unknown (not in the public API; could block or cap entry).
Coins removed entirely from `meta` (renames) would be missing (survivorship risk, unquantified).
Funding notional drift uses the day's open. Early 2023 events are mostly majors (SOL, BNB, AVAX),
not hype launches. The untouched 15% remains available for a new pre-registered hypothesis
(e.g. tail-capped/stop-loss variant) that must be declared before looking at it.
