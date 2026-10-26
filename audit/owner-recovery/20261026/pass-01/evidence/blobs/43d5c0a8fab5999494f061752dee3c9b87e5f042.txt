# H-003 pre-registration details (written before any outcome was computed)

Grid is fixed by `research/fast_rail/registry.jsonl` (H-003): yes_price_max {0.05, 0.10, 0.20}
x entry {24h, 1h} before market close_time = 6 trials.

## Sampling rule (outcome-blind, fixed before fetching markets)
- Series (KX-prefixed, long history, outcome not influenceable by traders):
  weather daily highs KXHIGHNY KXHIGHCHI KXHIGHMIA KXHIGHAUS KXHIGHDEN KXHIGHLAX KXHIGHPHIL (120 events each);
  indices KXINX KXINXU KXNASDAQ100 KXNASDAQ100U, crypto KXBTC KXBTCD KXETH KXETHD (60 events each);
  macro KXFED KXCPI KXCPIYOY KXPAYROLLS KXU3 KXGDP (up to 120 events each).
- Excluded: sports (close_time is set well after the game, so T-1h/T-24h quotes are post-outcome
  and stale), politics/elections/mentions/companies/entertainment (outcomes a participant can
  influence; compliance tags `event_participant`, `oracle_or_resolution_influence`).
- Per series: list all settled events; take the N with the lowest sha256("H-003|" + event_ticker).
- Per event: binary markets with result in {yes, no}; if > 25 markets, keep the 25 with the lowest
  sha256("H-003|" + market_ticker). Hash order is independent of outcomes and prices.

## Entry / quote rule
- entry_ts = close_ts - H*3600. Use the hourly candle with the largest end_period_ts <= entry_ts;
  it must end within 24h of entry_ts (else stale -> no trade). Never a candle closing after entry.
  (Amended before any outcome computation: historical candles are sparse -- emitted only in hours
  with quote/trade activity -- so the original 3h staleness cap would drop quiet-but-quoted markets.)
- Quote valid only if 0 < yes_bid and yes_ask < 1 and yes_bid <= yes_ask. Otherwise no trade.
- Signal: YES mid = (yes_bid + yes_ask)/2 <= yes_price_max. Buy NO at P = 1 - yes_bid (NO ask).
- Fee: Kalshi taker fee rounded up per contract: ceil_to_cent(0.07 * 1 * P * (1-P))
  (`quant.factory.sportsfair.kalshi_taker_fee(P, 1)`). Fee stress = 2 x that fee.
- Net return per contract = (payout - P - fee) / (P + fee); payout 1 if result == "no".

## Aggregation / split / verdict
- One unit per event: equal-weight mean of the traded contracts' net returns in that event.
- Event close = max market close_ts. All sampled events with >= 1 settled market are time-ordered
  (independent of expression): discovery first 55%, validation next 30%, last 15% untouched.
- Best discovery expression = max t of per-event mean net (n >= 10 events). Verdict on validation
  with required_t_statistic(6): mean > 0 and t >= required_t; mean > 0 at 2x fee; both
  chronological halves of validation mean > 0; max series share of total net < 50%; top 10% events
  share of total net < 50%; capacity >= $10k/month.
- Capacity assumption: per traded contract we may take 10% of the trailing-24h traded contract
  volume (sum of hourly candle volume ending at entry), capped by open interest at the entry
  candle, at price P; $/month = total over validation events / validation calendar months.
