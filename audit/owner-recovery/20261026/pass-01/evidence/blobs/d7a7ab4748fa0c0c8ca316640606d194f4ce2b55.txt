# Quant-Trade — Legacy Duplication / Rediscovery Map

Date: 2026-10-15  
Purpose: prevent future researchers from renaming previously investigated mechanisms and presenting them as novel.

## Classification vocabulary

`SAME_HYPOTHESIS` · `VARIANT` · `SAME_MECHANISM_DIFFERENT_IMPLEMENTATION` · `RELATED_MECHANISM` · `INDEPENDENT` · `UNCERTAIN`

| Historical item A | Historical item B | Relationship | Why | Rediscovery guard |
|---|---|---|---|---|
| B2 sector XRev (36 expressions) | Edge Lab sector-relative shock reversal | SAME_MECHANISM_DIFFERENT_IMPLEMENTATION / VARIANT | Both are sector-relative mean-reversion/reversal; later expression adds a shock condition | Do not call another sector-ETF reversal grid novel merely because thresholds/horizon change |
| Broad 190-futures trend+carry | B4 SPY/TLT/GLD TSMOM | SAME_MECHANISM_DIFFERENT_IMPLEMENTATION | Trend component overlaps, but B4 lacks broad universe/carry and has materially different breadth | A small-ETF failure does not kill broad futures; a broad historical positive does not rescue B4 |
| September month-end pension screen | `disc-monthend-pension-rebalance-spytlt-l1-v1` | SAME_HYPOTHESIS | Same institutional rebalancing mechanism; later generation is formal/data-gated | Future work must cite both; do not restart the mechanism as a new calendar anomaly |
| Prediction-market FLB lab | F2 Kalshi FLB OOS | SAME_HYPOTHESIS / VARIANT | Same favorite-longshot behavioral premise; F2 changes venue, executable ask and post-publication protocol | F2 is a cleaner generation, not a newly discovered mechanism |
| Treasury 5Y auction concession | ZF auction-pressure daily | SAME_MECHANISM_DIFFERENT_IMPLEMENTATION | Same auction supply/concession story, cash-event versus futures daily proxy | Treat source/proxy changes as implementation generations |
| France OAT/Bund v0 | France public-daily-route v1 | SAME_HYPOTHESIS | Same France-vs-Bund repricing thesis, changed public data route | Route repair is not novelty |
| CFE VIX v1 | CFE VIX v2-reader | SAME_HYPOTHESIS | Reader/source-format repair explicitly kept economic parameters and observations unchanged | Do not count v2-reader as a fresh economic trial |
| Historical Form-4 concept | Builder Form-4 census | SAME_HYPOTHESIS_DIFFERENT_STAGE | Census is outcome-blind population/data infrastructure for same insider-cluster concept | Census recovery is completion, not new research |
| Builder Form-4 census | Edge Lab Form-4 EOD v0 | SAME_HYPOTHESIS_DIFFERENT_STAGE | EOD lane expected to reuse census; failed because durable census was unavailable | Do not rebuild a new census under a different label before recovering existing work |
| Historical crypto carry | HL/CEX funding spread | RELATED_MECHANISM | Both arise from perp funding/venue segmentation, but one collects outright carry and the other cross-venue dispersion | Keep economic identity separate; do not merge P&L claims |
| Historical crypto carry | Binance extreme-funding reversal | RELATED_MECHANISM | Funding is common state variable, but reversal is directional crowding unwind | A carry result is not evidence for directional reversal |
| Simple liquidation-cascade rebound | Hyperliquid forced-flow paused lane | RELATED_MECHANISM | Both involve forced flow, but the paused lane may use different microstructure/timing | Simple hourly rebound negative result is a prior, not a blanket mechanism kill |
| FOMC pre-announcement overnight | Broad policy-announcement repricing lane | RELATED_MECHANISM | Same policy-information neighborhood, but broader lane's exact claim is not recovered | Do not generalize one FOMC expression into all policy events |
| Generic Weather forecast-probability V1-V3 | Weather V4 resolution/timing/microstructure candidates | RELATED_MECHANISM | Same market domain, materially changed source of edge | V4 candidates are not “V3 with a new name”; they also are not validated because V4 never opened a phase |
| Generic prediction-market favorite/longshot | prediction-market market making | INDEPENDENT / RELATED_MARKET_ONLY | Same venue class, different payer and economic mechanism | Do not treat maker evidence as rescue of favorite/longshot taker rules |
| Prediction-market negative-risk arb | sports sharp-price/CLV | INDEPENDENT | Structural contract inconsistency versus informational fair-value comparison | No shared trial budget should be assumed without evidence |
| Generic overnight SPY | FOMC-specific overnight | VARIANT_WITH_EVENT_CONDITIONING | Broad overnight net evidence is weak, while event conditioning produced stronger retrospective result | A calendar filter creates a new generation but consumes related exploratory degrees of freedom |
| Turn-of-month | month-end pension rebalance | RELATED_MECHANISM | Both are month-end effects, but pension rule uses cross-asset month-to-date imbalance | Do not conflate unconditional TOM beta with flow-conditioned rule |

## High-risk rediscovery zones

Future AI researchers are especially likely to rediscover these areas unless the ledger is consulted first:

1. **Sector ETF reversal / cross-sectional mean reversion** — already explored through B2 and a later shock-conditioned expression.
2. **Small-universe ETF trend** — B4 already consumed a validation window; broad futures trend/carry is a distinct but already known lineage.
3. **Month-end / overnight / FOMC calendar effects** — multiple variants already exist; generic calendar screens have substantial researcher degrees of freedom.
4. **Crypto funding** — carry, cross-venue spread and directional reversal have all been considered; a new proposal must state which payer/mechanism is actually different.
5. **Prediction-market FLB** — historical sign instability and F2 permission blockage are known; “buy favorites” or “fade longshots” is not novel.
6. **Prediction-market easy arbitrage** — negRisk/combinatorial and cross-venue settlement mismatches were already screened.
7. **Weather forecasting** — naive q-minus-price work and multiple design generations already exist; V4 explicitly shifted toward different mechanics.
8. **SEC Form 4** — do not restart the census or rebuild a new insider-cluster hypothesis without first resolving existing recovery/data-route artifacts.
9. **Treasury / sovereign event repricing** — route/source gaps, not absence of ideas, are the dominant unresolved issue in several lanes.

## Rules for future novelty claims

A proposed item should not be labelled `GENUINELY_UNEXPLORED` merely because its name, code path, model, threshold or horizon is new. Before novelty is granted, compare at least:

- payer and mechanism;
- universe and exposure;
- event definition;
- direction and horizon;
- source of expected compensation;
- execution path and main cost driver;
- overlap with spent datasets/outcome windows;
- whether a prior negative result already falsified the same economic signature.

If similarity cannot be resolved from provenance, classify `UNCERTAIN` and preserve both records. Do not merge by intuition.
