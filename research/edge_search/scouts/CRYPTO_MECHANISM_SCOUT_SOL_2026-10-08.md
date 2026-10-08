# AGENT 1 — CRYPTO MECHANISM SCOUT

Date: 2026-10-08
Worker: Sol one-shot scout
Base ref at branch creation: `executor/f1-trailing-volume-ranking-fix-2026-10-08`
F1 reference inspected structurally only: `research/crypto_carry_f1/PREREGISTRATION_F1_2026-10-08.md` and harness code. **No F1 Stage A or Stage B outcome was opened, downloaded, computed, or modified.** No candidate outcome dataset below was consumed.

Scope boundary: F1 is a long-spot / short-perpetual funding-carry expression driven by trailing realised funding, with funding + basis P&L. The candidates below must earn, if they work, from a different causal channel. No Stage A/B is opened; no A2/B2/B4 work; no framework or general board is created.

## CANDIDATE 1 — PRIOR_RANK = 1

MECHANISM = **FORCED-LIQUIDATION FLOW PERSISTENCE (Hyperliquid-first).** When leveraged positions cross maintenance margin, the venue submits forced market orders. A sufficiently concentrated forced-flow burst may create additional same-direction short-horizon price pressure beyond an ordinary voluntary taker-flow burst of comparable size. The hypothesised edge is continuation during an active forced-deleveraging cascade, **not** funding carry and not a generic post-crash reversion.

WHY_EDGE_CAN_EXIST = Liquidation orders are price-insensitive by construction and can arrive in clusters as marks move through nearby leverage thresholds. Hyperliquid documents that liquidations first attempt to close positions with market orders, with partial liquidation for large positions before full liquidation. A forced seller/buyer therefore has a different objective from an informed or liquidity-sensitive voluntary trader. Recent research also treats forced liquidation flow as empirically separable from voluntary aggressive flow; that is mechanism evidence only, not a project outcome read.

WHY_NOT_ARBITRAGED = The event onset is hard to predict, execution occurs during maximum adverse selection/volatility, the visible forced flow can stop abruptly, other traders compete to absorb it, and exchange/latency/fee risk can dominate a small continuation. Capital willing to lean into a cascade also faces jump and margin risk. These frictions can leave a short-lived impact even if the unconditional strategy is unattractive.

PUBLIC_DATA = Preferred: Hyperliquid public node/fill data plus L2/trade stream and liquidation status reconstructed from the public protocol/node logs; official docs describe liquidation mechanics and public historical/node data. Fallback diagnostic only: Binance `forceOrder` WebSocket plus trades/L2, **but Binance explicitly emits only the latest liquidation order per symbol in each 1000 ms window, so it is censored and unsuitable as a complete liquidation-notional truth source.**

DATA_FRESHNESS = Hyperliquid live node/fill collection can be prospective; its public S3 archive is uploaded roughly monthly and may be incomplete. Binance liquidation streams are live but 1000 ms throttled/censored. Therefore the clean experiment should start with a frozen prospective recorder rather than mining outcome-bearing history for thresholds.

MINIMUM_DISCRIMINATING_TEST = Before collecting outcomes, freeze one BTC/ETH-only event definition using **pre-event** liquidity/volume normalization and a single horizon. Prospectively record forced fills, ordinary aggressive fills, best bid/ask or L2, and midprice. Define `t0` as the end of the event bucket once the predeclared forced-flow threshold is crossed. Primary response: signed midprice return from `t0` to the one frozen post-event horizon, net of a conservative taker round trip. Compare forced-flow events with predeclared matched voluntary-flow controls of the same direction and similar contemporaneous signed aggressive notional, return and volatility. The mechanism survives only if the incremental forced-flow effect is positive, economically larger than costs, and not concentrated in one cascade/day. Otherwise kill it. No grid search and no post-outcome horizon selection.

EXPECTED_INFORMATION_GAIN = **VERY HIGH.** One small prospective test distinguishes “forced origin adds predictive pressure” from generic order-flow autocorrelation. A clean null after matched controls kills the causal mechanism cheaply; a positive result justifies a separately preregistered execution experiment.

MAIN_LEAKAGE_RISK = Defining events with post-event price/volume, selecting the horizon after seeing returns, reconstructing liquidation labels using information not known at `t0`, or using a censored Binance feed as if it were complete. Cascades also create strongly dependent observations, so event/day clustering is mandatory.

BLOCKER = Hyperliquid does not expose a simple complete liquidation WebSocket equivalent to a clean research table; reliable classification may require running/processing node fills and validating the mapping before any outcome-bearing test. If that cannot be made deterministic and point-in-time, this candidate is blocked rather than proxied with censored Binance liquidation volume.

PRIOR_RANK = 1

## CANDIDATE 2 — PRIOR_RANK = 2

MECHANISM = **CROWDED-LEVERAGE UNWIND / FUNDING × OPEN-INTEREST REVERSAL.** Extreme signed funding is used only as a crowding state variable; high/rising open interest supplies the leverage dimension. The hypothesised P&L is a directional move against the crowded side when leverage begins to unwind, **not receipt of funding and not a long-spot/short-perp carry book.**

WHY_EDGE_CAN_EXIST = Funding can become extreme when one side pays to maintain leveraged exposure, while open interest measures outstanding derivative positioning. If extreme funding is accompanied by expanding OI, a later loss of risk capacity can force position reduction and create directionally predictable deleveraging. Recent theoretical/empirical work on perpetuals supports state-dependent limits to arbitrage and reversal/continuation around extreme funding, but the exact timing remains unresolved — which is why OI should be tested as the discriminator rather than assuming funding alone predicts returns.

WHY_NOT_ARBITRAGED = Crowding can persist much longer than a directional trader can remain solvent; extreme funding often coincides with momentum, squeezes and regime shifts. Arbitraging a directional unwind is not delta-neutral, has uncertain event time, pays spread/fees and can be run over before the crowd exits. Those risks differ materially from simply harvesting carry.

PUBLIC_DATA = Binance public funding history, open-interest statistics/current OI, trades/klines and order-book streams; comparable public venue data can later be used for replication. Use only endpoints whose point-in-time availability and retention are verified before preregistration.

DATA_FRESHNESS = Funding and market data are live/public. Binance documents limited retention for historical OI statistics (recent-window availability), so a prospective recorder is preferable. Do not backfill a tuned event rule from the same window intended to test it.

MINIMUM_DISCRIMINATING_TEST = Freeze one prospective event rule before outcomes: signed funding must be extreme by an **ex ante fixed rule** and OI must show pre-event expansion; no return-derived threshold tuning. Primary hypothesis compares the next fixed-horizon opposite-crowd return for `funding-extreme + OI-expansion` events against a funding-extreme-only control, after identical costs. The mechanism survives only if the OI-conditioned incremental effect is positive and economically meaningful; otherwise kill the OI-crowding story. Thresholds and horizon must be chosen from market mechanics/literature before the recorder starts, not from historical returns.

EXPECTED_INFORMATION_GAIN = **HIGH.** It directly tests whether leverage state adds information beyond the funding variable already present in F1. A null prevents spending another experiment on a renamed funding signal; a positive incremental effect establishes a distinct crowded-leverage mechanism for later validation.

MAIN_LEAKAGE_RISK = Selecting “extreme” funding/OI thresholds after looking at future returns; using post-event OI collapse as if known at entry; survivorship/current-universe selection; inconsistent funding intervals; and testing many horizons or coins then reporting the best.

BLOCKER = Point-in-time OI history is retention-limited and exchange definitions can change. A frozen prospective recorder with explicit timestamps/interval normalization is required before a clean test. This candidate is also deliberately ranked below liquidation pressure because its predictor overlaps F1's funding state and causal separation is weaker.

PRIOR_RANK = 2

## SELECTION

TOP_CANDIDATE = **FORCED-LIQUIDATION FLOW PERSISTENCE (Hyperliquid-first)**

WHY_TOP = It is the cleanest causal departure from F1: the predictor is forced order origin, not the level of funding, and the key falsification is incremental impact versus matched voluntary aggressive flow. Hyperliquid's documented liquidation mechanism gives a structural reason for the effect, while the known Binance 1000 ms liquidation-feed censoring provides an explicit measurement trap to avoid. It has fewer semantic degrees of freedom than a funding/OI reversal and can be killed with a bounded prospective microstructure test before any broad backtest.

MINIMUM_NEXT_TEST = Build **only** an outcome-blind feasibility recorder/spec for Hyperliquid BTC/ETH that proves point-in-time liquidation classification, forced-notional aggregation, voluntary-flow control construction, L2/mid capture, timestamps and deterministic replay. Freeze one event threshold and one post-event horizon before recording/reading outcome returns. Then run one prospective paper/shadow discrimination test; no Stage A/B reuse and no F1 outcome access.

BLOCKER = Deterministic, complete point-in-time liquidation classification from public Hyperliquid node/fill data must be demonstrated first. If unavailable, stop; do not substitute Binance's censored `forceOrder` stream as complete liquidation volume.

## PUBLIC RESEARCH BASIS (mechanism plausibility only; not confirmatory project data)

- Hyperliquid Docs — Liquidations: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations
- Hyperliquid Docs — Historical data: https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data
- Binance Developer Docs — USDⓈ-M Futures WebSocket Market Streams / liquidation order streams: https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/All-Market-Liquidation-Order-Streams
- Wan et al., `forced-or-frantic` public replication repository / working-paper materials on forced versus voluntary deleveraging: https://github.com/edwinyeeshunwan/forced-or-frantic
- He, Manela, Ross & von Wachter, *Fundamentals of Perpetual Futures* (limits to arbitrage background): https://arxiv.org/abs/2212.06888

Guardrail: literature was used to establish mechanism plausibility and data feasibility only. No candidate parameter was selected from project outcome data; no candidate historical return sample was consumed.

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

---

# SECOND PASS — HYPERLIQUID MEASUREMENT RESOLUTION

Date: 2026-10-08
Scope: continuation of the existing scout only. **No F1 outcome was read, downloaded, computed, or modified. No candidate return outcome was consumed.**

## Measurement findings persisted from the completed second pass

Hyperliquid's fill representation carries liquidation metadata directly on a fill: the fill type may contain a `liquidation` object with fields including the liquidated user, liquidation mark price and liquidation method. This is materially stronger than inferring a liquidation from price action or funding. A market-wide node run with fill writing enabled (`--write-fills`, with block batching available via `--batch-by-block`) is the relevant capture surface because it preserves the fill record itself. By contrast, the ordinary public `trades` WebSocket is not sufficient by itself for this experiment because it does not provide the liquidation label needed to distinguish forced from voluntary aggressive flow.

The implication is that the **label semantics are deterministic on a captured fill record**: `liquidation != null` is forced-flow; otherwise the fill is not labelled as liquidation. The fill record also contains timestamped execution information sufficient to order fills in replay. This satisfies the core classification requirement at the record level without any future-price inference.

The remaining unresolved issue is not label ambiguity but **market-wide capture completeness and operational replay completeness**. A clean experiment must use the node fill output as the source of truth and continuously capture BTC/ETH fills plus contemporaneous book state. Historical/public archive material may assist validation, but it must not be assumed complete enough to replace a prospective recorder unless archive coverage and gaps are proven separately. Therefore the project may proceed to building and validating the recorder, but must not proceed to the economic execution test yet.

LIQUIDATION_CLASSIFICATION = **DETERMINISTIC_AT_FILL_RECORD_LEVEL** — classify forced fills iff the captured Hyperliquid fill carries a non-null `liquidation` object. Do not infer labels from subsequent prices, funding, or Binance `forceOrder`.

PUBLIC_DATA_VERIFIED = **YES_FOR_SCHEMA_AND_PUBLIC_CAPTURE_PATH; NOT_YET_FOR_END_TO_END_MARKET_WIDE_COMPLETENESS** — public Hyperliquid fill/node surfaces expose the required liquidation metadata; ordinary `trades` WebSocket alone is insufficient.

COMPLETENESS = **PROSPECTIVE_NODE_CAPTURE_REQUIRED / NOT_YET_PROVEN_END_TO_END** — the second pass resolved the semantic label but did not establish that historical archives alone are gap-free or that a not-yet-built local recorder can capture every market-wide fill without interruption. Completeness must be demonstrated by recorder health/gap accounting before economic outcomes are read.

POINT_IN_TIME = **YES_AT_CAPTURE** — the liquidation object is part of the fill record available when the fill is written; classification does not require post-event return information. Event construction must use only fill/L2 records with exchange timestamp `<= t0`.

REPLAYABLE = **YES_CONDITIONALLY** — deterministic replay is possible from an append-only raw log containing the original fill records, exchange timestamps, stable deduplication key(s), sequence/block context when available, and synchronized L2/BBO records. Out-of-order arrival must be normalized by exchange time plus deterministic tie-break, never by future outcomes.

COMPLETE_ENOUGH_FOR_RESEARCH = **CONDITIONALLY_YES_FOR_PROSPECTIVE_CAPTURE** — provided the recorder proves continuous market-wide node-fill capture, explicit gap accounting, and synchronized BTC/ETH book-state capture. Historical archive completeness is not assumed.

## Minimal raw-capture contract to implement next

Universe is exactly `BTC` and `ETH`. Persist raw records before any derived event computation.

Required fill fields: raw payload; exchange/event timestamp; local receipt timestamp; coin; side/direction; price; size; unique fill/trade/hash identifier where exposed; block/sequence context where exposed; liquidation object verbatim; derived boolean `is_liquidation` only as a deterministic mirror of `liquidation != null`.

Required book fields: exchange/event timestamp; local receipt timestamp; coin; best bid price/size; best ask price/size; derived mid `(bid+ask)/2`; full L2 payload if the selected capture surface exposes it. Missing book state is never forward-filled across an event boundary.

Raw-log invariants: append-only; UTC timestamps; no post-hoc mutation; duplicate raw records retained or counted but deduplicated deterministically for analysis; explicit recorder start/stop and gap records; source/version metadata recorded at process start.

FORCED_FLOW_AGGREGATION = signed liquidation notional in one frozen event bucket, `sum(sign * price * size)` over liquidation-labelled BTC/ETH fills only. Multiple forced fills within the same bucket are aggregated, not treated as independent events.

VOLUNTARY_AGGRESSIVE_FLOW_CONTROL = same signed notional construction over non-liquidation aggressive fills, using the same time basis and symbol. A voluntary control must never contain a liquidation-labelled fill.

DETERMINISTIC_REPLAY = sort accepted records by exchange timestamp and then a frozen stable tie-break (block/sequence/id when available; otherwise raw-log ordinal). Deduplicate only exact repeated fill identifiers/payloads under a frozen rule. Derived events are regenerated solely from raw logs and frozen constants.

## Frozen economic test status

TEST_FROZEN = **FALSE**. The second pass resolved measurement semantics but did not finish a defensible outcome-blind choice of the single event threshold, single post-event horizon, matching tolerance, cost constant and final clustered statistic. Those values must be frozen in code/spec **before the recorder's economic sample is opened for return analysis**. No grid search is authorized.

HARNESS_BUILT = **FALSE** — no recorder/parser/harness file was produced before this persistence request; none is invented retroactively here.

SYNTHETIC_TESTS = **FALSE** — no synthetic fixture/test file was produced before this persistence request. Required future fixtures remain: liquidation vs voluntary fill; duplicate events; out-of-order timestamps; missing L2; multiple forced fills; event clustering; leakage after `t0`.

CANDIDATE_1_STATUS = **MEASUREMENT_BLOCKER_RESOLVED_AT_SCHEMA_LEVEL__IMPLEMENTATION_BLOCKED**. Candidate 1 is **not** killed: the critical liquidation label can be deterministic and point-in-time from node fill records. It is also **not yet executable** because prospective completeness, recorder behavior and frozen-test implementation are not yet demonstrated.

READY_TO_RECORD = **FALSE** — recorder does not yet exist and continuity/gap accounting is not tested.

READY_TO_EXECUTE = **FALSE** — no economic sample may be evaluated until the recorder/parser exists, synthetic tests pass, prospective capture completeness is demonstrated, and exactly one event definition/horizon/statistic/cost/dependence rule is frozen.

BLOCKER = **IMPLEMENTATION_AND_COMPLETENESS_PROOF_ONLY** — build the BTC/ETH market-wide node-fill + L2/BBO recorder; prove no silent gaps/duplicate ambiguity; add deterministic replay and the required synthetic tests; then freeze the one-shot economic test before any candidate return outcome is read. The original semantic blocker — whether liquidation can be identified deterministically and point-in-time — is resolved.

NEXT_ACTION = **Build only Candidate 1's minimal prospective recorder/parser/replay harness and synthetic fixtures on this branch; validate capture continuity and then freeze one event rule plus one horizon before reading any economic return. Do not switch to Candidate 2 unless this implementation/completeness proof fails.**

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
