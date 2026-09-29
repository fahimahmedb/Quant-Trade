# WEATHER FORWARD ARCHITECT STATE — 2026-09-29

```text
STATUS         = DONE (spec + manifest + state committed and pushed on this branch)
CURRENT_PHASE  = COMPLETE — no further architect action; next mission = Builder implementation (spec §28)
BRANCH         = claude/intelligent-gates-msidml
REAL_CAPITAL_AUTHORIZED = FALSE
```

## SOURCES_ALREADY_CHECKED (do not re-fetch)

- research/recus_2026-09: agent1_registres.md, agent1_etat.md (branch claude/dazzling-dirac-foklrv); agent2_profits_mesures.md, agent2_etat.md (claude/gallant-cerf-e0rpao); agent3_recette_recu.md, agent3_etat.md (claude/exciting-edison-w68tos) — read in full.
- QUANT_NORTH_STAR.md; governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md; handoff/BLUE_MASTER_V2_STATE_2026-09-20.md; handoff/BLUE_CONTEXT_REACQUISITION_2026-09-20.md; governance/P0_T0_PRECOMMIT_TEMPLATE_2026-09-21.md; D05 sample-sufficiency and D09 EC1 heads (conventions: frozen estimand, allocation policy is claim-defining, precommit before t0).
- Polymarket: gamma `events?tag_slug=weather` (open + last 30 days closed, 600 events), CLOB `/book`, `/markets/{condition_id}`, `/prices-history`, data-api `/trades?market=`, `/v1/leaderboard?category=WEATHER` (one spot check only); docs.polymarket.com/trading/fees (fee formula, weather 0.05, rebate 25%), /programs/taker-rebates (tiers), maker-rebates page (via search summary).
- Settlement: live market descriptions (NOAA WRH template, WU fallback, no-data → lowest bracket, 7-day correction clause, HKO one-decimal template); weather.gov/wrh/timeseries page + obs.js (Synoptic API, obtimezone=local, units=temp|F).
- Forecast/obs: Open-Meteo ensemble API (ecmwf_ifs025 51, gfs025 31, icon_seamless 40 members; local-day extremes), previous-runs (429), single-runs docs (run= init time, archives from 2026-04-02, 4–6 h availability lag), pricing page (600/min, 5k/h, 10k/day); api.weather.gov (generatedAt/updateTime present); aviationweather METAR history (36 h OK).
- Roissy April 2026 sensor case (Zonebourse, Le Tribunal du Net; Bloomberg/NPR/CNN cited by Agent 3) — verified secondary.
- github.com/jattree/weather-edge post-mortem (−13.9% ± 5.3% per trade simulated; live loss) — unverified secondary.

## DECISIONS_FROZEN

See WEATHER_FORWARD_FREEZE_MANIFEST_2026-09-29.md section A (T_entry = game_start − 6 h; ECMWF ENS 51 via Open-Meteo; dressed ensemble σ = 1.0 °C with 30-day point-in-time bias; single argmax leg; h = 0.10; taker fee 0.05·p(1−p); REALISTIC/CONSERVATIVE fills; S_ref 50 USD; tiers 100/500/1,000/5,000; θ = ΣN/ΣC; block bootstrap over dates; min 1,000 trades / 60 dates / 30 stations; gate §18).

## BLOCKERS

- None scientific. Procedure items before t0: STATION_TABLE hash, settlement parser ≥ 98% agreement, forecast access/licence decision, params/engine/manifest hashes, t0 declaration by Blue (manifest section B).
- Operational unknowns carried: legal access, Open-Meteo licence, Synoptic token terms, NOAA page rounding chain.

## NEXT_ACTION

None for this role. Next authorized mission: Builder implements spec §28 (station table, capture services, eligibility/decision/fill/ledger engines, replay tool), runs burn-in ≥ 30 days, then requests t0 from Blue. REAL_CAPITAL_AUTHORIZED stays FALSE.
