# MANDATORY AUDIT INTEGRITY CHECK

AUDIT_ACCESS_STATUS: YES  
AUDITED_BRANCH: `blue/weather-v3-orchestration-2026-10-02` — YES  
AUDITED_SHA: `5747f11cb87c59bea32d2cb38c9e2c4c06db08ea` — YES  
PRIMARY_DOCUMENT_VERIFIED: YES — complete Gold content fetched and read  
ARTIFACTS_ACTUALLY_READ: YES — exact list below; referenced final V3/S4/S6 artifacts: NO at examined anchors  
EXTERNAL_SOURCES_VERIFIED: PARTIAL — documentary existence/selected aggregate arithmetic only  
DATASETS_ACTUALLY_AVAILABLE: PARTIAL — four public aggregate artifacts; historical PIT market data UNKNOWN; raw historical weather PIT PARTIAL (documented candidates, no raw validation); executable L2 UNKNOWN  
MAIN_AUDIT_LIMITATION: PARTIAL — exposure custody/clean validation cannot be certified; unlinked prior final work not available.

## PASS 1 — VERIFIED FACTS

|Access/integrity check|Status|
|---|---|
|repository_accessible|YES|
|exact_branch_resolved|YES|
|exact_sha_resolved|YES|
|primary_gold_map_read_completely|YES|
|additional_files_read|YES|
|referenced_V3_final_synthesis_S4_S6_available|NO|
|external_sources_independently_verified|PARTIAL|
|historical_PIT_market_data_available|UNKNOWN|
|historical_PIT_weather_data_available|PARTIAL|
|executable_orderbook_data_available|UNKNOWN|

Artifacts actually read (first eight at audited SHA; later paths at explicitly named source SHA):

- `AGENTS.md`
- `QUANT_NORTH_STAR.md`
- `research/weather_forward/v3/AGENTS.md`
- `research/weather_forward/v3/V3_CURRENT.md`
- `research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md`
- `research/weather_forward/v3/V3_CODEX_CONTINUATION_2026-10-03.md`
- `research/weather_forward/v3/CODEX_NATIVE_ORCHESTRATOR_2026-10-03.md`
- `research/weather_forward/v4/WEATHER_V4_EDGE_ARCHAEOLOGY_GOLD_MAP_2026-10-04.md`
- `S1@697865d4f8ba5ecfcb23025272b50b5eee2b2f30:research/weather_forward/v3/data/V3_DATA_ARCHAEOLOGY_2026-10-02.md`
- `S0@1fa81100d3d4f32cd8f8842356c043c3d502910d:research/weather_forward/v3/compute/ACCEPTANCE_REPORT.json`
- `S0@1fa81100d3d4f32cd8f8842356c043c3d502910d:research/weather_forward/v3/coordination/S0_PROGRESS.md`

External pages actually inspected: Command Center README; Marketlens Weather page; Pondletter article; Polydata HighTempTation; Synoptic HF-ASOS documentation; AviationWeather Data API; official NegRisk repository overview. External artifacts actually parsed: Command Center ground-truth, hourly hold, fade-lock, bias-validate JSON at `55fe92b8c720b177cdd2e00889fcea1ff5105b1b`; `scripts/verify-backtest.mjs` read via GitHub (blob `8831300afe0f541061d9238b85db333aadd6af42`). Verifier logic was independently reimplemented, not executed as trusted code. Other cited sources are unverified leads.

Missing/inaccessible evidence: final V3 synthesis and S4/S6 final reports absent at anchor/explicit linked branch trees; no precisely bound final SHA supplied. S1 machine-readable inventory path is referenced but not read; its report sufficed for metadata audit. Raw forecast vintages, source-incidence denominator, books, fee history, complete wallet positions, deployed contract bindings and holdout custody were not inspected. **NOT VERIFIED — INSUFFICIENT EVIDENCE.** Do not infer that they do not exist elsewhere.

### Small independent source diagnostic

Pinned public artifact contains 727 city-model cells; 35 have at least 300 `pm_bucket` attempts. Independent Wilson arithmetic reproduces the four displayed passes (London ICON/UKMO/UKMO_2km and NYC GFS_HRRR). This verifies aggregate arithmetic, not raw labels, PIT features, OOS independence or economic gains. Ground-truth lineage uses `Open-Meteo historical-forecast-api`, so its availability-at-decision is not established. Hold/fade lineage uses hourly observations for 2024-04-07–2026-04-07, corrected Denver/Houston station mappings and a Hong Kong proxy; these are material source-transfer cautions. Bias validate lineage is rolling30d with validation 2025-08-20–2026-01-06: multiple model cells share weather dates, and a named validation split is already exposed to Quant. No full regeneration undertaken.

Artifact SHA256 hashes:

- ground-truth: `12d94c0e8d5459c2b88639b4a773751ef5acad325b71b8a30550bf2c4e634281`
- hourly hold: `5c6c7c1eb7b320553d18ccc123c1a7cabde0b058fa71f434efd0d9a779811c42`
- fade-lock: `8a18c1b83468edf7786e9ba41f6f4131453d3ed0a3c56dedfed15ea0c6eb62e7`
- bias validate: `8c8636254246915f4d1a3a799a7f61f1cb43c90640ccaf85a38d16a4628c49ff`

Polydata displays $3,663 / $57,196 as 0.064...%; arithmetic is about 6.40%. This is a display-unit problem, not independently reconciled wealth evidence. Do not extrapolate it to every vendor statistic.

### Material claim register

States below describe this audit's verification, not whether a hypothesis is true. DEPENDENT_ON_PRIOR_RESEARCH=VERIFIED means dependence is established, not that the prior result is valid; NOT_APPLICABLE means no such dependency needed.

|CLAIM_ID|CLAIM|SOURCE_OR_FILE|DIRECTLY_VERIFIED|POINT_IN_TIME_AVAILABLE|DEPENDENT_ON_PRIOR_RESEARCH|EVIDENCE_STATUS|REMAINING_UNCERTAINTY|
|---|---|---|---|---|---|---|---|
|AC01|Exact branch/SHA and complete Gold are accessible|Git object + GitHub fetch at audited SHA|VERIFIED|NOT_APPLICABLE|NOT_APPLICABLE|VERIFIED|Remote branch may move later; audit is fixed|
|AC02|Gold uses adaptive external findings to rank research|Gold §§0,2,7,13|VERIFIED|NOT_APPLICABLE|VERIFIED|VERIFIED|Full previous-agent exposure not reconstructed|
|AC03|No complete trial/exposure ledger or locked estimand in Gold|Gold §§6,9,10,12,15; anchor V4 path inventory|VERIFIED|NOT_APPLICABLE|PARTIALLY_VERIFIED|VERIFIED|Controls may exist outside allowed/unlinked scope|
|AC04|V3 final verdict independently established|Gold §0 vs anchored V3_CURRENT and linked trees|UNVERIFIED|NOT_APPLICABLE|VERIFIED|UNVERIFIED|Final synthesis not present/bound; not evidence it never existed|
|AC05|S0 Layer B remains pending at linked SHA|S0_PROGRESS and ACCEPTANCE_REPORT|VERIFIED|NOT_APPLICABLE|VERIFIED|VERIFIED|Later work not authoritative here|
|AC06|S1 reports potential as-issued forecast archives, not executable depth proof|S1 archaeology report|VERIFIED|PARTIALLY_VERIFIED|VERIFIED|PARTIALLY_VERIFIED|Report reviewed; raw archives not fetched/validated|
|AC07|No clean historical economic validation surface certified in inspected scope|Gold, V3_CURRENT, S1; access inventory|PARTIALLY_VERIFIED|UNVERIFIED|PARTIALLY_VERIFIED|PARTIALLY_VERIFIED|Cannot establish universal contamination/absence outside scope|
|AC08|Command Center four headline cells reproduce count-based gate|Pinned ground-truth JSON; independent Wilson arithmetic|VERIFIED|UNVERIFIED|VERIFIED|VERIFIED|Source generation/PIT/fees not reproduced|
|AC09|Command Center artifact contains 727 city-model cells, 35 n>=300|Pinned ground-truth JSON parsed independently|VERIFIED|UNVERIFIED|VERIFIED|VERIFIED|Cells correlated; not M_eff|
|AC10|Ground-truth forecast lineage names historical-forecast-api|Pinned artifact _lineage|VERIFIED|UNVERIFIED|VERIFIED|VERIFIED|Endpoint label does not prove original first-seen forecasts|
|AC11|Lock statistics have corrected/proxy station provenance|Pinned hold/fade _lineage|VERIFIED|UNVERIFIED|VERIFIED|VERIFIED|Hourly proxy may not equal settlement extremes or receipt information|
|AC12|Bias validation is rolling30d, 2025-08-20 to 2026-01-06|Pinned bias validate _lineage|VERIFIED|UNVERIFIED|VERIFIED|VERIFIED|Cell-count lift is not independent economic replication|
|AC13|HF-ASOS documentation reports 2–5 min latency and whole-C precision|Synoptic source documentation|VERIFIED|NOT_APPLICABLE|NOT_APPLICABLE|VERIFIED|Provider report not measured station-by-station during audit|
|AC14|Vendor executable historical L2 is available and usable|Marketlens page|UNVERIFIED|UNVERIFIED|PARTIALLY_VERIFIED|UNVERIFIED|Marketing verified, raw provenance/access/coverage not verified|
|AC15|Pondletter establishes all generic forecast Weather edges fail|Gold §2.1; author article|UNVERIFIED|UNVERIFIED|VERIFIED|UNVERIFIED|Short author-reported selected rules cannot establish universal failure|
|AC16|Wallet signatures identify latency causality|Gold §§2.2,3.4; Polydata aggregates|UNVERIFIED|UNVERIFIED|VERIFIED|UNVERIFIED|Multiple mechanisms, accounting/selection confounds|
|AC17|Polydata top-three displayed percentage has unit inconsistency|HighTempTation page; independent division|VERIFIED|NOT_APPLICABLE|VERIFIED|VERIFIED|Local display issue does not prove all analytics false|
|AC18|Selection/multiplicity risk critical without complete controls|Observed flexibility + statistical argument §4|PARTIALLY_VERIFIED|NOT_APPLICABLE|PARTIALLY_VERIFIED|PARTIALLY_VERIFIED|Risk judgment, not measured false-discovery rate|
|AC19|Adaptive multi-edge engine can fit noise at plausible effective N|Gold conceptual chain; audit conditional attack §9|PARTIALLY_VERIFIED|NOT_APPLICABLE|PARTIALLY_VERIFIED|PARTIALLY_VERIFIED|No implemented engine/effective N inspected; prospective risk|
|AC20|Forward repaired design is possible|Audit architecture conditional on new sealed data|UNVERIFIED|UNVERIFIED|NOT_APPLICABLE|UNVERIFIED|Access, capture authorization, inferential power and horizon feasibility pending|
|AC21|No edge has positive independently validated economics in inspected evidence|Source/edge matrix|PARTIALLY_VERIFIED|UNVERIFIED|PARTIALLY_VERIFIED|PARTIALLY_VERIFIED|Absence of verified evidence, not proof zero real edge|

## Audit limitations before judgment

|Own limitation|Could change design verdict?|Contamination verdict?|Multiplicity verdict?|Economic interpretation?|
|---|---|---|---|---|
|Full exposure/variant custody missing|YES if additional independently anchored controls exist|YES; unidentified history could be clean or contaminated|YES if complete search/control budget supplied|YES; present unknown is not negative profitability|
|V3 final synthesis/S4/S6 not bound|YES if documented repairs already exist|YES if access histories recovered|PARTIAL; may clarify past selection|YES; cannot rely on alleged terminal prior result|
|Raw PIT weather/books/receipt clocks not inspected|YES if impossible clocks imply stronger unidentifiability|PARTIAL; raw access could reveal prior reuse|PARTIAL; candidate feasibility changes test universe|YES; realistic net gaps cannot be inferred|
|External arithmetic only; no raw regeneration or wallet accounting|PARTIAL; source premises could collapse|YES; exact exposed periods not fully known|PARTIAL; selection count likely incomplete|YES; headlines may fail PIT/denominator checks|
|No empirical effective N/power/rare-loss calibration|YES; clean test could be infeasible at useful horizon|PARTIAL; dependence changes boundaries|YES; M_eff not estimated|YES; tail/positive-probability precision unknown|

Separate dimensions: research-governance quality = PARTIAL (good prohibitions, missing enforceable test contract); evidence integrity = PARTIAL (source arithmetic reproducible, PIT economics unverified); contamination risk = HIGH with unknown extent; clean-test identifiability = UNKNOWN historically / conditionally repairable prospectively; execution realism = UNKNOWN; ability to infer future economic edge = NOT VERIFIED — INSUFFICIENT EVIDENCE. Numerical scores for each = **NOT ESTIMABLE FROM AVAILABLE EVIDENCE**. No global confidence score.

## PASS 2 — ADVERSARIAL INTERPRETATION

The verdict below is the auditor's risk judgment conditional on PASS 1, not an observed profitability result. Weakest critical link: no certified clean economic validation contract/surface; missing book evidence cannot be replaced by theory.


# ASTRA — Weather V4 edge-map / research-overfit audit — 2026-10-04

## 1. Executive verdict

**WEATHER_V4_RESEARCH_DESIGN = RESEARCH_DESIGN_REPAIR_REQUIRED**

EDGE_REGISTRY_INTEGRITY = PARTIAL; MULTIPLICITY_RISK = CRITICAL; SELECTION_BIAS_RISK = HIGH; DATA_REUSE_RISK = HIGH; COMBINATION_OVERFIT_RISK = CRITICAL; FORWARD_VALIDATION_PATH = REPAIRABLE.

The Gold Map is useful discovery material, not yet an identifiable confirmatory research design. Its source grades, PIT/execution gates, winner-and-control requirement (§5), and refusal to launch a strategy (§9) are real safeguards. They do not control the implicit variant search, repeated exposure, horizon selection or adaptive composite. In particular §10 permits promotion after positive markout and an available forward path, without requiring an untouched test, adjusted uncertainty or an actual forward result. §15's “kill the rest” instruction conflicts with this audit's explicit preservation mandate: replace deletion with authority/dormancy states. This report preserves every meaningful Gold family, plus explicitly labeled scope extensions from the mission; it does not select a profitable subset.

No profitability conclusion follows. All economic decision weights remain zero; STRUCTURAL denotes a conditional identity/correctness primitive, not proved arbitrage opportunity or trading permission. Non-pruned hypotheses can be investigated under a repaired lifecycle. Nothing examined establishes fundamental unidentifiability if synchronized prospective capture and sealed validation can later be provided.

## 2. Authority / exact SHA

Repository: `fahimahmedb/Quant-Trade`; audit anchor: `5747f11cb87c59bea32d2cb38c9e2c4c06db08ea`; source branch: `blue/weather-v3-orchestration-2026-10-02`. Git object type is commit; the remote branch resolved to exactly this SHA during audit. GitHub fetch_commit independently resolved the same authority. Primary: `research/weather_forward/v4/WEATHER_V4_EDGE_ARCHAEOLOGY_GOLD_MAP_2026-10-04.md` (hereafter Gold).

Read North Star, root AGENTS, V3 AGENTS/CURRENT and V3 orchestration/continuation/native dispatch only for relevant contracts. User's bounded audit and preservation instruction supersede old pruning instructions; V3 bootstrap permits task-specific reads. No strategy code changes, deployments, holdout reads, private results or threshold tuning.

**Authority gap:** the anchor's V3 tree has planning files only. V3_CURRENT still lists S0 WIP and pending design/synthesis. The explicitly linked S0 `1fa81100d3d4f32cd8f8842356c043c3d502910d` has Layer A/acceptance PASS but Layer B not run. Linked S1 `697865d4f8ba5ecfcb23025272b50b5eee2b2f30` has a data inventory/report. S4/S6 branch tips are still S1; no S4/S6 final design reports are present. No V3 final synthesis is bound by a path+SHA in Gold. Thus Gold §0's `V3_NOT_JUSTIFIED` is an assertion in the map, not independently verified terminal evidence. Do not backfill authority from chat or later unlinked branches. This gap does not invalidate the resolved audit anchor; it limits conclusions about prior research.

REAL_CAPITAL_AUTHORIZED = FALSE; LIVE_TRADING_AUTHORIZED = FALSE; t0 = NOT_DECLARED; BUILDER_AUTHORIZED = FALSE.

## 3. Audit methodology and source evidence

Falsification-first document audit: trace claim → source type → PIT information set → experimental unit → executable outcome → independent validation. Distinguish source authenticity, mechanism existence, causal attribution, economic magnitude and permission. Small independent arithmetic/source checks only; no large simulation, V3 rebuild, market dataset, private result or reserved holdout inspected.

|Source inspected|What it supports / attack|Audit authority|
|---|---|---|
|[Command Center](https://github.com/testedmedia/polymarket-weather-command-center), pinned `55fe92b8c720b177cdd2e00889fcea1ff5105b1b`|Public artifacts/verifier exist; README explicitly presents selected wins and labels combos ASOS proxies. A cellwise Wilson gate cannot establish executable economics or correct for selecting city/model cells. Regeneration is not independent replication.|B artifact availability, not economic validity|
|[Marketlens](https://marketlens.trade/polymarket-weather-data)|Claims L2/weather coverage since July 2026, not years. No raw books, access/license or completeness audit performed. Listed market counts are not independent weather days.|C capability claim only|
|[Pondletter](https://pondletter.com/kalshi-weather-markets-efficient/)|Author's short forward-test account describes negative ensemble rules. No raw event ledger or independently reproduced fills examined. Cannot generalize its negative result to all forecasting or to V4 latency.|C author report; no B upgrade|
|[Polydata HighTempTation](https://polydata.pro/traders/hightemptation)|Behavior/P&L aggregates only; displayed top-three fraction has a percentage-unit inconsistency. Complete wealth/cash-flow history not reconciled. High win rates coexist with large losses.|C selected analytics; no causal authority|
|[Synoptic HF-ASOS](https://docs.synopticdata.com/services/high-frequency-asos)|Provider documents experimental availability, whole-degree Celsius precision and typical 2–5 minute receipt latency. One-minute sampling is not instantaneous publication or exact settlement precision.|A for provider's documented product, not official contractual truth|
|[AviationWeather API](https://aviationweather.gov/data/api/)|Official API documentation; retention/product semantics do not certify historical receipt time.|A product documentation only|
|[NegRisk adapter](https://github.com/Polymarket/neg-risk-ctf-adapter)|Official protocol repository supports investigating equivalence, not deployed per-market guarantees, executable depth or profit.|A protocol source; application unproved|

Gold's generic polymarket/help homepages are not versioned individual rules or historical fee evidence. FAA, Weatherstappen/ColdMath, wethr mappings, all-city incident/backtest artifacts and community leads not independently reproduced here: inherited leads only. A reproducible JSON count can still have revised weather, selected models or wrong station labels. A/B provenance must not be conflated with H4 economic evidence.

### NEW_INFORMATION_TOUCHED

- Anchor metadata and file paths above, plus remote branch/path inventories: governance/document exposure only; no sealed results. S0 acceptance/progress are synthetic engineering summaries, DEVELOPMENT_ONLY; S1 archaeology report is metadata, not market outcomes.
- External Command Center README, verifier and four explicitly Gold-referenced artifacts: `polymarket_asos_ground_truth_v1.json`, `asos_hourly_hold_rates_v1.json`, `asos_fade_lock_v1.json`, `bias_adjusted_polymarket_v5_validate.json`, pinned to the SHA above. Aggregate outcomes/calibration summaries **are discovery exposure**, including their train/validate periods, city rankings and generated selection; they cannot be a clean confirmatory surface for hypotheses chosen here. No Quant holdout was opened. Diagnostic hashes/results appended below.
- Marketlens landing page: coverage/capability metadata; its historical rows remain unopened but cleanliness is UNKNOWN because Gold already reflects selected external history. No market sample downloaded.
- Pondletter article and Polydata HighTempTation page: published retrospective/forward outcome summaries now DISCOVERY_CONTAMINATED for Quant selection; their underlying periods cannot be called clean just because raw fills remain unopened. Exact period provenance must be recorded by the ledger custodian. Other named wallets were not opened.
- Synoptic, AviationWeather and NegRisk documentation: mechanism/API knowledge; no outcome contamination, but product/source-version exposure influences hypotheses. Web retrieval occurred 2026-10-04; pages may be mutable/cached and are not evidence of what existed at historical entry.
- No future/private result, reserved forward holdout or additional raw weather/market dataset inspected. Unknown prior agent exposure is not certified absence of exposure.

## 4. Multiplicity analysis

Gold names about a dozen headline ideas, but §§3–5 and E1–E5 imply many correlated alternatives. The audit registry has 33 rows including infrastructure and mission extensions, not 33 independent economic tests. A modest illustrative rectangular search is:

`20 economic mechanisms × 10 cities × 2 high/low × 4 models × 3 horizons × 4 release/local times × 3 feeds × 7 buckets × 2 sides × 5 entry cuts × 5 exits × 2 execution modes × 3 regimes × 3 windows × 2 source mappings = 725,760,000 specifications`.

Versions, subsets, structural portfolios and edge interactions enlarge it. Many cells are impossible/redundant; this is a search-capacity illustration, **not measured M_eff**. Continuous thresholds and adaptive rewrites make the actual search count unbounded without a ledger. Effective N-tests requires the complete tried family and joint null dependence, neither supplied. Even a much smaller 100–1,000 effective alternatives would make unadjusted nominal 5% selection unsafe.

Under independent null tests, FWER = `1-(1-.05)^m`: 64.2% at 20; 99.4% at 100. Dependence changes those numbers but does not remove hidden researcher choice. For independent standardized Gaussian noise, leading-order maximum scales roughly `sqrt(2 log m)` (3.0 at 100, 4.3 at 10,000); this illustrates best-of-N/winner's-curse inflation, not a calibrated Weather threshold. All-null discoveries have conditional FDP=1 whenever any rejection occurs.

Control architecture: immutable family/variant graph, including failures/unpublished forks and objective changes; all explorations explicitly non-confirmatory. For a **frozen finite promotion batch**, Holm at program FWER .05 across the declared economic tests is a defensible default with valid dependence-aware p-values. BY can support exploratory discovery FDR under arbitrary dependence but must not grant economic authority. Resampling max-tests require reconstructing the entire selection process and valid blocks, not just testing the final survivor. Repeated batches consume a preallocated program alpha budget (e.g. `.05/2^batch`); new variants cannot reset it. If sequential confidence/e-processes are used, their bounded-loss/dependence assumptions must be proved before peeking; otherwise lock one analysis time. Bayesian shrinkage alone is not multiplicity protection when priors/model selection were tuned to seen outcomes.

## 5. Selection / survivorship analysis

Leaderboard winners are selected on future realized success relative to their earlier fills. Their high-price/fast-sale signatures can be luck, post-resolution buying, inventory management, arbitrage, copied information, cash-flow accounting or selection. Public repository survival adds publication bias; impressive screenshots select payoffs rather than expose full risk.

Freeze wallets from an outcome-blind sampling frame before the evaluation period: all eligible activity strata, including unsuccessful/inactive wallets. If winners are deliberately oversampled for mechanism discovery, label case-control selection and never estimate population profitability from it. Match controls on pre-period capital/activity/market access, not future survival. Reconcile deposits, withdrawals, purchases, sales, redemptions, unclaimed losers, open inventory, fees/rebates and external transfers. Public fills cannot identify hidden capital, off-platform hedges/private information, account fragmentation or copying networks. Cluster copied accounts by shared shock/network. Use public behavior to generate distinguishable hypotheses, never establish causal edge. Winner classification must use a prior period; subsequent same-period “validation” is leakage.

## 6. DATA-USE / contamination map

|Surface/period|Documented uses|Classification|Clean validation implication|
|---|---|---|---|
|V2/V3 synthetic simulations / S0 summaries|Design, calibration, diagnostic equivalence|DEVELOPMENT_ONLY|Can test inferential algorithms; cannot prove economic edge|
|V2/V3 weather/market historical periods|No complete access/selection ledger at anchor|UNKNOWN|Treat as unavailable for confirmation until custodian certifies exposure history|
|S1 ECMWF 2023-01-18+, GEFS 2017+, MOS station archives|Metadata archaeology; raw join/use not certified|UNKNOWN|Possible forecast-side development, not certified clean executable economic data|
|Open-Meteo stitched archives, revised observations/reanalysis|S1 flags PIT mismatch|DEVELOPMENT_ONLY|Not decision-time feature reconstruction; final truth may label outcomes separately|
|Command Center two-year statistics and train/validate artifacts|Gold selects high-lock/cities/models; audit inspects aggregates|DISCOVERY_CONTAMINATED|Their published validation is development for Quant, not fresh validation|
|Pondletter July 16–30 2026 described test|Gold uses published outcome to change priority|DISCOVERY_CONTAMINATED|Cannot validate the new priority using same period|
|Named winner analytics / historical incidents|Winner/archetype-driven hypothesis generation|DISCOVERY_CONTAMINATED|Raw data remains useful for mechanism diagnosis only|
|Vendor L2 July–Sep 2026 claimed coverage|Landing-page metadata only; potential overlap with selected external outcomes|UNKNOWN|Unopened != clean; conditional clean certification possible only with exposure/overlap audit|
|Reserved prior forward holdout|Not opened; custody/exposure not verified|UNKNOWN|Preserve seal; do not inspect merely to prove cleanliness|
|Post-lock future capture|Not collected/authorized by this audit|STILL_CLEAN only prospectively and conditionally|No concrete existing historical clean set certified|

**No genuinely clean historical economic validation surface is demonstrated.** This is an epistemic limitation, not a claim every unopened row has been read. Cleanliness is hypothesis-specific and includes indirect published summaries, choice of favorable regime, prior agents and global city/date weather overlap. A new data vendor or withholding buckets from already seen city-days cannot reset it. If historical custody is irrecoverable, classify it development and rely on new chronological observations after lock. Obtain a custodian certificate of date ranges/access logs/hashes without exposing results; raw holdout access stays prohibited.

Leakage firewall: feature availability time is the maximum of issuance/publication, provider receipt, system receipt and required processing completion, with uncertainty; observation time is not receipt time. As-issued forecasts only; no future model cycles, stitched fields, reanalysis features or ex-post station/source corrections. Store raw revisions with their first-seen time; later corrections may label final contractual outcomes but cannot rewrite historical features. Historical books need sequence order/gap checks and original timestamps, not later reconstructed best depth. Settlement knowledge cannot enter an earlier lock state. All mappings, local-day/DST cutoffs, source fallbacks, fees and model versions must be known/versioned before entry.

## 7. Dependence / pseudo-sample size

Matrix DEPENDENCE_UNIT is the minimum unit; no listed unit is automatically independent. Collapse buckets/fills/legs to event inventory P&L first; cluster regional date/system shocks and source/model-release episodes. Nearby stations, high and low, overlapping forecast windows, repeated releases and copying wallets share information. Execution legs share inventory/fill risk. Calendar blocks must exceed empirically defensible weather/bias dependence; define them on development data before seal. Block/calendar sensitivity and date × station effects are useful, but two-way clustering is not a cure for few clusters or persistent serial correlation. Use conservative blocks/small-cluster inference with assumptions declared; under unidentified long memory, refuse a precise CI.

Report counts of city-days, calendar dates, regional episodes, source-version episodes and eligible events, plus concentration and effective block count. A rough autocorrelation diagnostic `N_eff ≈ N/(1+2Σ rho_k)` requires stationarity and is not an independent-count certificate. Power must target post-cost minimum effect and the corrected promotion rule. Repeated buckets cannot buy more power by relabeling them trades. The vendor's stated July–Sep span is at most roughly three months of calendar days before dependence, missingness and holdout allocation; no thousands-of-independent-events assumption is warranted.

## 8. Narrative-overfit attacks

|Gold inference/signature|Observational alternatives|Discriminating observation|
|---|---|---|
|Fast sells → observation latency|Split fills, inventory rotation, post-resolution exit, copying, arbitrage|Receipt-synchronized observation shock precedes entry; matched control shocks; net executable response after attainable lag|
|High-price/high event win rate → safer economics|Near-resolution pricing, negative skew, selected closed winners|Price-conditioned net payoff, full inventory and loss distribution at fixed capital|
|Cheap entries → tail mispricing|Lottery preference, illiquidity compensation, hedged baskets, selected jackpot|Complete loser denominator and conditional probability-price calibration after costs|
|Many fills/short sessions → fast information trader|Order fragmentation/DCA, session cutoff algorithm, maker replenishment|Inventory holding time and maker/taker order lifecycle; session duration alone insufficient|
|High survival rate → fadeable upper buckets|Price already reflects it; ex-post peak/decline labels; wrong settlement sample|PIT locked survival rule versus same-time executable ask/NO cost including late-new-high losses|
|Best city/model → persistent local skill|Best-of-many selection, season/version mix, station mismatch|Nested blocked selection then independent unseen regime with proper scoring and net market comparison|
|Source divergence → oracle alpha|Corrections not yet actionable, harmless rounding, both sources valid in different contracts|Frozen rule identifies payable surface, first-seen divergence and tradable price gap|
|Book reprice near release → causal release edge|Other feeds arrive earlier, common weather shock, stale timestamps|Actual release/receipt clocks, matched non-release controls, negative-control lags and feasible fills|
|Rebate → positive maker overlay|Toxic fills, inventories, conditional reward qualification|Realistic queue/eligibility plus adverse markout and paired incremental economics|

Correlation/event study can establish prediction under a locked information set without identifying an exclusive causal mechanism. Claim that narrower result when causality remains underdetermined.

## 9. Combination-engine red team

Twenty binary edge contexts already admit `2^20=1,048,576` subsets and 190 pairwise interactions before continuous weights. Layers often restate one shock, so multiplying their apparent confirmations creates false certainty. `P(edge_i positive | evidence)` requires a defined target, likelihood, trial history and calibration; no universal posterior is supplied by source grades. The proposed product of mechanism prior × reliability × context × freshness × execution is unsafe: subjective scales need not be probabilities; factors are dependent; a zero in one factor can hide useful information; a positive product cannot manufacture validated net effect.

Safer architecture: (1) immutable full observation registry; (2) outcome-blind collection priority driven by identifiability/value of information/cost and coverage, distinct from (3) hard economic eligibility gates; (4) uncertain net-effect estimation with strong prespecified shrinkage among eligible candidates only; (5) separate composite validation. Monitor any family at zero weight. Give informative unproved feeds collection budget, not trade influence. Structural constraints may veto impossible contracts immediately, but do not boost expected P&L without executable proof.

|Sophisticated zero-edge failure|Safeguard|
|---|---|
|Six layers encode one atmospheric shock as six votes|Common-shock lineage; no multiplying dependent evidence|
|Ex-post city experts fit seasons|Hierarchical shrinkage, fixed context taxonomy, blocked unseen season|
|A lock uses final daily peak|Replay first-seen observations only|
|Model archive gives later corrected vintage|Raw as-issued availability manifest|
|Winner wallets teach a selected profitable label|Outcome-blind controls; archaeology not causal authority|
|Oracle layer assumes current rule applied historically|Per-market rule-version snapshots|
|Maker rebate covers costs only on assumed fills|Conservative queue/eligibility and adverse-selection envelope|
|Active exits choose best subsequent bid|Frozen exit and delay; both legs and residual inventory|
|Basket arb counts unsimultaneous depth|All-leg timing, partial-fill losses, atomicity proof|
|Probability-positive hides rare catastrophic loss|Tail/drawdown guardrails and expected-net check|
|Adaptive weights repair every losing week|Frozen update law; new version/new validation on discretionary change|
|Capture gaps drop fast adverse moves|All-universe missingness accounting, worst-case sensitivity|
|Weights stack overlapping signals on same capital|Single persistent Book and joint portfolio validation|
|Source change erases economics but old evidence dominates|Hard invalidation on semantic changes; new-regime test|

**Maximum safe complexity now:** zero fitted economic routing parameters and zero capital authority. A fixed diagnostic baseline with one predeclared family/target can be formalized after repair; this is an audit testing cap, not deletion of the registry. No effective N is certified, so no numeric ML capacity claim is honest. Generic adaptive mixture-of-experts is presently unacceptable. For a future finite low-dimensional model, a conservative planning screen is at least 20 effective independent blocks per effective fitted parameter, counting selection/contexts/update choices, with enough unseen blocks for corrected power; this is a heuristic ceiling, not a sufficiency theorem. Initially permit intercept + at most one prespecified main effect, no learned interactions, and strongly pooled contexts only if that screen and calibration survive. Estimate effective degrees of freedom including hyperparameter search; heavy tails/dependence may force a much smaller model. Complex models remain research-only until they beat that baseline on new data. No `N/20` calculation from fill count.

## 10. Edge-by-edge authority matrix

Risk codes: M=MEDIUM, H=HIGH, C=CRITICAL. A/B/C/D in evidence cells refer to Gold provenance grades, not these risk codes. Every row has economic decision weight 0. STRUCTURAL is mechanism/correctness authority only; PROMISING is collection priority only. Unlisted measured effect sizes do not exist in this audit. Clean-test column is abbreviated P?: no certified historical test, conditional prospective test after lock/capture. Scope extensions are labeled in comments; winner archetypes and L2 are research instruments, not profit generators.

|EDGE_ID|EDGE_FAMILY|MECHANISM|CURRENT_EVIDENCE_GRADE|MECHANISM_CREDIBILITY|OVERFIT_RISK|DATA_CONTAMINATION_RISK|DEPENDENCE_RISK|EXECUTION_RISK|REGIME_DECAY_RISK|CURRENT_AUTHORITY|WHAT_WOULD_PROMOTE|WHAT_WOULD_FALSIFY|CLEAN_TEST_AVAILABLE|COMMENTS|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|O01|Observation latency|Authoritative observation precedes price response|A mechanism; no edge|plausible|H|H|H|C|H|EXPLORATORY|Receipt-time lead + conservative net executable response|Lead disappears at achievable latency|P?|Gold §§4.3,9 E1|
|O02|Settlement/oracle latency|Contractual result inferable before final repricing|A conditional; no edge|plausible|H|H|H|H|H|EXPLORATORY|Frozen rule version and executable residual gap|No tradable gap or unresolved dispute risk|P?|Distinct from sensor latency|
|C01|Exact resolution source|Source and cutoff determine payable outcome|A conditional rule; no bound market|strong conditional|M|M|H|H|H|STRUCTURAL|Versioned market-rule binding reproduced|Ambiguous or mismatched source invalidates application|P?|Correctness primitive; no standalone alpha|
|C02|NOAA/WU/ASOS divergence|Different surfaces imply different bucket|C/D incidents|plausible|H|H|H|H|H|EXPLORATORY|All divergences including non-events + PIT rule join|Divergences immaterial or already priced|P?|Physical difference is not economic edge|
|C03|Source migration|Legacy pricing follows obsolete source|C mapping|plausible|H|H|H|H|C|EXPLORATORY|Migration dates + blinded pre/post controls|No residual mispricing after execution|P?|Transient participant learning|
|C04|Fallback/outage|Explicit fallback changes contractual outcome|A conditional; D occurrence|plausible|H|H|C|C|C|EXPLORATORY|Complete incident denominator + rule certainty|Outage does not activate fallback or no economic gap|P?|Viewer failure is not source failure|
|L01|High-lock|Running high survives remaining local day|B artifact unvalidated economics|plausible|H|H|H|H|H|EXPLORATORY|PIT survival calibration versus contemporaneous price|Net gap absent or survival calibration fails|P?|Not deterministic before contractual cutoff|
|L02|Low-lock|Running low survives remaining local day|hypothesis only|plausible|H|H|H|H|H|EXPLORATORY|Separate low-market PIT calibration and executable test|Evening fronts invalidate calibration or gap absent|P?|Mirror-image inference insufficient|
|F01|Model-release latency|As-issued run moves prices with delay|hypothesis only|plausible|C|H|H|C|H|EXPLORATORY|Actual publication/receipt times and frozen markout|Response complete before achievable entry|P?|Gold §4.2|
|F02|Paid/pre-schedule dissemination|Earlier lawful access changes information set|not evidenced in Gold|unknown|C|H|H|C|C|DORMANT|Access rights and receipt-time lead independently verified|No legitimate earlier information or costs exhaust gap|P?|Scope extension; do not invent availability|
|O03|ASOS high-frequency access|Faster stream than ordinary polling|A provider documentation|plausible|H|H|H|C|C|PROMISING|Station-specific precision/latency/availability comparison|Quantization or delay eliminates usable information|P?|Frequency != latency; experimental feed|
|C05|Contractual sampling|Included samples differ from physical extreme|A conditional; no reconstruction|strong conditional|H|H|H|H|H|EXPLORATORY|As-seen sampling rule + full inclusion reconstruction|Contract does not use supposed sampling filter|P?|Hourly filtering needs explicit rule|
|C06|Quantization/encoding/conversion|Boundary mapping changes payable bucket|mechanical; no edge|strong conditional|H|H|H|H|H|EXPLORATORY|Boundary tests using exact raw precision and rule|Exact conversions remove divergence|P?|Round once; do not invent missing precision|
|S01|Exact-station effects|Correct station changes target forecast/observation|A conditional; B warnings|strong|M|H|H|H|H|STRUCTURAL|Versioned identifier/timezone/source binding|Wrong station invalidates every dependent claim|P?|Correct mapping prevents false alpha|
|P01|Station microclimate|Local systematic deviation predictable|hypothesis only|plausible|C|H|H|H|H|EXPLORATORY|PIT residual prediction after station/season shrinkage|Incremental value vanishes out of sample|P?|Scope extension from station specificity|
|P02|Upstream physical nowcasting|Upstream atmosphere predicts next local state|hypothesis only|plausible|C|H|C|H|H|EXPLORATORY|Predefined upstream variables add executable OOS value|No incremental forecast/reprice information|P?|Scope extension; common atmosphere dependence|
|F03|City/model specificity|Model skill differs by station/horizon|B selected artifact|plausible|C|H|H|H|H|EXPLORATORY|Nested blocked selection + fresh city-date replication|Selected lift disappears after correction|P?|Gold §3.10; winner city not causal|
|F04|Regime-dependent weights|Weather regime moderates model skill|hypothesis only|plausible|C|H|C|H|C|DORMANT|Frozen pre-trade regimes and shrinkage beat fixed baseline|Benefit disappears on unseen regimes|P?|Scope extension; no flexible experts now|
|F05|Forecast innovation|New minus previous run contains incremental signal|hypothesis only|plausible|C|H|H|C|H|EXPLORATORY|PIT vintages and price-conditioned incremental test|Shock redundant with price or unavailable at entry|P?|Separate skill from delivery speed|
|F06|Ensemble-dispersion shocks|Uncertainty change predicts reprice or risk|hypothesis only|plausible|C|H|H|H|H|EXPLORATORY|PIT members + locked target and proper-score baseline|No incremental calibrated/executable value|P?|Scope extension; target cannot drift|
|F07|Model-version regimes|Version update changes transportability|A change mechanism; no edge|strong drift mechanism|C|H|H|H|C|SHADOW|Version metadata and fresh version replication|No stable performance across declared version|P?|Mostly drift control, not alpha|
|B01|Multi-bucket probability pricing|Mass over subset versus acquisition cost|algebra; empirical q|strong conditional|C|H|H|C|H|EXPLORATORY|Frozen subset/q + all-leg executable test|Net gap absent or subset-selection lift collapses|P?|Adjacent baskets are dependent|
|B02|YES/NO complements|Equivalent payout portfolios differ in cost|structural conditional|strong conditional|M|M|H|C|H|STRUCTURAL|Prove exact payoff/cost/fill equivalence|Incomplete payoff coverage or net gap <=0|P?|Payoff identity != available profit|
|B03|NegRisk identities|Conversions create equivalent payout portfolios|A protocol|strong conditional|M|M|H|C|H|STRUCTURAL|Correct deployed contract + atomicity/leg-risk evidence|Conversion assumptions or net execution fail|P?|Gold §4.1; no frequency proof|
|B04|Logical/physical coherence|Related claims impose probability bounds|algebra/hypothesis|conditional|H|H|H|C|H|EXPLORATORY|Separate exact logical from uncertain physical bounds|Relation false under source/time semantics|P?|Scope extension; physical bounds probabilistic|
|M01|Maker/rebate overlay|Spread/rebate exceeds selection and inventory losses|A conditional rules; no fills|plausible|C|H|H|C|C|EXPLORATORY|Queue-aware fills + eligible realized rebates + adverse markout|Costs/selection erase incremental net|P?|Never assume maker execution|
|M02|Adverse-selection state|Pre-trade state predicts toxic flow|hypothesis only|plausible|C|H|H|C|C|EXPLORATORY|Locked toxicity proxy predicts incremental safe execution|Post-fill features or no OOS value|P?|Diagnostic may have zero decision authority|
|M03|Active repricing/exits|Trade price response before settlement|C behavior inference|plausible|C|H|H|C|C|EXPLORATORY|Both entry/exit books + latency + unmatched inventory|Exit not executable or gains reverse after costs|P?|Session duration is not holding duration|
|H01|Behavioral longshot/favorite|Systematic probability-price distortion|C archetype/hypothesis|unknown|C|H|H|H|H|EXPLORATORY|Price-conditioned calibration and full net loss distribution|Distortion explained by costs/risk or absent OOS|P?|Retain tail hypothesis despite objective preference|
|X01|Cross-venue equivalence|Identical settlement permits relative pricing|A conditional contracts|strong conditional|H|H|H|C|C|STRUCTURAL|Prove source/day/buckets/cutoffs/disputes equivalence|Any payoff mismatch or infeasible transfer/fills|P?|Funding/FX/access constraints included|
|W01|Winner-wallet archaeology|Public fills suggest mechanism candidates|C selected analytics|non-causal|C|C|C|H|H|EXPLORATORY|Preselected controls + complete cash/position reconciliation|Behavior reproduced by non-edge controls|P?|Research instrument, never autonomous alpha|
|D01|Historical L2 event studies|Synchronized feed/books identify response|C vendor claims|conditional infrastructure|H|H|H|C|H|EXPLORATORY|Immutable receipt/sequence/gap provenance and full universe|Reconstructed books or clocks cannot support horizon|P?|Data capability, not edge family|
|F08|Generic ensemble/bias correction|Forecast q exceeds market information|B/C; prior design only|plausible|C|H|H|H|H|DORMANT|As-issued forecasts + fixed development correction + new net test|No incremental net information at feasible power|P?|V3 terminal negative not durably certified at anchor|


Demotion for **every row**: a failed PIT/source/target/execution/calibration/transport check removes its evidentiary authority and moves it to SHADOW or DORMANT; a clean economically null result under current rules becomes NEGATIVE_CURRENT_REGIME, not deletion. Reactivation for **every row** requires an independently logged new regime/source/mechanism observation, restored identifiability, a locked next test and fresh observations. If that changes target/context/execution/horizon, create a child ID and do not inherit parent's confirmation. JSON records these rules individually and gives per-family dependence units. Mechanism falsification differs from economic falsification: absent profitable gaps can falsify current economics without denying a genuine payoff identity.


### Evidence versus plausibility — each family

P=PARTIALLY_VERIFIED; U=UNVERIFIED. Mechanism-observed P includes documented identities/products or historical aggregates, not measured economic mechanism. Historical OOS claims from exposed third-party artifacts remain U as independent validation. Missing evidence in every U cell: **NOT VERIFIED — INSUFFICIENT EVIDENCE**.

|EDGE_ID|Mechanism may exist|Mechanism observed|Measured prospectively|Historical OOS survived|Realistic costs survived|Positive economic evidence|
|---|---|---|---|---|---|---|
|O01|P|U|U|U|U|U|
|O02|P|U|U|U|U|U|
|C01|P|P|U|U|U|U|
|C02|P|U|U|U|U|U|
|C03|P|U|U|U|U|U|
|C04|P|U|U|U|U|U|
|L01|P|P|U|U|U|U|
|L02|P|U|U|U|U|U|
|F01|P|U|U|U|U|U|
|F02|U|U|U|U|U|U|
|O03|P|P|U|U|U|U|
|C05|P|P|U|U|U|U|
|C06|P|P|U|U|U|U|
|S01|P|P|U|U|U|U|
|P01|P|U|U|U|U|U|
|P02|P|U|U|U|U|U|
|F03|P|P|U|U|U|U|
|F04|P|U|U|U|U|U|
|F05|P|U|U|U|U|U|
|F06|P|U|U|U|U|U|
|F07|P|P|U|U|U|U|
|B01|P|U|U|U|U|U|
|B02|P|P|U|U|U|U|
|B03|P|P|U|U|U|U|
|B04|P|U|U|U|U|U|
|M01|P|U|U|U|U|U|
|M02|P|U|U|U|U|U|
|M03|P|U|U|U|U|U|
|H01|U|U|U|U|U|U|
|X01|P|P|U|U|U|U|
|W01|P|U|U|U|U|U|
|D01|P|U|U|U|U|U|
|F08|P|U|U|U|U|U|

## 11. Evidence ladder / weighting without pruning

Lifecycle state and evidence level are separate axes; STRUCTURAL is not a shortcut past execution or validation.

|Level|Required evidence|Permitted decision weight / prohibited claim|
|---|---|---|
|H0 Registered mechanism|Timestamped falsifiable ID, target, lineage, alternatives|Collection only; economic weight 0; no empirical claim|
|H1 Observed mechanism|Reconstructed raw/source episode including controls/denominator|Research diagnosis only; 0; no causality/profit from anecdote|
|H2 PIT-replayable|Immutable availability/rules/versions; outcome-blind replay audited|Development/shadow diagnostics only; 0; no historical executable edge from midpoint|
|H3 Conservative executable development|All costs/legs/latencies/inventory, dependence and trial history; positive adjusted development result|0; contaminated development is not confirmation|
|H4 Locked clean validation|Independent untouched chronological surface; fixed estimand and complexity; program-corrected uncertainty above frozen economic minimum, tail/capacity constraints|Candidate for **locked shadow policy**, no adaptive authority or capital; no forward robustness claim|
|H5 Forward shadow replication|Presealed policy, new complete observations, attainable execution envelope, calibrated inference, no discretionary adaptation|Non-zero **shadow decision** weight may be considered only by governance; still no live/capital authority|
|H6 Robust shadow economics|Predeclared independent regimes, joint Book/composite test, conservative cost/tail stresses, capacity and decay checks|Eligible for separate governance consideration only; audit never authorizes trading|

No family in the examined evidence reaches H4. A trustworthy execution envelope is required even in shadow; no actual maker-order deployment is authorized here. If maker queue validity cannot be verified without new permission, maker economics stay zero. ACTIVE_EVIDENCE requires empirical stage/target/date, never a source label. Observation priority can be high at H0/H1 when the next falsification has high information value; caps and a coverage floor prevent winners monopolizing collection. Evidence weight is a conservative lower-confidence net effect with uncertainty/shrinkage and applicability vetoes, not an arbitrary product of subjective scores. Freeze shrinkage priors and decay on development; never use several layers' agreement as independent replication.

## 12. Durable discovery-ledger schema

Append-only record; corrections append superseding records. Missing historical declaration date stays UNKNOWN, not today's backdated assertion. At minimum:

```json
{
  "HYPOTHESIS_ID": "V4.O01.v1",
  "PARENT_HYPOTHESIS": null,
  "DATE_FIRST_DECLARED": "ISO8601 or UNKNOWN",
  "DISCOVERY_SOURCE": [{"uri": "...", "sha_or_hash": "...", "evidence_type": "A/B/C/D"}],
  "MECHANISM": "...", "EXPECTED_SIGN": "...", "TARGET_VARIABLE": "...",
  "DECISION_HORIZON": "frozen", "CONTEXT": "eligibility known before decision",
  "DATA_ALREADY_SEEN": [{"dataset_id": "...", "period": "...", "exposure": "raw/aggregate/indirect", "agent": "...", "time": "..."}],
  "DATA_NOT_YET_SEEN": [{"sealed_manifest_hash": "...", "custodian": "..."}],
  "PRIMARY_METRIC": "...", "SECONDARY_METRICS": [],
  "FALSIFICATION_CONDITION": "...", "EXECUTION_ASSUMPTIONS": "versioned manifest",
  "DEPENDENCE_UNIT": "...", "CURRENT_AUTHORITY": "EXPLORATORY",
  "EVIDENCE_DECAY_RULE": "versioned", "NEXT_ALLOWED_TEST": "...",
  "TRIAL_FAMILY_ID": "...", "VARIANT_PARAMETERS": {}, "ALPHA_SPENT": 0,
  "LOCK_COMMIT_SHA": null, "DATA_ACCESS_LOG_HASH": null,
  "STOPPING_RULE": "...", "ECONOMIC_MINIMUM": "...", "COMPLEXITY_BUDGET": "...",
  "CODE_DATA_CONTRACT_HASHES": [], "RESULTS_INCLUDING_FAILURES": [],
  "SUPERSEDES": null, "CHANGE_REASON": null, "REVIEWER": null
}
```

A commit preceding the sealed observations, immutable access logs and manifest timestamp prove precedence; a retrospectively written ledger does not. Record every agent's source access and negative/unpublished experiment. Keep candidate ID distinct from event ID and composite ID; composite gains need their own ledger and validation. The schema is a proposed contract, not a fabricated historical exposure ledger.

## 13. Validation architecture and objective audit

DISCOVERY → DEVELOPMENT → independent PRE-REGISTRATION/LOCK → CLEAN VALIDATION → FORWARD SHADOW → robust composite shadow. Discovery adapts freely but marks all exposed data development. Development uses blocked/nested tuning only within its boundary. Blue proposes changes; an independent validator checks the exact locked manifest; custodian controls sealed access. User controls already reserved authorization boundaries. This audit does not declare DATA_T0 or any other t0.

Freeze population/eligibility, station/source/rules, PIT feature graph, labels, primary estimand, capital Book, entry/exit/sizing, fees/fills/rebates/latency, exclusions/missingness, baseline, dependence/blocks, sample/stopping plan, minimum economic effect/capacity/frequency, inferential method and program alpha, all model hyperparameters/update rules, code/data hashes. Custodian releases only the declared endpoint output; full raw access is not casually granted. Keep ongoing discovery on a separate chronological stream, with no outcomes shared across the validation boundary.

New ID for a changed mechanism/target/horizon/threshold/cohort/source mapping/exit or discretionary weight update after results. Bug-only repairs preserving semantics still require hash change and independent impact review; if results influenced the repair or information set, previous validation becomes development and a fresh surface is mandatory. Validation read early, failed subset excluded, or poor result prompting extension contaminates that surface; account for sequentially permitted looks only under the original valid plan. A frozen online update law may adapt features using strictly past data if the **whole law** was locked and evaluated prospectively; discretionary updates reset validation, not alpha. Dormant re-entry follows the matrix rules. Scarce history favors fixed simple hypotheses and future capture, not repeated random splits or continually relabeled holdouts. Failure stops a research package; the library survives.

### Frozen economic estimand proposal

Subject to explicit Blue/owner ratification **before results**, primary: `P(W_30d - W_0 > 0)` over a prespecified current-regime 30-calendar-day opportunity process, one persistent shadow bankroll, no deposits/resets, locked exposure/financing/execution, net all variable and allocated incremental data/operations costs. This respects probability-positive preference while remaining subordinate to North Star wealth growth. Horizon 30d is a proposal, not inferred owner authorization or optimized choice. 7d/90d are descriptive secondary diagnostics with adjusted claims; no switching primary H after results.

Promotion additionally requires a lower confidence bound on expected net wealth increment above a predeclared positive economic minimum and risk constraints on 5th percentile, drawdown, total-loss exposure, capacity/opportunity frequency. Guardrails prevent a strategy winning 99 small gains then one destructive loss from winning the primary objective. Median/win rate alone insufficient. A 5% quantile cannot certify losses rarer than 5%; add explicit bounded-exposure/worst-case stress. Freeze minima before validation; none is supplied by Gold. Multiple co-required gates are intersection requirements; claims across alternative targets/H/candidates still need multiplicity control.

Use non-overlapping locked 30d blocks or a prespecified dependence model for probability-positive; overlapping rolling H outputs are correlated diagnostics, not extra replicates. Three months supplies only about three non-overlapping 30d paths even before weather/regime dependence: no precise probability-positive estimate follows. Bootstrapping a few months does not create unseen tail/regime information. Do not restart capital on every block in the deployment-like trajectory; define comparable conditional state/bankroll and account for compounding, concurrent inventory and reinvestment. If 30d probability cannot be estimated at required precision, label uncertainty and extend only under the predeclared rule or create a new validation epoch; do not replace it with an easier markout metric. Markout is a mechanism screen, not the terminal economic estimand.

### Execution gate

At minimum: aligned clocks with conservative uncertainty; executable ask/bid at attainable entry/exit time and size; depth swept and partial/no fills; order/sequence/gap provenance; frozen delay distribution; queue evidence for maker fills or conservative no-fill envelope; fees/rebate eligibility in force at that time; conversion/funding/FX/capital lockup; all inventory and unfilled legs; source/dispute/settlement risk. Entry ask plus observed future bid is not guaranteed round-trip execution. Positive midpoint response or a hindsight best-depth snapshot cannot promote. Structural payoff identities bypass weather prediction, never non-atomic execution losses.

### Decay and drift

Keep immutable historical evidence; discount **transport relevance**, not inconvenient losses. Exact logical identities remain until contract/protocol conditions change; any source/station/rule/fee/bucket/model-semantic change hard-invalidates dependent application pending fresh binding/test. Routine API/precision/availability changes also trigger replay review. Physical skill needs version/season/site transfer evidence; old version performance cannot simply pool with new. Information latency, maker and behavioral effects need short prespecified review epochs because participant/liquidity learning can erase them. Quirks/incidents get episode-local authority and no extrapolated half-life from one occurrence. Numeric half-lives are currently unsupported: predeclare conservative expiry/no-trade on stale or unverified relevance and estimate decay only in development. Drift monitoring uses frozen triggers and cannot select favorable restart dates.

## 14. Research-process repairs

1. **Registry and exposure custody:** replace Gold §15 deletion with permanent IDs/authority states; recover complete variant/data/source/agent-access history, bind missing V3 synthesis/S4/S6 evidence or mark unknown. Seal candidate-specific clean surfaces without opening them. Keep failure archive and diagnostic source-access ledger.
2. **Confirmatory contract:** freeze the small economic estimand hierarchy, program-wide multiplicity/optional-look budget, dependence units and minimum economic/execution/power criteria before E1–E5 outcomes. Separate descriptive markout from economic promotion. Price-response studies and clean prospective evidence are different stages.
3. **Authority/complexity firewall:** all edges remain observed; all economic weights stay zero through contaminated history. No generic ML experts/interactions/adaptive routing until independent information supports a capped model. Require independent H4/H5 and separately locked composite validation before any non-zero shadow authority.

These are controls to formalize, not a Builder dispatch. Existing prohibitions persist. No additional hypothesis needed to repair process; stop this audit's exploration once these blockers are established.

## 15. What remains scientifically learnable / terminal answers

|Question|Answer|
|---|---|
|Q1 Gold materially adaptively contaminated?|Yes as discovery: rankings/architecture reflect V3 disappointment, winner analytics and selected public model/lock summaries. This is legitimate hypothesis generation, not clean confirming evidence. Complete extent unknown.|
|Q2 Investigate without discarding?|Yes: permanent registry, distinct collection and economic weights, locked future tests. Dormancy is not deletion.|
|Q3 Clean historical surfaces?|None certified. Unopened vendor rows/forecast periods and protected prior holdout remain UNKNOWN until exposure custody/PIT/economic completeness certified; this audit does not open them.|
|Q4 Weighted engine unacceptable combination risk?|Yes under current evidence/unspecified adaptation. Repairable via eligibility gates, capped fixed rules and new composite validation.|
|Q5 Safe maximum complexity?|Now zero fitted economic parameters; no certified N. Future small frozen models only under effective-block/power/complexity screen in §9; no expert ensemble authorization.|
|Q6 Structural/empirical/anecdotal?|Structural conditional: source/station binding, payoff complements, NegRisk, exact cross-venue identities. Empirical: latency, locks, model skill/innovation, microstructure, tail distortion. Anecdotal/third-party support: winner causal stories, incidents, vendor capability. Matrix separates mechanism from evidence; tiers overlap.|
|Q7 Zero-authority monitoring?|Every family, including weak/tail hypotheses, drift, station/contract diagnostics, wallet archaeology and L2 capability. Priorities can differ without deleting IDs.|
|Q8 Non-zero decision authority?|No live authority here. Non-zero locked shadow weight only after H4 corrected clean economic validation + H5 forward replication, PIT/execution proof, frozen tail/capacity minima and independent governance review; composite independently tested.|
|Q9 Proceed to design?|Outcome-blind process/registry/capture-contract design may proceed. Repair research controls before outcome-bearing E1–E5 studies or weighted strategy construction; no Builder authorization.|
|Q10 Falsify direction?|For frozen E1–E5 scope, credible synchronized studies with sufficient power show upper confidence bounds below declared minimum net effect/capacity/frequency at attainable execution, and no rule-robust source/structural advantage. Alternatively inability to recover receipt-time/contract/filled-cost observability makes latency economics unidentifiable with those data. Failure of E1–E5 cannot logically falsify every dormant atmospheric/behavioral hypothesis forever. Do not move targets to avoid current-regime rejection.|

Contract mapping, feed precision/receipt latency, conditional lock prediction and price-response timing can be learned separately from economics. Source diagnostics may materially improve data correctness without generating alpha. Honest no-opportunity/null outcomes are useful evidence.

## 16. What cannot currently be claimed

No identified causal wallet edge; no prospective forecast or timing alpha; no durable lock arbitrage; no validated L2 availability/PIT completeness; no independent 2-year market replication; no calibrated posterior probability of edge; no validated probability-positive economics; no justified composite routing capacity; no certified clean historical market holdout; no independently anchored V3 final negative verdict. Correct protocol identities and source documentation do not establish tradeable frequency, net gains or capital permission.

## 17. Exact next safe step

Blue writes one outcome-blind V4 research contract with permanent family/variant registry, known/unknown exposure manifest, sealed validation custody, primary economic estimand and execution/dependence/multiplicity/complexity budgets. Bind missing prior-work SHA artifacts or explicitly retain UNKNOWN. Independent reviewer checks that exact contract before outcome-bearing E1–E5 work. No acquisition of paid data, capture deployment, reserved holdout access or trading is authorized by this audit.

### Audit progress / deviation ledger

CURRENT_PHASE = COMPLETE; publication verified through branch commit handoff; INPUT_SHA_SET = audit anchor + explicitly linked S0/S1 + pinned external source; FAILED_CANDIDATES/SURVIVING_CANDIDATES = NOT_APPLICABLE (no strategy test); OPEN_QUESTIONS = exposure custody, absent V3 final artifacts, vendor provenance, effective N. WHY = bounded audit needed to test source integrity; SCIENTIFIC_EFFECT = external aggregates now discovery-only, no economic promotion; FROZEN_SURFACE_TOUCHED = NONE; NEW_REAUDIT_SURFACE = any later process contract or strategy composite. NEXT_EXACT_ACTION = commit/push only the two requested audit files. Model identity was not switched or misrepresented; the scientific reviewer role is ASTRA.


WHAT_THIS_AUDIT ESTABLISHES: exact research authority; source/arithmetic integrity within declared scope; missing confirmatory controls and candidate-specific exposure custody; a repairable non-pruning scientific lifecycle.

WHAT_THIS_AUDIT DOES NOT ESTABLISH: profitability, causal winner mechanisms, historical PIT/executable data completeness, clean holdout custody, future edge, or trading/deployment permission.

MOST IMPORTANT UNVERIFIED ASSUMPTION: an untouched, synchronized, contract-correct, executable-cost validation surface can be supplied at sufficient effective information and prospective horizon.

NEXT SAFE RESEARCH ACTION: Blue locks the registry/exposure/estimand/multiplicity/execution/dependence contract; independent review before outcome-bearing studies.
