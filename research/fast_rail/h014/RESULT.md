# H-014 Polymarket crypto "above K" vs DVOL digital fair value: UNDERPOWERED

Verdict: UNDERPOWERED (cause POWER). No Polymarket price or outcome was fetched. No dataset was built.

## Inventory (metadata only, see INVENTORY.json)
- Hourly BTC (series 11372): 4419 events, 10 or 20 strikes, ends 2026-03-20..2026-09-29.
- Hourly ETH (series 11373): 4411 events, 10 or 16 strikes, same span.
- Daily BTC (series 45): 367 events x 11 strikes, ends 2025-09-03..2026-09-28 (ETH daily: same structure, not enumerated).
- Distinct hourly resolution times (BTC or ETH): 4429.
- Resolution source: Binance BTCUSDT/ETHUSDT. Hourly = 1h candle Close ending at the title time (ET). Daily = 1m candle Close at 12:00 ET.
- Hourly markets are created only ~1-2h before end, so entry at T-30min is the latest liquid point with history.

## Declared expression (see registry.jsonl)
Hourly, entry T-30min, fair N(d2) with sigma = DVOL/100 and S = Binance spot at entry. Buy YES if fair-ask-fee >= 0.02, buy NO if (1-fair)-no_ask-fee >= 0.02. Prices only in [0.10, 0.90]. ask = history price + 0.01. Fee C*0.07*p*(1-p), C=100, rounded up to 0.0001. Cluster = resolution hour (BTC and ETH of one hour = one unit).

## Power
- Assumed effect 0.01 per contract (1 probability point net; an assumption, no source effect exists).
- sigma = binary_payoff_sigma(0.5) = 1.0 per event. Validation units = 30% of 4429 = 1329.
- expected_t = 0.01/1.0 * sqrt(1329) = 0.36. required_t(1 trial) = 1.96.
- Units needed for t=1.96 at this effect: 38,416, about 29x the available history.

## Consequence
Historical validation cannot resolve a 1-point effect. Only a large effect (>= ~5.4 points) would be detectable in 1329 units. Forward SHADOW_DIRECT with a declared sigma floor is the remaining route. The lead decides.

Caveat: hourly events are heavily cross-correlated (same spot path across strikes), which is why one unit per resolution hour is used. Multiple bets per unit would raise per-unit sigma above 1.0 and lower expected_t further.
