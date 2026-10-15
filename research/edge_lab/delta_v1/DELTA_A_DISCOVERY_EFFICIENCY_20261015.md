# DELTA A — Discovery Efficiency

Date: 2026-10-15
Status: DECISIONAL RESEARCH ONLY
Branch: `research/delta-research-pack-v1-20261015`
Base: `93534d9c365b52f2aa80c4277da1cac4e7338d31`

## Mandate boundary

This DELTA selects research capabilities, not agents, prompts, software architecture, live systems or capital actions.

`BUILDER_AUTHORIZED = FALSE`
`PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
`ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
`REAL_CAPITAL_AUTHORIZED = FALSE`
`LIVE_TRADING_AUTHORIZED = FALSE`

The canonical Owner North Star remains: **Long-run net real wealth growth after all real frictions.** The research-mission wording is subordinate to that authority.

## Decision question

Which discovery method or minimal combination should enter the first research system, if any?

## Evidence summary

No literature provides a clean randomized horse race across all discovery families below. A universal ranking would therefore be fabricated. The useful evidence is heterogeneous:

- causal / quasi-causal evidence that forced institutional flows and constraints move prices and sometimes create predictable pressure;
- large literatures showing textual/event information has economic content and increasingly credible real-time AI evidence around earnings;
- robust evidence that simple factor/anomaly search is vulnerable to multiplicity, post-publication decay, costs and short-borrow frictions;
- encouraging but still experimental 2026 evidence that constrained LLM research loops can discover factors when the evaluation harness is sealed;
- evidence that unconstrained adaptive search can turn the validation history into training data and manufacture apparent improvement;
- evidence that human+AI research can improve forecast/research productivity, while AI assistance can also crowd out causal understanding.

## Method decisions

| Candidate family | Primary role | Decision | Accessibility | Main reason |
|---|---|---|---|---|
| Economic mechanism decomposition | DISCOVERY + CONTROL | RETAIN | HIGH | Forces a falsifiable payer/persistence story and reduces blind specification search; not itself an alpha source. |
| Edge / anomaly archaeology | DISCOVERY feeder + CONTROL | RETAIN | HIGH | Existing literature/codes provide cheap priors, failure cases and mechanism seeds; post-publication decay makes direct copy-trading inappropriate. |
| Forced flows | DISCOVERY | RETAIN | MEDIUM | Strong empirical evidence of predictable price pressure from constrained institutional trading; naturally low-capacity niches can suit a small operation. |
| Institutional constraints | DISCOVERY | RETAIN | MEDIUM | Closely related to forced flows; causal evidence from short-sale constraints, fund flows and rebalancing supports mechanism-first research. |
| Regulatory / settlement mechanisms | DISCOVERY / EXPLORE | RETAIN | MEDIUM | Public institutional events can create discrete mechanisms; event frequency and timestamp/execution quality often limit immediate testing. |
| Literature mining | DISCOVERY feeder + CONTROL | RETAIN | HIGH | Efficient way to harvest priors, replications, known failures and negative knowledge; novelty is limited and publication decay must be assumed possible. |
| Event / document intelligence | DISCOVERY + ENHANCEMENT | RETAIN | HIGH/MEDIUM | Public documents are accessible; current real-time evidence shows structured AI extraction around earnings contains material contemporaneous information. |
| Earnings / guidance intelligence | DISCOVERY + ENHANCEMENT | RETAIN | HIGH/MEDIUM | Strong subcase of Event/Document with precise timestamps and repeated events; crowded but information-rich. |
| Fundamental intelligence | ENHANCEMENT, later DISCOVERY | DEFER | MEDIUM | AI can improve valuation/forecasting productivity, but direct net-alpha evidence is less clean and overlaps Event/Document. |
| Microstructure | DISCOVERY | DEFER | LOW | Mechanisms are real but high-quality message/BBO/fill data, venue semantics and latency requirements are a material barrier at current scale. |
| Cross-market mechanisms | DISCOVERY + ENHANCEMENT | DEFER | MEDIUM | Plausible, but large combinatorial surface and execution alignment create multiplicity risk before the evidence core is proven. |
| Regime discovery | ENHANCEMENT | DEFER | MEDIUM | Useful only with preregistered state definitions; otherwise it creates a very large ex-post partitioning surface. |
| Guided data mining / ML | DISCOVERY + ENHANCEMENT | DEFER as first engine | MEDIUM | ML has genuine OOS forecasting evidence, but flexible search greatly increases overfit/multiplicity; use after trial accounting/sealed evaluation exists. |
| Open-ended LLM ideation | DISCOVERY | DEFER standalone | HIGH | 2026 research is promising but still mostly experimental; adaptive feedback can contaminate validation. Allow only bounded ideation behind deterministic gates later. |
| Human + AI generation | DISCOVERY + CONTROL | RETAIN as research mode | HIGH | Evidence supports productivity/forecast gains, but it is a collaboration mode rather than an independent economic edge. |

## Why forced flows / institutional constraints survive

Coval & Stafford document price pressure from mutual-fund flows and significant returns to liquidity suppliers trading against forced sales. Harvey, Mazzoleni & Melone (2025/2026) document predictable next-day patterns around institutional rebalancing. More recent work on pension funds again documents liquidity-driven equity sales unrelated to contemporaneous equity performance. These are attractive research mechanisms because the **payer and constraint are identifiable before looking at returns**.

This does not mean every flow proxy is tradable. Data timing, instrument choice and execution are still first-class gates.

## Why Event / Document survives

The evidence is no longer only retrospective NLP. Koijen & Levy (NBER 2026) construct a real-time benchmark around earnings and report that optimized agentic systems raise explained contemporaneous return variation from about 8% to near 20% using only announcement-time information. Other 2026 work finds AI-assisted analyst research improves forecast accuracy, and earnings-call models can predict analyst forecast errors in later years.

This supports Event/Document as a **discovery/information-processing capability**, not as proof of a deployable strategy.

## Why archaeology/literature stays but does not lead

McLean & Pontiff find published predictor returns decline materially OOS and especially post-publication. Hou, Xue & Zhang show large replication failure under common methodology and multiple-testing hurdles, while Jensen, Kelly & Pedersen show that many factors do replicate when organized into a smaller number of themes and evaluated globally. The correct inference is not “factor literature is useless”; it is that archaeology is valuable primarily as:

- a prior library;
- a failure library;
- a known-mechanism benchmark;
- a source of candidate transformations;
- a duplication detector.

It should not be rewarded for rediscovering a known backtest.

## LLM / autonomous research conclusion

2026 systems such as AQuA, XAlpha and constrained factor-research agents show that LLMs can improve factor-generation/search under fixed splits and deterministic evaluators. But evidence remains mostly backtest/held-out research evidence, not multi-cycle live portfolio evidence. A recent forward audit of an adaptive LLM loop also shows that repeatedly querying the same history turns the backtest into training data and can materially overstate improvement.

Therefore:

`LLM_DISCOVERY = RETAIN_AS_FUTURE_BOUNDED_CAPABILITY`
`UNCONSTRAINED_LLM_DISCOVERY = REJECT_FOR_P0`

## Exploration / exploitation

No fixed 60/30/10 allocation is justified by the evidence.

Retain instead three **budget classes** whose exact weights remain Owner/P0-later decisions:

- exploitation: deepen a preregistered promising family;
- adjacent exploration: nearby mechanisms/datasets with a clear distinction from the parent;
- radical exploration: genuinely different payer/mechanism/data family.

A permanent non-zero exploration floor is conceptually justified to prevent convergence to the current winner, but no percentage is ratified here.

## Decision-oriented Value of Information

Every expensive experiment should preregister a decision map:

```text
OUTCOME_A -> ACTION_A
OUTCOME_B -> ACTION_B
OUTCOME_C -> ACTION_C
DECISION_DIVERGENCE = HIGH / MEDIUM / LOW
```

High VOI means plausible outcomes lead to materially different next actions. A precise pseudo-numeric VOI score is not required in P0.

## Falsification scope

A negative experiment may falsify only the region it actually tests. Required minimum fields later:

- mechanism manifestation tested;
- universe;
- instrument/proxy;
- horizon;
- data regime;
- execution assumptions;
- conditions under which the negative result applies;
- explicit out-of-scope variants.

One failed US-equity forced-flow proxy must never become “forced flows do not work.”

## Required output

### Discovery method decisions

```text
ECONOMIC_MECHANISM_DECOMPOSITION = RETAIN
EDGE_ARCHAEOLOGY = RETAIN_AS_FEEDER_CONTROL
FORCED_FLOWS = RETAIN
INSTITUTIONAL_CONSTRAINTS = RETAIN
REGULATORY_SETTLEMENT = RETAIN_AS_EXPLORATION_SPACE
LITERATURE_MINING = RETAIN_AS_FEEDER_CONTROL
EVENT_DOCUMENT = RETAIN
EARNINGS_GUIDANCE = RETAIN
FUNDAMENTAL_INTELLIGENCE = DEFER
MICROSTRUCTURE = DEFER
CROSS_MARKET = DEFER
REGIME_DISCOVERY = DEFER
GUIDED_DATA_MINING_ML = DEFER_AS_FIRST_ENGINE
OPEN_ENDED_LLM = DEFER_STANDALONE
HUMAN_AI = RETAIN_AS_RESEARCH_MODE
```

### P0 recommendation

```text
P0_DISCOVERY_RECOMMENDATION = NONE
```

Reason: P0 should prove that the scientific kernel can register, freeze, reproduce, count, assess and decide on a **fixed preregistered cohort** before a discovery engine is allowed to generate adaptive research pressure.

### First post-P0 discovery recommendation

```text
METHOD_1 = MECHANISM_FIRST_FORCED_FLOW_INSTITUTIONAL_CONSTRAINTS
ROLE = DISCOVERY
ACCESSIBILITY_AT_OUR_SCALE = MEDIUM

METHOD_2 = EVENT_DOCUMENT_INTELLIGENCE
ROLE = DISCOVERY + ENHANCEMENT
ACCESSIBILITY_AT_OUR_SCALE = HIGH_TO_MEDIUM

SUPPORT_LAYER = EDGE_ARCHAEOLOGY + LITERATURE_MINING
ROLE = DISCOVERY_FEEDER + CONTROL
```

This is a recommendation, not an authorization.

## What would change this recommendation

- prospective evidence that constrained LLM/open-web discovery materially outperforms the two retained families after identical trial accounting and costs;
- evidence that event/document data timing or licensing is materially worse than assumed;
- evidence that forced-flow proxies require institutional-only data/latency at the relevant horizons;
- a rigorous comparison showing Edge Archaeology produces more independent validated mechanisms per unit cost than the retained pair;
- a new accessible microstructure dataset that removes current data/latency barriers.

## Trajectory implication

DELTA A alone does **not** select T2. It weakly favors a common evidence core plus a small number of specialized discovery families because no evidence supports immediately operating a large autonomous federation.

## Governance compatibility

```text
OD01_OD12 = PASS
STRUCTURAL_PRE_OP = PASS
EXISTING_INVARIANTS = PASS
```

No conclusion here grants economic authority, prospective observation, Builder authority, live trading or real capital.

## Key evidence used

- Coval & Stafford, *Asset Fire Sales (and Purchases) in Equity Markets*, JFE / NBER w11357.
- Harvey, Mazzoleni & Melone, *The Unintended Consequences of Rebalancing*, NBER w33554, revised 2026.
- Koijen & Levy, *Assessing the Benefits of Optimized Agentic AI Systems for Asset Pricing*, NBER w35431, 2026.
- Gu, Kelly & Xiu, *Empirical Asset Pricing via Machine Learning*, RFS 2020.
- McLean & Pontiff, *Does Academic Research Destroy Stock Return Predictability?*, JF 2016.
- Hou, Xue & Zhang, *Replicating Anomalies*, RFS 2020.
- Jensen, Kelly & Pedersen, *Is There a Replication Crisis in Finance?*, JF 2023.
- Harvey, Liu & Zhu, *...and the Cross-Section of Expected Returns*, RFS 2016 / NBER w20592.
- Chordia, Goyal & Saretto, *Anomalies and False Rejections*, RFS 2020.
- AQuA, arXiv:2608.12841 (experimental agentic evidence only).
- Liu et al., *Can AI Do Financial Research?*, SSRN 6569258 (2026; experimental evidence only).
