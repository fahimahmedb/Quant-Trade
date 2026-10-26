# BLUE — OD01–OD03 OWNER DECISION SUPPORT — 2026-10-04

DECISION_SUPPORT_ONLY  
AUTHOR = BLUE  
OWNER_APPROVAL = FALSE  
OD01_OD03_DECISION_SUPPORT = READY_FOR_OWNER_REVIEW

## 1. Authority, chronology and outcome-blind scope

Starting branch: blue/weather-v4-research-design-repair-2026-10-04  
Starting SHA: 06c0c8cf7e0a16b63940d1b2167642dd9dcf889e

Chronology is preserved:
Repair Plan → Decision Support → Owner Decision → Integrated Contract → Independent Astra Audit.

Only Repair Plan and this Decision Support exist in this sequence as authored here. No Owner Decision, integrated completion, approval, freeze or independent audit is created by this memo. Existing Repair Plan, contract, criteria, registry and exposure ledgers remain unchanged. This memo qualifies how to interpret proposals; it does not retroactively complete them.

Sources permitted and used:
- Existing BLUE_V4_REPAIR_CONTRACT_2026-10-04.json at starting SHA; verified blob 60279210d5b8a82472e742ceabf8732477920ba3.
- Existing BLUE_RESEARCH_DESIGN_REPAIR_OWNER_ADDENDUM_2026-10-04.md at starting SHA.
- Already-recorded surface/access metadata from BLUE_V4_EXPOSURE_CUSTODY_LEDGER_2026-10-04.json; only metadata projection read in this turn.
- Mathematical/statistical reasoning and existing non-outcome architectural constraints visible in the Repair Plan: long-run real wealth, single persistent Book, no reset, no implicit phase authorization.

No new market/weather history, P&L, wallet results, backtests, holdout, candidate-performance summaries or economic validation results were accessed. No external empirical comparison was performed. References to prior exposure are metadata, not retrieval or evaluation of its reported performance. EMPIRICAL_COMPARISON_NOT_AUTHORIZED applies whenever determining which option is more profitable, less risky, better calibrated, sufficiently powered or more executable would require new outcomes.

V3_TERMINAL_SHA = fff9f5ed6604cf6cbf5bb3bf90141f033cd0c170  
V3_TERMINAL_STATUS = CLAIMED_BUT_NOT_REPOSITORY_VERIFIED  
HISTORICALLY_EXPOSED_INFORMATION = TRUE  
VALIDATION_STATUS = NOT_USABLE_AS_UNSEEN_EVIDENCE

The previous remote non-resolution is retained; it does not erase prior human/agent exposure to the reported V3 conclusions. Neither those conclusions nor their absence as a resolvable object establish clean data. No fresh V3 resolution or results retrieval was needed for this memo.

REAL_CAPITAL_AUTHORIZED = FALSE  
LIVE_TRADING_AUTHORIZED = FALSE  
t0 = NOT_DECLARED  
DATA_T0 = NOT_DECLARED  
EXPERIMENT_T0 = NOT_DECLARED  
BUILDER_AUTHORIZED = FALSE  
ECONOMIC_DECISION_WEIGHT = 0  
COMPOSITE_ECONOMIC_AUTHORITY = 0

## 2. Common mathematical objects

Let π denote an already-defined candidate policy, not a new strategy. Let S_t=(cash, positions, liabilities, prior wealth and relevant state) be the persistent Book state. Let W_t^R(π) be real net wealth in a fixed numeraire/purchasing-power convention, including inventory, liabilities, variable frictions and consistently allocated operating costs. The deflator, currency and cost-allocation rule are unresolved operational definitions; no inflation/FX data are accessed.

X_H(π,t;S_t)=W_{t+H}^R(π)-W_t^R(π) is the net real wealth increment over H calendar time. R_H=X_H/W_t^R is defined only when W_t^R>0. “NetPnL_H” means this complete net increment under the chosen terminal valuation, not closed-trade P&L excluding open losses or fixed costs.

p_H=P(X_H>0 | target population/regime and admissible S_t); μ_H=E[X_H | same target]. The probability law includes opportunities, non-opportunities, missingness treatment and execution. It is not defined by an arbitrary resampling of convenient observed trades. Equalities/zero P&L are not positive gains. A baseline-adjusted increment X_H^π-X_H^baseline is a distinct estimand, useful for attribution; it must not silently replace absolute real net gain.

All economic preferences and statistical rules require a fixed target population/state distribution before comparisons. No distribution, stationarity, independence, effective information or finite moments are certified here.

## 3. OD01 — materially distinct objective choices

EVALUATION_HORIZON != TERMINAL_OBJECTIVE.

The existing NORTH_STAR is long-run net real wealth growth after actual frictions. A mathematical preference representation can change which uncertain wealth distributions are preferred; a finite primary estimand is a measurement of that preference, not a new North Star.

The small set below exposes genuine choices. It is not a search over new strategies, objective combinations or fitted utility parameters.

|Definition and exact form|Role and benefit|Failure modes and tail implications|Ex-post flexibility, multiplicity and winner-selection bias|
|---|---|---|---|
|Expected wealth gain: μ_H=E[X_H]; prefer larger μ_H subject to chosen risk constraints|Candidate PRIMARY_ESTIMAND or SELECTION_OBJECTIVE; finite proxy for NORTH_STAR. Measures gain magnitude; additive dollar/net wealth interpretation|Rare large gains can dominate expectation; large losses may still be acceptable under mean-only ranking. Mean may be unidentified/infinite under an unspecified law. Sizing/capital differences make unnormalized means incomparable|Changing H, capital, cost allocation or exclusions after results changes the target. Selecting max sample mean among candidates inflates reported performance; noisy/heavy-tail estimates can win. All candidate/variant claims require OD05 accounting|
|Probability-positive preference: p_H=P(X_H>0)|Candidate PRIMARY_ESTIMAND, ELIGIBILITY_CONSTRAINT p_H≥p_min, or SECONDARY_REPORTING_METRIC. Captures preference for ending a window ahead|Ignores gain/loss magnitude; a high p_H can coexist with negative mean or destructive rare loss. Arbitrarily small positive gains count. Costs can move near-zero outcomes across the boundary. Atoms/ties matter|H, outcome threshold, denominators and selected regime can improve apparent p_H. Max empirical p_H has winner bias; best observed win probability is not automatically best economics or most certain. Horizon/subgroup selection adds multiplicity|
|Expected log real wealth growth: g_H=E[log(W_{t+H}^R/W_t^R)] when positive wealth is guaranteed; long-run representation g_∞=liminf_{T→∞} T^{-1}E[log(W_T^R/W_0^R)]|Possible explicit mathematical representation of compounding preference consistent with NORTH_STAR, but OWNER_DECISION_REQUIRED before adoption. Finite g_H could be PRIMARY_ESTIMAND/SELECTION_OBJECTIVE; may instead be SECONDARY_REPORTING_METRIC|Penalizes proportional losses and capital destruction; zero wealth makes log undefined or extended value −∞. Leverage/funding/path state and integrability assumptions crucial. Finite g_H does not prove asymptotic growth; no ergodicity claimed|Post-hoc leverage, floor/truncation of losses, horizon or utility change can manufacture improvement. Empirical maximization across policies/sizing has winner bias. No invented ε wealth floor, utility coefficient or log-optimal sizing rule|

Expected terminal wealth at a fixed T is equivalently W_0+E[X_T] for identical initial state, but extrapolating it to an unbounded horizon needs assumptions not present here. Log growth and expected wealth are not interchangeable; log utility is an economic preference, not a scientific obligation. Absolute mean gain also does not identify repeatability, causal edge or incremental advantage over a financed cash baseline.

Risk measures (drawdown, expected shortfall, concentration) are possible ELIGIBILITY_CONSTRAINTS or SECONDARY_REPORTING_METRICS. They become SELECTION_OBJECTIVES only through an explicit owner tradeoff; no generic “risk-adjusted score” is adopted. Mechanism calibration/markout is diagnostic and not the terminal economic objective.

### ECONOMIC_PREFERENCE versus STATISTICAL_SELECTION_RULE

ECONOMIC_PREFERENCE specifies which true wealth distributions are desirable: gain magnitude, likelihood of ending ahead, compounding and tolerated downside. STATISTICAL_SELECTION_RULE specifies which decisions are justified by finite noisy evidence. A preference for a high true p_H does not justify selecting argmax of observed p_H, and a preference for expected gain does not justify selecting the largest sample mean.

Three materially distinct arrangements may be considered without adopting any:
- Mean-first: expected net wealth increment is primary; probability-positive and risk constraints provide eligibility/reporting.
- Probability-first: probability-positive is primary within a set satisfying positive expected-net and risk constraints; this does not remove North Star wealth growth.
- Compounding-first: log growth is primary under explicit solvency/tail safeguards; net gain and probability-positive provide complementary reporting/eligibility.

No lexicographic order, scalar weighted utility, tie-breaker or arrangement is selected. Probability-first could be lexicographic, constraint-based or a reporting preference; choosing one is a separate owner decision. Strict lexicographic ranking can favor an infinitesimal improvement in one objective over a large improvement in another and may be unstable under estimation uncertainty. All arrangement choices remain OWNER_DECISION_REQUIRED.

### What future promotion could account for — no rule adopted

A future contract could specify a confidence region for (μ_H,p_H,chosen risk measures), candidate-specific execution scenarios, a positive practical-effect threshold and risk caps. Promotion might require conservative bounds to satisfy all co-required conditions rather than compare point estimates. A simultaneous region would protect candidate selection as well as individual claims; a marginal interval alone is insufficient after searching for the winner. These are explanatory possibilities, not implemented acceptance criteria.

Estimation uncertainty → OD04 for valid inference; OD06 for required precision/information.  
Multiplicity → OD05 across candidates, variants, horizons, metrics and repeated looks; a co-required intersection differs from trying alternatives until one passes.  
Dependence → OD04 for shared weather systems, dates, stations, releases and persistent inventory; no naive trade/binomial independence.  
Execution uncertainty → OD10 for attainable fills, costs, delays, unmatched legs and funding; an economic claim could be required to survive a preregistered adverse envelope, with its definition unresolved.  
Minimum practical effect → OD03; mathematical positivity is not practical materiality.  
Negative or inconclusive evidence → OD07: sufficient valid evidence below a required minimum differs from insufficient/invalid information; no favorable horizon switch, indefinite extension or automatic candidate promotion.

A Bayesian ranking/shrinkage alternative would also need locked priors, selection history and calibrated decision consequences; it is not a shortcut past these dependencies. The future comparison/promotion rule remains DEPENDENCY_UNRESOLVED on OD04–OD07/OD10/OD11. Empirical option ranking: EMPIRICAL_COMPARISON_NOT_AUTHORIZED.

## 4. OD02 — horizon and evaluation unit

Only three calendar horizons and one event diagnostic are compared. The 7/30/90-calendar-day labels originate from the existing Repair Contract's recorded primary proposal and secondary diagnostics. Their appearance is inherited design choice, not a statistical convention, operational mandate or owner ratification. No new candidate duration or numerical range is invented. OWNER_DECISION_REQUIRED for primary horizon and whether any secondary horizon is retained.

|Candidate|Exact object and time basis|Preference fit, uncertainty and tail observability|Time, capital, decay, data and execution implications|
|---|---|---|---|
|7 calendar days|Distribution of X_{7d}(π,t;S_t), with μ_{7d} and/or p_{7d} under the selected target; full elapsed time including inactive days|Fits short-run preference for ending ahead; weak view of slow inventory resolution, persistent losses and rare disaster. More calendar windows in a fixed span do not imply more independent information. Endpoint sign may be dominated by valuation/liquidation conventions|Earliest complete window is shorter, not necessarily earlier reliable answer. Charges ongoing costs and locked capital for elapsed time. Could detect short-lived relevance sooner, but does not establish long-run growth. High-quality receipt/book/terminal marks needed; “7 days” does not repair missing fills|
|30 calendar days|Distribution of X_{30d}(π,t;S_t); same cash/inventory trajectory, not a reseeded monthly experiment|Intermediate accounting window and the existing proposal; not statistically privileged. Can mix several inventory/weather episodes but cannot guarantee tail representation. Uncertainty and comparability of starts depend on state/regime|Intermediate wait and capital-use measurement. Drift within the window can affect the target. Costs/funding and open inventory must be valued across the full month; complete data span alone is not execution evidence|
|90 calendar days|Distribution of X_{90d}(π,t;S_t), preserving compounding and unresolved inventory|Longer view of cumulative wealth and operating burden; still no automatic rare-tail certification. Fewer complete non-overlapping windows within a fixed history; neither that count nor elapsed days certify independent information|Later earliest endpoint; may bridge regime/model/source changes, complicating transport. Better visibility of prolonged capital lockup/costs, but obsolete edge can average with fresh edge. Longer consistent Book/contract/version lineage required|
|Completed inventory/execution episode — diagnostic evaluation unit|Z_e=net real cash/inventory change from a preregistered episode start to completion under fixed attribution; duration D_e=τ_exit−τ_entry. Event time, not a fixed economic horizon|Useful diagnostic for fills, capital turnover and loss mechanisms. Completion conditioning excludes unfinished losers unless their censored/open state is retained. It omits no-opportunity time and fixed cost burden if isolated; unsuitable automatic substitute for calendar economics|Wait for completion may be unbounded. Show exposure-time A_e=∫ deployed capital dt and open/censored episodes. Calendar cost allocation must reconcile to Book. Shared shock/inventory makes episodes dependent. Receipt/depth evidence required for both legs|

No effective independent sample size, block count estimate or power is estimated/certified. Any effective-information estimate is DEPENDENCY_ON_OD04. Minimum information, accuracy target and maximum observation duration are DEPENDENCY_ON_OD06. Relative horizon profitability/tail frequency/drift speed cannot be established here: EMPIRICAL_COMPARISON_NOT_AUTHORIZED. A complete calendar window is not a scientifically sufficient sample.

### Exact Book requirements for each candidate

The persistent Book is an existing architectural constraint, not an OD02 option to reset capital for better performance. Reset paths may only be explicitly separate counterfactual diagnostics if later authorized; they cannot feed a deployment-like economic claim as independent bankroll repetitions.

|Definition|Persistent versus reset, window overlap and start|Reinvestment, inactive time and partial exposure|Terminal treatment, financing and fixed costs|
|---|---|---|---|
|7d calendar|One continuous Book. A 7d window starts with actual W_t and inventory/liabilities S_t. Overlapping rolling windows may report a trajectory; non-overlapping windows do not reset inventory or become independent by construction. Reporting choice OWNER_DECISION_REQUIRED|Frozen reinvestment/sizing law, not discretionary reset. Inactive days remain in calendar denominator; partial allocation includes unused cash/opportunity cost under declared baseline. OWNER_DECISION_REQUIRED for reinvestment and cash convention|At t+7d either mark open inventory under a frozen conservative valuation or define a separate force-liquidation policy with costs. No accounting fiction that liquidates then reopens without cost. Funding/fixed costs accrue for elapsed time including inactivity. Choices OWNER_DECISION_REQUIRED|
|30d calendar|Same Book/state requirements at t and t+30d. Monthly labels imply neither fresh capital nor stationarity. Overlap/reporting and conditional start distribution OWNER_DECISION_REQUIRED|Same locked law and cash treatment; intra-month gains can finance later positions only under chosen rule; withdrawn/reseeded capital cannot improve measured gain. Inactive periods and partial exposure retained|Same mark-versus-actual liquidation distinction at 30d; carrying inventory into next window preserves liabilities. Financing and consistently allocated fixed expenses retained. OWNER_DECISION_REQUIRED|
|90d calendar|Same persistent state over 90d. Calendar boundary does not erase prior positions or select an attractive regime. Reporting/start distribution OWNER_DECISION_REQUIRED|Same law; longer compounding changes exposure, not just time scaling. Inactive and partial-exposure intervals included; capital utilization reported separately|Same endpoint distinction at 90d. All operating/funding costs and outstanding claims retained; model/source transitions documented without post-hoc exclusion. OWNER_DECISION_REQUIRED|
|Episode diagnostic|Episode is a subledger of the same Book, not a reset Book. Freeze inventory attribution and start/stop; concurrent episodes can overlap and share exposures. Completion/censoring rules OWNER_DECISION_REQUIRED|Sizing/reinvestment inherited from Book. Episode-only reporting must additionally reconcile no-trade time, idle cash, unfinished exposure and portfolio netting. OWNER_DECISION_REQUIRED for allocation, not permission to drop them|Realized round-trip cash flows plus residual liabilities/partial legs. Open episodes marked/censored per fixed rule. Funding and fixed costs allocated without double counting or omission; reconciliation to calendar Book required. OWNER_DECISION_REQUIRED|

For all definitions: initial nominal/real wealth, currency/deflator, inherited inventory, liabilities, allowed external flows, reinvestment, eligibility/start dates, baseline and cost allocation remain unresolved. Net external deposits/withdrawals must be excluded from gain via a preregistered flow-aware accounting method; policy withdrawals/sizing also affect future state. No wealth amount or live/shadow funding is assigned here.

Marking yields X_H^mark; mandatory liquidation yields X_H^liq under a different policy. They are not interchangeable outcomes. Marking needs conservative attainability/settlement uncertainty and eventual reconciliation; liquidation needs realistic depth, latency, fees and leg losses. Choice OWNER_DECISION_REQUIRED, DEPENDENCY_UNRESOLVED on OD10. Book size and fixed operating budget require non-outcome operational inputs and OD12; no old unrelated personal budget is imported.

## 5. OD03 — positive economics and risk constraints

A = scientific requirement for an interpretable, honest claim. B = economic/risk preference requiring owner choice. A measure's existence does not justify any numerical threshold. All parameters below remain OWNER_DECISION_REQUIRED; no convenient numerical ranges are supplied.

For risks, tail probability β describes the economic distribution's tail; inferential error α describes confidence in an estimated measure. They are distinct, independently chosen, and not assigned values here. Where a measure has no tail parameter, “not applicable” is not permission to skip inferential uncertainty. Confidence method and α are DEPENDENCY_UNRESOLVED on OD04/OD05. A stress set Ω is a declared scenario set, not a confidence level.

|Constraint / exact measure|A: scientific requirement; B: owner preference|Tail/confidence parameter versus numerical limit|Value origin and required information|
|---|---|---|---|
|Positive net performance: μ_H>0; optionally μ_H−μ_H^baseline>0 as distinct incremental gate|A: net all costs, full state and uncertainty; no gross/markout claim as net edge. B: choose absolute and/or baseline-relative eligibility and minimum gain preference|Zero is algebraic break-even, not a confidence level or practical minimum. Whether a bound must exceed it, and its confidence, unresolved|Break-even zero is a definitional economic boundary; not empirical evidence/statistical convention. Chosen gate role = economic preference. Need complete accounting, fixed baseline and execution law|
|Probability-positive: p_H≥p_min|A: correctly defined denominator/state, ties, dependence and uncertainty. B: whether gate or primary, and p_min|No intrinsic tail level. Inferential α separate; p_min unresolved, not an assumed majority/default|p_min = economic preference. Need tolerance for ending behind, magnitude/tails and H; win probability alone insufficient|
|Practical expected gain: μ_H≥δ_min|A: units/scale and uncertainty explicit; feasible economics net of costs. B: dollar, real wealth fraction or hurdle relative to baseline; δ_min|δ_min unresolved. No inherent tail parameter; α separate|δ_min = economic preference, potentially grounded by documented operating/capital constraints. Need budget, capital/time opportunity cost and minimum worthwhile return; no arbitrary buffer|
|Drawdown: D_H=max_{u≤v within window}(W_u^R−W_v^R)/W_u^R with positive reference wealth; also D_{0:T} on full Book history|A: wealth path/marks/missingness correct; distinguish window DD from lifetime peak-to-trough, do not reset peaks silently. B: constrain realized path or quantile/probability of D_H|Measure D; if probabilistic use Q_{1−β_D}(D_H)≤d_max or P(D_H>d_max)≤β_D. β_D, α and d_max separately unresolved|Measure = risk preference; limit/tail = risk tolerance; α = inferential choice. Need liquidity commitments, ability to bear interim losses, marking/execution resolution and OD07 actions|
|Terminal tail loss / VaR: L_H=−X_H (positive means loss), Q_{1−β}(L_H)|A: define loss sign, horizon, atom/quantile convention and full inventory. B: whether quantile limit is useful|β_tail unresolved; α separate; Q_{1−β}(L_H)≤ℓ_max with ℓ_max unresolved. Losses beyond the quantile are not bounded by it|Measure/tail/limit = risk tolerance; no conventional tail level silently chosen. Need economic loss capacity and concern about rare events; quantile alone cannot certify ruin safety|
|Expected shortfall: ES_β(L_H)=β^{-1}∫_{1−β}^{1}Q_u(L_H)du when integrable|A: quantile-integral definition handles atoms; mean tail estimability and integrability required. B: limit average severity in worst β fraction|β_ES unresolved; inferential α separate; ES_β≤s_max, s_max unresolved|Measure and β/limit = risk tolerance; α later inferential choice. Need ability to bear tail severity and future authorized tail coverage; cannot infer from a few completed winners|
|Bounded worst-case exposure: B(S)=sup_{ω∈Ω} loss(S,ω), counting open/partial legs and liabilities|A: explicit Ω and omitted hazards; prove bound under contract/capital semantics, no probabilistic “guarantee” from finite observations. B: allowable hard exposure/loss|No tail/confidence level for a mathematical conditional bound; Ω coverage is separate. B(S)≤b_max; b_max unresolved|Bound mechanics may be operational/contract constraints; cap = risk tolerance or documented operational constraint. Need liability, leverage/funding, source/dispute and leg-risk rules. Max scenario loss is not unrestricted worst case|
|Concentration: C_g(t)=gross loss-bearing exposure in group g / declared positive capital base; g=city, station, date, weather-system; include joint stress loss|A: trace shared liabilities and overlapping groups; no netting unrelated exposures or summing overlapping groups as distinct risk. B: group caps/portfolio stress budget|No intrinsic tail parameter for exposure share; stress-tail model/confidence separate. c_city,c_station,c_date,c_system unresolved|Caps = risk tolerance; group mapping needs OD04 and contract metadata. Need inventory aggregation, system/date definitions and acceptable correlated loss; statistical clustering is not an exposure cap|
|Capacity: K_H(π,c) = maximum deployable policy size satisfying frozen attainable execution/cost/risk constraints; distinguish financial gain at chosen size from scalable gain|A: attainable depth, delays, partial fills and size response; no snapshot depth as sustainable capacity. B: k_min or required viable Book size|Tail treatment belongs to execution/risk envelope, confidence α separate; K_H≥k_min unresolved|k_min = economic preference/operational capital requirement. Need intended capital and OD10 envelope; capacity evidence not authorized here|
|Opportunity frequency: λ_H=E[N_eligible,H]/H under frozen full eligible calendar process; optionally distribution of inactive waiting time|A: eligible/no-fill/no-trade denominators and dependence explicit; trades not independent replicates. B: λ_min or tolerated inactivity|Mean λ has no intrinsic tail level; waiting-time tail level only if chosen; α separate; λ_min/inactivity cap unresolved|Economic preference/operational need. Need acceptable time-to-gain, fixed overhead and capture coverage; no preference invented for “more activity”|
|Execution-cost tolerance: C_H=all variable execution/funding losses under frozen accounting; stress envelope C_H(η), η in declared scenarios|A: real attainable costs and uncertainty; rebates only if eligible; gross profit cannot erase unmatched-leg losses. B: cost ceiling, allowed scenario severity or margin-above-cost hurdle|No intrinsic tail level for deterministic cost cap; if cost quantile then β_cost separate. C_max or allowed budget unresolved; α separate|Measured/contractual components eventually empirical/operational; tolerance = economic preference/risk tolerance. Need size, funding, fee rules, delay/queue uncertainty and budget. No empirical cost estimate accessed|

The log-growth option additionally needs solvency convention W_t^R>0 and treatment of ruin; that is a domain/interpretation requirement, not an invented tolerable ruin probability. The wealth domain, scenario coverage and allowable insolvency risk remain OWNER_DECISION_REQUIRED.

### Unresolved parameters: tighter versus looser, and needed information

|Parameter family|Objectively known now versus preference|Consequence of tighter/looser choice; later dependencies|
|---|---|---|
|μ positivity, baseline, δ_min and units|Net-gain definition and accounting necessity known; attainable effect, viable operating hurdle and owner desired gain unknown|Higher δ_min screens out trivial gain but may require more information; lower δ_min admits less material economics and can lengthen precision needs near zero. Changing units/capital changes the hurdle. OD01/02, OD04–07, OD10–12|
|p_min|Probability ignores magnitudes; no owner minimum known|Higher p_min prefers more frequent positive windows, can reject profitable skewed gains or encourage negative-skew risk if uncoupled. Lower permits more losing windows; it does not inherently permit more tail loss. OD01/02, OD04–07, OD10/11|
|d_max, β_D, ℓ_max, β_tail, s_max, β_ES|Path drawdown, quantile and tail mean differ; no tolerances/levels known|Lower loss caps tighter; smaller β examines rarer tail and usually needs harder-to-obtain tail information. Drawdown/ES tightening can reduce opportunity/capital use; loosening exposes greater severity. More stringent confidence can reduce false certainty but need more information. OD04–07, OD10–12|
|Ω and b_max|Conditional worst-case proof differs from unseen empirical tail; no verified comprehensive hazard set/cap|Broader Ω or smaller b_max is stricter; narrow Ω can create a false safety appearance. Looser cap increases possible loss; cannot remove hazards to pass. OD04, OD07–10, OD11/12|
|Concentration caps and capital denominator|Cities/stations/date/systems can share shocks; no cap or denominator chosen|Lower caps reduce correlated exposure but may lower viable capacity; loosening increases shared-shock loss. More groups do not guarantee diversification. OD04, OD07–11, OD12|
|k_min and intended size|Feasibility depends on size and cost; no intended Book funding is selected|Higher minimum demands economically useful scale but excludes small viable effects; lower minimum permits smaller gains. A larger requested size may worsen fill/cost risk. OD02, OD06, OD08, OD10–12|
|λ_min / inactivity allowance|Calendar inactivity consumes time/overhead; no required activity rate known|Higher minimum favors more opportunity but must not force unvalidated activity. Lower accepts scarce edge and slower time-to-answer; positive net economics still mandatory under chosen gate. OD02, OD04, OD06–08, OD10–12|
|C_max / cost stress severity / practical margin|Costs must be counted; achievable cost distribution and tolerance unknown|Stricter ceiling/adverse envelope can refuse trades lacking margin; looser accepts more implementation risk and can destroy net effect. Double counting costs and δ_min must be avoided. OD03, OD04, OD06/07, OD10–12|
|α and other inferential confidence choices|Economic β, α and numerical risk limits are different objects; no confidence adopted|More stringent error protection generally widens requirements/time; weaker protection increases erroneous-selection risk. Statistical convention can be offered later with source, but cannot justify loss limits. OD04/05/06/11; all DEPENDENCY_UNRESOLVED|

No numerical candidate risk range is supplied. No parameter is labelled empirical evidence without outcomes. Existing calendar labels are inherited arbitrary design proposals explicitly identified in OD02; mathematical zero is break-even. Every economic threshold, tail level, confidence level and numerical limit remains OWNER_DECISION_REQUIRED. Required non-outcome inputs include intended capital/obligations, loss-bearing capacity, fixed operating budget, financing/access constraints and preferred time-to-gain. If choosing a value requires performance distributions, EMPIRICAL_COMPARISON_NOT_AUTHORIZED; request a later authorized evidence phase rather than read history now.

## 6. Dependency map — later decisions are not resolved

|Later decision|OD01–OD03 interaction|Status|
|---|---|---|
|OD04 dependence/inference|Valid law/conditioning, confidence for p/mean/tails, shared shocks and Book state; effective information|DEPENDENCY_ON_OD04; DEPENDENCY_UNRESOLVED|
|OD05 multiplicity|Candidate/metric/horizon comparisons, simultaneous selection protection and repeated looks|DEPENDENCY_UNRESOLVED; no error budget/procedure adopted|
|OD06 information/duration|Precision, tail evidence, maximum duration and time-to-answer|DEPENDENCY_ON_OD06; DEPENDENCY_UNRESOLVED; no sample size certificate|
|OD07 stopping/reopening|Negative versus inconclusive, safety suspension, no rescue extension or post-result target switch|DEPENDENCY_UNRESOLVED; no stopping rule adopted|
|OD08 capture|Whether future scope can measure cash/inventory/cost/no-opportunity and chosen horizons|DEPENDENCY_UNRESOLVED; no option chosen/activated|
|OD09 custody|Hypothesis-specific clean evidence and permitted access/release|DEPENDENCY_UNRESOLVED; no actors appointed/unblind|
|OD10 execution|Valuation versus liquidation, size/capacity/funding, cost and risk envelope|DEPENDENCY_UNRESOLVED; no fill law/stress values adopted|
|OD11 promotion/complexity|Which joint bounds/gates justify future authority; policy/update degrees of freedom|DEPENDENCY_UNRESOLVED; no promotion rule or model chosen|
|OD12 resources/authorization|Capital assumptions, operating budget and separately authorized later phases|DEPENDENCY_UNRESOLVED; all hard authority flags unchanged|

Owner can state preferences before inference is designed. Operational feasibility and final statistical contract may still be unresolved afterward. These dependencies are not a reason for Blue to decide them by implication. A future integrated contract must record where the owner's preference cannot be measured with approved resources rather than redefine it for an easier result.

## 7. Owner choices exposed and next safe action

OD01 — choose the intended economic preference/primary estimand and role of the other two; decide whether any ranking, co-required eligibility or lexicographic order is desired. OWNER_DECISION_REQUIRED. None approved.

OD02 — choose primary calendar horizon and optional reporting units; specify conditional Book/start population, initial wealth/inventory, cash/reinvestment, external-flow accounting, overlap reporting, terminal mark/liquidation and cost definitions. OWNER_DECISION_REQUIRED. Thirty days is one option, not adopted.

OD03 — choose which positive-economics/risk constraints apply, their measures, distinct tail/confidence parameters, units and numerical thresholds with documented origin. Values lacking defensible grounding remain unresolved rather than receive convenient defaults. OWNER_DECISION_REQUIRED.

Next safe action is owner review and an owner-authored or explicitly owner-ratified decision artifact, limited to OD01–OD03 and honest about remaining dependencies. Partial ratification is permissible; unresolved parameters must remain explicit. Blue subsequently integrates only ratified choices into a new version-bound contract; independent Astra audit comes afterward. Neither this memo nor owner preference review activates capture, E1–E5, backtests, Builder, paper economics, validation, optimization or capital.

ECONOMIC_PROGRESS = clarified genuine objective, horizon and risk tradeoffs without creating a new search space.
REMAINING_BLOCKER = unratified OD01–OD03 and unresolved later statistical/operational dependencies.
EXIT_CONDITION = owner review/explicit ratification, followed by integrated contract and independent audit before any separately authorized phase.
OUTCOME_BLIND_CHECK = PASS_THIS_MEMO_SCOPE.
NEW_OUTCOMES_ACCESSED = NONE.
NEW_DATA_ACCESSED = NO_NEW_OBSERVATIONAL_OR_OUTCOME_DATA; permitted existing contract/addendum/exposure metadata and Git metadata only.
FILES_MODIFIED_OUTSIDE_SCOPE = NONE.
