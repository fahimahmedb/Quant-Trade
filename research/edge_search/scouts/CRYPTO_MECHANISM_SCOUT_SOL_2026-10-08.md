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
