# BLUE — OD04–OD12 ONE-SHOT OWNER DECISION SUPPORT — 2026-10-04

DECISION_SUPPORT_ONLY = TRUE  
OWNER_APPROVAL = FALSE  
AUTHOR = BLUE  
OD04_OD12_DECISION_SUPPORT = READY_FOR_OWNER_REVIEW

## 1. Verified authority and scope

Mandatory owner authority:
- branch owner/weather-v4-od01-od03-decision-2026-10-04;
- SHA 377af70116f24f486feac7b4da5d2873107822a2;
- research/weather_forward/v4/owner/OWNER_OD01_OD03_DECISION_2026-10-04.md;
- verified blob a64a29069d6a3b8a6e4166f27a3d9159b86fd3d7.

Prior design authority:
- Repair Plan at 06c0c8cf7e0a16b63940d1b2167642dd9dcf889e, blob 8cb60f0d28c5b041ee043add4d7a73affa1c86e8;
- OD01–OD03 support at af77165c26308bc085fabf44282e2bacd09bdbb4, blob 89220aa71d539a168256784f0f26709360faf738.

All commits and named artifacts independently resolved remotely at exact SHAs. Owner branch HEAD verified at the mandatory SHA. Parent chain: Owner Decision → OD01–OD03 Support → Repair Plan. The new Blue branch starts from the owner SHA and changes only this new document; no owner-branch mutation or existing-artifact rewrite.

Preserved owner decisions:
OD01 = RATIFIED  
OD02 = PARTIALLY_RATIFIED  
OD03 = PARTIALLY_RATIFIED  
PRIMARY_EVALUATION_HORIZON = RATIFIED_30_CALENDAR_DAYS  
ECONOMIC_PREFERENCE = Probability-first  
STATISTICAL_SELECTION_RULE = UNRESOLVED  
ECONOMIC_AUTHORITY = 0  
EXPECTED_NET_ECONOMICS_GATE_REQUIRED = TRUE  
EXPECTED_NET_ECONOMICS_GATE_OPERATIONAL = FALSE  
RISK_GATE_OPERATIONAL = FALSE  
TAIL_SEVERITY_GATE_REQUIRED = TRUE  
P_MIN_ROLE = UNRESOLVED

The primary class is probability of positive finite-horizon net real wealth change; the North Star remains long-run net real wealth growth after all real frictions. Neither argmax empirical probability nor a lexicographic selection procedure is authorized. The single persistent Book and prohibition on economic resets are ratified. Start-state population, inventory/flows, terminal valuation/liquidation, cost allocation, overlap, dependence and execution remain unresolved. Required positive practical economics, drawdown/path risk, tail severity, catastrophic exposure, concentration, executable capacity and execution-friction protections retain unresolved measures/levels/limits. No convenient default completes them.

Chronology: Repair Plan → Decision Support → Owner Decision → Integrated Contract → Independent Astra Audit. This new support follows the limited OD01–OD03 Owner Decision and precedes any OD04–OD12 Owner Decision or integration. This is not a completed/frozen contract, owner decision, experiment, validation, Builder mission or capture permission.

REAL_CAPITAL_AUTHORIZED = FALSE  
LIVE_TRADING_AUTHORIZED = FALSE  
t0 = NOT_DECLARED  
DATA_T0 = NOT_DECLARED  
EXPERIMENT_T0 = NOT_DECLARED  
BUILDER_AUTHORIZED = FALSE  
ECONOMIC_DECISION_WEIGHT = 0  
COMPOSITE_ECONOMIC_AUTHORITY = 0  
OBSERVATION_AUTHORITY = UNCHANGED

## 2. Shared definitions, optionality and dependency types

Let X_30(π,t;S_t) be 30-calendar-day net real wealth change for a previously defined policy π starting in persistent Book state S_t. p_30=P(X_30>0) is the owner-ratified estimand class, conditional on an as-yet unresolved start-state/regime population. μ_30=E[X_30] describes the required expected-net gate. This notation does not complete accounting, costs or the probability law. A primary label, many fills or one long trajectory cannot identify that law by themselves.

Scientific requirements below mean requirements for valid, correctly scoped claims. Preferences include tolerated error, practical precision, duration/cost limits, numerical risk limits and choice among defensible designs. Methods require justified assumptions; choosing a method does not make those assumptions true.

For every OD:
DESIGN_DEPENDENCIES = definitions, assumptions and evidence needed to describe a coherent option.
DECISION_DEPENDENCIES = owner choices needed to adopt it as a contract.
ACTIVATION_DEPENDENCIES = separate exact permission, reviewed implementation/access and prerequisites needed to run it.
None implies the next.

BEFORE FREEZE: preserve useful scientific optionality.  
AT FREEZE: deliberately remove optionality by explicit preregistration.  
AFTER FREEZE: do not recover optionality after observing outcomes.

Options A/B/C are materially different design alternatives, not numerical tuning candidates. No option is selected, no error budget or sample size is supplied, and no method is declared empirically superior.

V3_TERMINAL_SHA = fff9f5ed6604cf6cbf5bb3bf90141f033cd0c170  
V3_TERMINAL_STATUS = CLAIMED_BUT_NOT_REPOSITORY_VERIFIED  
HISTORICALLY_EXPOSED_INFORMATION = TRUE  
VALIDATION_STATUS = NOT_USABLE_AS_UNSEEN_EVIDENCE

Remote non-resolution does not erase historical exposure. No V3 results are consulted here.

## 3. OD04 — dependence and inference

Scientific requirements: collapse buckets, fills and execution legs belonging to one economic event before counting information; preserve joint inventory/cost economics. Track dependence across calendar time, regional weather systems, cities/stations, shared release cycles, source-version episodes and persistent Book state. Overlapping 30d windows share outcomes; non-overlapping windows may still share weather, inventory, compounding or regime. City/date two-way clustering alone does not remove serial or release dependence. No independence or effective N is certified.

|Option|Definition, consequence and scientific conditions|What becomes harder/impossible; optionality/contamination; operational cost|
|---|---|---|
|A Conservative calendar/system blocking|Preregister blocks and system/episode grouping; aggregate Book increments and use a dependence-valid block method with justified separation/mixing and small-sample behavior. Keep overlap as reporting or explicitly account for it|Broad aggregation can lose precision; too few blocks means no precise p_30/tail claim. A block boundary is not proof of independence. Freeze lengths/grouping before validation; no post-result finer split to gain significance. Grouping/logging cost; no measured information gain|
|B Structured joint dependence model|Preregister a model for calendar serial structure, city/station/weather/release effects and conditional Book starts; assess calibration under declared assumptions in a later authorized development phase. Estimate p_30 from the specified law, not a binomial count of fills|Can exploit structure but misspecification distorts uncertainty, especially tails; high-dimensional parameters need OD11 limits. Underidentified model means inference unavailable. Fitting or model-switching on sealed results contaminates. Greater specification/calibration/maintenance burden|
|C Assume little; bounded or partially identified conclusions|Use demonstrated contractual exposure bounds and conservative sensitivity/identified sets; where a justified probability law is absent report bounds or NOT_IDENTIFIED/INCONCLUSIVE instead of a precise distribution|Cannot infer useful p_30 from no information or arbitrary dependence; worst-case bounds may be vacuous. Bounds require real scope assumptions, not fabricated guarantees. Less fitting; may need more future collection and delay a decision. No post-result selection of an optimistic sensitivity case|

Small clusters: asymptotic cluster-robust errors can fail with few independent clusters. Finite-sample/randomization methods require their own actual invariance/assignment assumptions; observational weather is not randomized by declaration. A valid small-cluster procedure may be considered only after its assumptions and intended claim are justified. Bootstrap repetition creates no independent episodes. Persistent Book dependence requires either a justified conditional start-state distribution or appropriately limited trajectory-specific reporting, neither adopted.

OWNER_DECISION_REQUIRED: dependence representation, conditioning/start-state population, overlap treatment, inference/sensitivity method and assumption-failure outcome. Structural parameters needing empirical determination remain unknown: EMPIRICAL_COMPARISON_NOT_AUTHORIZED.

DESIGN_DEPENDENCIES: OD02 unresolved Book/overlap; OD08 metadata graph; OD10 joint inventory; OD11 model degrees of freedom.
DECISION_DEPENDENCIES: OD05 claim/error scope; OD06 precision/information; OD07 looks; remaining OD03 tail measures.
ACTIVATION_DEPENDENCIES: exact integrated/audited contract, authorized development calibration and clean validation access under OD09/12; none authorized now.

## 4. OD05 — multiplicity and looks

Scientific requirements: one complete trial/variant graph for the 33 canonical families and all descendants, including failed/negative/unpublished variants. Thirty-three registered families are not thirty-three independent economic tests. Include cities/stations, contexts, sides, horizons, entry/exit, source choices, execution and objectives that can affect selection. H4 clean evidence cannot be recovered from exposed history by retrospectively guessing a trial count.

|Option|Definition and consequence|Harder/impossible; optionality and cost|
|---|---|---|
|A Finite-batch family-wise control|A locked finite list of primary economic claims with valid dependence-aware tests/regions and program-level family-wise error control. Holm is one possible implementation; not selected. Allocation across future batches explicitly capped|Requires committing candidate list/claim scope before look; strongest protection against even one false promotion can reduce discovery throughput. Future descendants consume remaining budget, not fresh names. Enumeration and audit cost; ordinary failures remain recorded|
|B Sequential family-wise program|Predeclare program allocations and valid time-uniform tests/regions or a proved spending design for permitted looks. Need validity under actual dependence, filtration, tails and stopping|Can support informative looks but may be impossible if assumptions/wealth bounds or dependence cannot support the method. Repeated naive fixed-time intervals are invalid. Greater design, release logging and calibration cost; optionality only within frozen law|
|C FDR-controlled exploratory screening, separate confirmatory gate|Control expected false-discovery proportion for a declared exploratory claim family using a dependence-valid procedure; keep economic authority zero until separate fresh confirmatory evidence with separately specified protection|FDR does not promise no false promotion and cannot alone satisfy economic authority. BY is an illustrative dependence-robust FDR procedure under valid p-values, not adopted. More exploratory throughput may consume data and new-validation resources; selected survivors need selection-aware confirmation|

Bayesian shrinkage may regularize estimates but is neither automatically FWER/FDR control nor an authority grant; prior/model selection must be recorded. No Holm, BY, alpha-spending, Bayesian or numerical convention is adopted. The Repair Plan's FWER 0.05 and geometric allocations are prior illustrative proposals (statistical convention/design choice), not owner-ratified limits. This memo adds no numerical error level.

Ratified secondary 7d/90d outputs are descriptive unless separately preregistered inferential claims; they cannot rescue primary confirmation or change stopping. Declaring them “descriptive” does not make outcome-driven candidate/context selection harmless. Subgroup/horizon comparisons, interactions and child selection remain exposure and multiplicity records.

A failed test does not refund consumed error by default. Under an explicitly proved rule, unspent allocations or graph-based recycling may be transferred only as that frozen rule allows; that is redistribution, not resetting lifetime risk. New epochs, child IDs, markets or agent sessions cannot replenish a budget to repeat the same claims. A separately named future program cannot evade repeated-selection accounting or evidence reuse. No replenishment rule is adopted.

OWNER_DECISION_REQUIRED: inferential claim scope, FWER versus exploratory FDR roles, finite/sequential architecture, global budget, allocation/recycling law, secondary/subgroup treatment, complete-history failure rule.

DESIGN_DEPENDENCIES: OD04 valid dependent statistics; full hypothesis lineage; OD11 selected-policy claim scope.
DECISION_DEPENDENCIES: OD06 available information/precision; OD07 looks; statistical selection rule still UNRESOLVED.
ACTIVATION_DEPENDENCIES: audited exact claim/variant manifest, authorized analyses/releases OD09/12; no testing or budget consumption authorized here.

## 5. OD06 — minimum information and maximum duration

Scientific requirements: distinguish availability/coverage from economic information. Independently justified cluster/episode counts, eligible denominator, Book start-state representation, concentration, tail support and corrected inferential precision are different prerequisites. Many markets/buckets/fills/days cannot substitute for one another. Tail absence does not prove tail safety. Ratified tail severity requires a defensible measure and informative evidence or an explicitly adequate hard bound.

|Option|Definition and consequence|Harder/impossible; contamination/optionality and cost|
|---|---|---|
|A Fixed duration with prespecified adequacy checks|Lock one maximum endpoint, minimum-information conditions and required precision before outcomes; evaluate at endpoint and report INCONCLUSIVE if adequacy fails|Calendar deadline cannot guarantee sufficient independent information or tails. No post-result extension to rescue primary. Predictable maximum resource commitment; low frequency may leave evidence insufficient|
|B Information-targeted plan with hard calendar ceiling|Predeclare valid information/precision targets, their monitoring/release law and maximum calendar duration. Stop only under OD07/OD05-compatible design|If information is outcome-dependent, stopping invalidates naive inference; time-uniform/valid planned monitoring needed. Mere data-volume monitor can leak prevalence/outcomes. More control/custody overhead and uncertain runtime within cap|
|C Staged feasibility then a separately locked economic epoch|A later explicitly authorized metadata/operational feasibility stage determines observability/coverage; economic specification then locks on a fresh clean surface|Staging cannot measure economic variance/tails from metadata alone. Any outcome-bearing pilot becomes development and cannot be unseen confirmation; whole selection process must be logged. Extra calendar delay and potentially duplicated setup/storage; useful optionality only before freeze|

OWNER_DECISION_REQUIRED: minimum-information definitions, primary precision tolerance, expected-net practical effect, tail estimator/level/adequacy, maximum duration, low-frequency resource policy and insufficient-information outcome. No sample size, power, frequency, duration forecast or effective N is invented. EMPIRICAL_COMPARISON_NOT_AUTHORIZED for power/variance/prevalence/duration comparisons needing outcomes. Operational receipt completeness alone can prove data health, not economic power.

Low opportunity frequency remains in the calendar economics, including idle capital/fixed costs. It may force INCONCLUSIVE, a smaller scope, or a separately authorized later epoch; cannot justify counting correlated buckets as new information, silently changing the primary estimand or picking high-frequency cities after results.

DESIGN_DEPENDENCIES: OD04 information model; OD03 tail and practical minima; OD08 coverage; OD10 observable fills.
DECISION_DEPENDENCIES: OD05 error/precision tradeoff; OD07 stopping; OD12 cost/time ceiling.
ACTIVATION_DEPENDENCIES: authorised data phase and access, locked adequacy/endpoint rules and independent audit; no pilot, power study or capture now.

## 6. OD07 — stopping, continuation, failure and reopening

Scientific requirements: stopping law follows validity assumptions and exact frozen primary contract. Safety/data-integrity actions preserve all adverse evidence; suspension is not successful confirmation. Terminal statistical failure, practical insufficiency and data invalidity are different outcomes.

|Option|Definition and consequence|Harder/impossible; optionality/contamination and cost|
|---|---|---|
|A Fixed primary endpoint|One terminal analysis at preregistered duration; earlier only permitted outcome-blind health/safety actions; evaluate frozen success/failure/adequacy gates|No economic early success/extension from interim results. Wastes some time on a weak package but lowers look complexity. Early economic futility needs a separately valid predeclared rule, not an informal peek|
|B Valid sequential primary plan|Predesign time-uniform bounds or proved planned-look procedure plus success/futility/information-cap rules|Needs OD04/05 validity and outcome access controls. Repeated conventional intervals cannot implement it. Greater calibration/logging cost; no retrospective threshold/look-date edits|
|C Planned two-stage economic design|Preregister stage-one decision boundary, futility/continuation and terminal maximum; account for selection and error across stages|Only two stages by label is not validity; actual boundaries/claim accounting need proof. Futility may be binding or nonbinding only as prespecified. Restricted adaptivity can save resources but must not choose a new policy/horizon on the same confirmatory outcomes|

Illustrative logic, NOT chosen rule: valid sufficient evidence placing an economic upper bound below the practical minimum supports failure of the frozen current-regime package; a region spanning the minimum gives INCONCLUSIVE; missing PIT/execution/identifiability gives NOT_VALIDATABLE. Required risk-gate failure cannot be overruled by high primary win probability. Safety breaches may mandate suspension before inference, with logged causes and complete losses.

Continuation must follow a frozen valid law within OD06's cap; at the cap inadequate evidence remains INCONCLUSIVE. A new contract/epoch after failure keeps failure in trial history, uses remaining budget and new clean observations. Reopening needs independently logged source/regime/mechanism rationale and restored identifiability. Material target/context/horizon/rule/source/sizing/exit changes create a child; engineering-only repairs still need version and independent impact review.

SECONDARY_HORIZONS_MAY_RESCUE_PRIMARY_CONFIRMATION = FALSE  
SECONDARY_HORIZONS_MAY_CHANGE_PRIMARY_STOPPING_OR_CONTINUATION = FALSE  
SECONDARY_RESULT_TRIGGERED_CHILD = NEW_VALIDATION_REQUIRED

OWNER_DECISION_REQUIRED: fixed/sequential/staged plan, numerical boundaries and limits, futility status, safety actions, continuation/reopening law and treatment of INCONCLUSIVE. No thresholds or rule selected.

DESIGN_DEPENDENCIES: OD04 valid primary uncertainty; OD05 looks/child accounting; OD06 adequacy/cap; OD10 safety semantics.
DECISION_DEPENDENCIES: unresolved OD03 limits; OD09 permitted health/outcome releases; OD11 promotion.
ACTIVATION_DEPENDENCIES: exact approved stopping contract, named safety authority/release permissions and separately authorized phase OD12.

## 7. OD08 — prospective capture architecture

Scientific requirements: immutable first-seen raw records/revisions, timestamp uncertainty, sequence/gap provenance, versioned contract bindings, full eligible/missingness denominator and hypothesis-specific exposure custody. Completeness and receipt timing must be demonstrable; a schema is not data.

|Option|Definition and consequence|Harder/impossible; optionality/contamination and cost|
|---|---|---|
|A Broad sealed capture|Predesign broad outcome-blind source/market scope with coverage floor; keep raw outcomes behind custody|Preserves possible later tests only if hypotheses/selection were independent of captured and correlated outcomes. Large storage/transfer/permission surface; metadata leakage and incomplete scope harder to govern. Dormant hypotheses cannot claim clean status from seal alone|
|B Narrow locked-package capture|Collect only complete universe/control/denominator inputs for an explicitly selected preregistered package|Lower capture/storage/access burden but other dormant families may lack required data and require fresh capture later. Narrowing based on seen success contaminates. Completeness must cover failed/no-opportunity events, not just candidate triggers|
|C Separated discovery and validation streams|Predesign chronological/system-aware partition and independently controlled validation branch; discovery outcomes remain marked development|Allows continuing research but correlated weather/releases/wallet summaries can cross the boundary. Merely different stations/vendors/buckets is insufficient separation. Duplicate storage/routing and access auditing cost; validation stream cannot be cherry-picked after discovery|

GENERIC_SCHEMA_FIELDS: immutable record/surface IDs; content hash/raw reference; source/version; event/publication/provider/system/processing timestamps and uncertainty; provenance; sequence/gap/correction; manifest/access/exposure IDs; bindings; supersedes; missingness reasons. Conceptual extensibility does not select an operational source.

WEATHER_SPECIFIC_OPERATIONAL_FIELDS: exact station identifiers/location and source role; contractual local day/DST/cutoff; high/low/variable/units/precision/rounding; model/run/lead; sampling/fallback/revision; venue/condition/token/bucket; endpoint/auth/license; universe, source priority, polling cadence. These remain OWNER_DECISION_REQUIRED and/or future separately authorized operational design, not populated here. Ratified 30d horizon alone mandates none of their exact values.

No exact station, endpoint, model, cadence, universe or source priority is chosen. Contract-source semantics may later constrain a binding, but no particular market binding is instantiated. No collector code, deployment or activation.

DESIGN_DEPENDENCIES: OD04 correlated-surface graph; OD06 adequacy; OD09 custody schema; OD10 receipt/book/contract requirements.
DECISION_DEPENDENCIES: capture option/scope, lawful feasibility and cost ceilings OD12; target package/complexity OD11.
ACTIVATION_DEPENDENCIES: separate operational design approval, reviewed implementation, access rights, explicit capture authorization and timestamps OD12; not inferred here.

## 8. OD09 — custody, access and unblinding

CAPTURED != CLEAN  
SEALED != CONFIRMATORY_CLEAN

Scientific requirements: candidate-specific direct/indirect exposure ledger; timestamped preregistration precedence and independent selection; complete lineage/access/manifests; no inferred absence of exposure from unopened raw files. Preserve six cleanliness prerequisites in the owner addendum. Related dates/cities/stations/upstream systems/releases/derived summaries/agent access count. Missing history remains UNKNOWN. A sealed dataset may be contaminated for one child and admissible for another only with positive certificates.

|Option|Capture/custody/access/release architecture|Harder/impossible; contamination and cost|
|---|---|---|
|A Independent custodian|CAPTURE_OWNER writes; separate CUSTODY_OWNER seals/manifests; RESEARCH_ACCESS receives approved outcome-free metadata; OUTCOME_ACCESS only exact endpoint outputs; named UNBLIND_AUTHORITY authorizes custodian release|Best organizational separation but needs independent actor/service and availability. Endpoint projection itself may leak outcomes. Human/service overhead and controlled release auditing; no named person appointed here|
|B Technically isolated vault with independent approval|Dedicated capture identity writes encrypted/content-addressed records; custody service controls immutable manifests/ACLs; research lacks decrypt rights; independent designated reviewer/owner approves release procedure|Automation lowers recurring burden but key/admin/log design can undermine separation. A shared administrator capable of reading outcomes requires explicit access/incident accounting, not a claim of perfect blindness. Setup/security/recovery cost|
|C Documented shared-role custody with independent pre-release review|Where staff scarce, role overlap declared; mechanical isolation/access logs plus outside exact-release review; use restricted authority when independence cannot be certified|Cheaper staffing, weaker assurance. If designer has outcome access or unexplained logs, clean confirmation impossible for affected hypotheses; data remains development/UNKNOWN. Additional fresh validation may cost more than saved custody effort|

No option waives hypothesis-specific cleanliness. Immutable manifests carry hash/time/scope/ACL and chain corrections; access logs distinguish capture, access, viewing, outcome-viewing and design use. Release procedure later binds hypothesis/lock SHA, code hash, data manifest, approved output, recipients and timing; no raw broad dump by default. Missing logs/summary leaks/exception dashboards/volume proxies trigger incident record and affected-surface reclassification, independent review and fresh validation where required. Deleting a leaked output never restores blindness.

OWNER_DECISION_REQUIRED: actual CAPTURE_OWNER, CUSTODY_OWNER, RESEARCH_ACCESS, OUTCOME_ACCESS, UNBLIND_AUTHORITY, key/admin roles and RELEASE_PROCEDURE. No date or release authorization assigned.

DESIGN_DEPENDENCIES: OD08 manifests/projections; OD04 overlap graph; stopping/looks OD07; historic exposure recovery.
DECISION_DEPENDENCIES: role separation/resources OD12, exact look/output permissions OD05–07.
ACTIVATION_DEPENDENCIES: verified technical controls and custody certificate, exact frozen/audited contract and separately approved unblind operation; no vault implementation/access expansion here.

## 9. OD10 — execution envelope

Scientific requirements: executable information set and whole Book economics at attainable size/time, not midpoint markout. Count no-fill, partial legs, unmatched inventory, fees/rebate eligibility, latency/clock uncertainty, depth depletion, financing, transfer/funding restrictions and contract/source/oracle/dispute/void risk. Maker limit-price touch is not queue/fill evidence.

|Option|Definition and consequence|Harder/impossible; contamination and cost|
|---|---|---|
|A Conservative taker-only economic envelope|Predesign marketable execution with attained latency, swept-depth/partial/no-fill and adverse cost assumptions; maker remains diagnostic/zero authority|Simpler queue requirements but taker spread/impact can erase gain or constrain capacity. Requires synchronous depth and both legs, not just quotes. Data/provenance cost; unknown latency cannot be optimistically filled|
|B Execution uncertainty/partial-identification envelope|Bound economics over independently justified fill/delay/depth/cost scenarios; use conservative identified sets; do not claim point profitability where envelope is unresolved|May be vacuous or cannot promote if optimistic/pessimistic bounds straddle practical gate. Scenario extremes need defensible scope, not cherry-picking. More stress bookkeeping but avoids unsupported exact fill model|
|C Maker-inclusive envelope conditional on queue evidence|Predefine queue, priority/cancel/partial-fill, adverse-selection and inventory model; require independently evidenced behavior and rebate qualification before maker economics|Without approved independent queue/fill evidence maker economics remain zero/unidentifiable. More order-event fidelity/calibration/custody; no real order deployment authorized to obtain it. Changing queue model after favorable outcomes contaminates|

A liquidation endpoint is a policy with executable costs; marking retains inventory/settlement uncertainty. Compare alternatives as accounting/execution choices, not interchangeable outcomes. Conservative marking needs availability/valuation/error rules and eventual reconciliation; forced liquidation needs achievable bids/depth/delay and leg risk. OWNER_DECISION_REQUIRED: terminal valuation, liquidation, cash/funding/cost allocation and tolerable execution envelope. Delay, size, no-fill/partial-fill rule, fee/version, rebates, funding/transfer and dispute stress values remain unresolved. No new execution outcomes or latency advantages accessed.

DESIGN_DEPENDENCIES: OD02 full Book/state/accounting; OD03 capacity/friction/risk measures; OD08 raw receipts/bindings/depth.
DECISION_DEPENDENCIES: selected envelope, cost tolerances OD03, uncertainty treatment OD04, resources OD12.
ACTIVATION_DEPENDENCIES: independently checked PIT/contract bindings, approved model calibration and data phase, reviewed implementation and separate evaluation permission; no orders/paper fills now.

## 10. OD11 — promotion, evidence and model complexity

Scientific requirements: distinguish observed mechanism, replayable information, conservative executable development, clean validation and independent replication. Source authenticity, logical identity and repeated model agreement are not economic performance.

MULTI_MODEL_CONSENSUS != INDEPENDENT_EVIDENCE  
AGREEMENT_BETWEEN_AI_SYSTEMS != ECONOMIC_AUTHORITY  
COMPOSITE_ECONOMIC_AUTHORITY = 0

Retain audit interpretation:
H4 = exact locked clean validation with corrected economic uncertainty, practical/risk/capacity and execution gates.
H5 = new forward shadow replication of presealed policy with valid attainable execution.
H6 = stronger regime/transport and joint Book/composite robustness.
H4 is candidate eligibility, not automatic nonzero weight. Audit floor H4 AND H5 plus separate governance is not weakened. H6 still does not grant live/capital authority. This mission authorizes no shadow validation to obtain any stage.

|Option|Promotion/evidence requirement|Harder/impossible; optionality/contamination and cost|
|---|---|---|
|A Preserve audit floor for future component shadow consideration|H4+H5 with all ratified operational gates and explicit governance; separately locked composite validation before joint policy authority|Least added evidence relative to audit, still blocked until remaining gates complete. No general robustness claim from one regime. Costs of clean validation and new replication remain; secondary success cannot waive primary|
|B Require H6 before any nonzero component shadow authority|Add preregistered regime/transport stress and robustness before eligibility for separate governance|Slower and more demanding; unavailable regimes may make timely promotion impossible. More capture/calendar/validation resources; no selecting favorable regime epochs after results|

Complexity choices within either evidence route, not automatic authorization:
- C1 Fixed minimal policy with no learned context router/interactions. Easier traceability; may be too restrictive to represent conditional effects. Lower parameter/calibration burden; preserves registry even if one package selected.
- C2 Small preregistered regularized/hierarchical model with justified fitted-parameter/context cap and locked priors/update law. Allows structured differences; degrees of freedom include context selection, hyperparameters, routing and hidden variants. Greater calibration and fresh-test burden; weak information may forbid even this model.

Neither cap nor model selected. Current fitted economic routing parameters and authority remain zero. The prior “20 effective blocks per parameter” was a design heuristic, not a power theorem, empirical result or owner-approved limit; no numeric cap is imported. Shrinkage can reduce noise but cannot create independent evidence or excuse multiplicity. Learned interactions/routing require explicit added complexity and validation of the complete law; no profit-maximizing black box designed.

Evidence ageing: preserve historical results; assess current applicability separately. Source/station/contract/fee/model-semantic change triggers binding/transport invalidation and review. Fixed expiry/review epochs versus prespecified drift-trigger suspension are possible future approaches; thresholds and half-lives unresolved. No exponential decay is fitted and no loss erased as stale. Monitoring that sees outcomes belongs to look/exposure accounting.

A composite is its own hypothesis/version/Book policy with component correlation, sizing/netting, cash/inventory, execution, update law and trial history. Individual success cannot certify joint behavior. New clean composite validation and separate governance required; no adaptive agreement score or consensus weights.

OWNER_DECISION_REQUIRED: floor versus stricter evidence, gate operational definitions, precision/error links, model/parameter/context/interaction constraints, ageing/expiry rules and exact selection/promotion rule. Dependency still unresolved; Probability-first is not argmax empirical p.

DESIGN_DEPENDENCIES: OD04 inference/information; OD05 variant/composite correction; OD10 conservative economics; remaining OD03 risk minima.
DECISION_DEPENDENCIES: OD06 achievable information/cap, OD07 epoch/stop, OD12 resources; all numerical complexity/promotion choices open.
ACTIVATION_DEPENDENCIES: clean exact-commit H4/H5(/H6) evidence and independent review plus distinct shadow/economic authority decision; no current promotion or weighting.

## 11. OD12 — resources and future phase authorization

Scientific/governance requirement: resources and permission are explicit, bounded and phase-specific. Selecting architecture, agreeing to a preference, funding documentation or passing audit does not authorize collection or experiments.

|Option|Resource arrangement|Harder/impossible; optionality/contamination and cost|
|---|---|---|
|A Documentation/recovery only|Budget/time for metadata, authority and exposure-history recovery plus conceptual schema; later phases separately scoped|Can frame contract but cannot solve unknown empirical power/fills/edge prevalence; no data acquisition. Lowest operational footprint; recovery that encounters outcome summaries must stop or log authorized development exposure|
|B Staged non-outcome operational feasibility|Separately approve conceptual architecture then bounded access/schema/contract feasibility work; return evidence and seek operational capture decision|Can resolve practical gaps without efficacy research, but protocol access could expose outcomes; constrain exact queries/projections. Extra stages/time but smaller early commitments; no automatic implementation/activation|
|C Preplanned staged resource envelope with independent permission gates|Owner reserves total ceilings/roles for potential design/build/capture/research phases, each locked behind a separate exact authorization event|Can plan continuity but reserve is not permission. Greater planning overhead; inability to provide independent custody/resources may block later phases. Unused reservation must not be converted to data/experiment authority|

No money/time/server/licensing limits are invented. Need owner operating budget, storage/retention, actor availability, credential/access rights, compute and calendar ceilings. Known directional burdens in prior tables are engineering consequences, not measured prices or promised turnaround.

|Distinct future phase|What later explicit authorization would need to say|Current status|
|---|---|---|
|Documentation/exposure recovery|Exact scope/resources; prohibit or separately log outcome-bearing materials|Only this decision-support document is authorized now|
|Generic architecture work|Conceptual schemas/roles versus implementation scope|No extra architecture mission launched|
|Operational capture design|Exact station/source/endpoint/universe/cadence/bindings, rights/budget, privacy/custody projections|Not selected/started|
|Builder|Exact implementation SHA/scope, required checks, deployment prohibition unless separately granted|BUILDER_AUTHORIZED = FALSE|
|Capture activation|Reviewed implementation/environment, approved capture manifest/roles/resources, explicit activation|Not authorized|
|DATA_T0|Owner-defined data epoch semantics and accountable timestamp, separate from activation or plan date|NOT_DECLARED|
|EXPERIMENT_T0 / freeze|Exact approved preregistered contract/SHA, clean surface/selection certificate and start semantics|NOT_DECLARED; freeze not authorized|
|E1–E5|Exact bounded outcome study and access/claim/stopping budget|Not authorized|
|Validation|Exact clean data/code/contract and independent analysis/release permission|Not authorized|
|Paper economics|Exact shadow Book/policy/execution/risk and authority; diagnostics are not confirmation by label|Not authorized|
|Unblinding|Named authority, exact output/date/recipients/manifest and release law|Not authorized|
|Live trading|Separate executable policy/governance/risk/environment authorization|LIVE_TRADING_AUTHORIZED = FALSE|
|Capital authorization|Separate capital amount/limits/custody and accountable decision|REAL_CAPITAL_AUTHORIZED = FALSE|

DATA_T0, EXPERIMENT_T0 and runtime activation are different events. A capture deployment can precede experiment lock only if separately authorized and with selection-specific cleanliness; it never backdates confirmatory evidence. No phase inferred from resolving OD04–OD11.

OWNER_DECISION_REQUIRED: option/resource ceilings, named roles, phase sequence and exact later authorization boundaries.
DESIGN_DEPENDENCIES: demands and unresolved feasibility from OD04–11; partial OD02/03 accounting constraints.
DECISION_DEPENDENCIES: all cost/actor/calendar/access choices; no ordinary negative forces owner to invent a strategy.
ACTIVATION_DEPENDENCIES: separate exact-phase approved artifact and independent prerequisites; this document cannot satisfy them.

## 12. Decision map and evidence firewall

|OD|Unresolved owner choice exposed|Main linked ODs|
|---|---|---|
|OD04|Blocking / joint model / partial identification; conditioning, overlap and valid inference|OD02/03, OD05/06/08/10/11|
|OD05|Finite FWER / sequential FWER / exploratory FDR; full claims, budgets/looks/recycling|OD04/06/07/09/11|
|OD06|Fixed deadline / information-targeted cap / staged feasibility; precision/tail/minimum/cap|OD03/04/05/07/08/10/12|
|OD07|Fixed / sequential / staged; futility/safety/continuation/failure/reopening|OD03/04/05/06/09/10/11|
|OD08|Broad sealed / narrow locked / separate streams; scope and operational fields|OD04/06/09/10/11/12|
|OD09|Independent custodian / isolated vault / declared shared-role restrictions; actors/access/release|OD04/05/07/08/12|
|OD10|Taker / uncertainty envelope / queue-evidenced maker; full Book endpoint/cost rules|OD02/03/04/08/11/12|
|OD11|Audit floor / H6-first; minimal / constrained regularized policy; promotion/complexity/ageing|OD03/04/05/06/07/10/12|
|OD12|Documentation / staged feasibility / reserved envelope with separate gates; resource/phase decisions|All unresolved decisions|

Every row is OWNER_DECISION_REQUIRED. All links awaiting a decision/evidence prerequisite are DEPENDENCY_UNRESOLVED. Choices may be ratified partially; unresolved numbers/actors/assumptions must remain explicit in a later integrated contract. An impossible inference/feasibility under approved resources must be reported, not “fixed” by lowering criteria or changing owner objective.

OUTCOME_BLIND_CHECK = PASS_DOCUMENT_SCOPE  
NEW_OUTCOMES_ACCESSED = NONE  
NEW_DATA_ACCESSED = NO_OBSERVATIONAL_OR_OUTCOME_DATA  
EXTERNAL_INFORMATION_ACCESSED = NONE

Only exact authority documents and Git commit/ref/tree metadata were accessed. Already verified prior support/plan content informs comparisons; no new market/weather history, city/model rankings, prevalence, performance, P&L, wallets, holdouts or latency advantage was examined. No external verification was necessary.
EMPIRICAL_COMPARISON_NOT_AUTHORIZED for option ranking/power/tails/opportunity/cost performance needing outcomes.
EXTERNAL_RESEARCH_BLOCKED_PENDING_CONTRACT_DECISION for information that could change belief about edge efficacy.
No tests of strategies, simulations, capture, implementation, optimization, paper economics or delegated research ran.

ECONOMIC_PROGRESS = exposed nine linked governance choices while preserving owner economic preference, 30d horizon and full hypothesis optionality before freeze.
REMAINING_BLOCKER = OD04–OD12 decisions, unfinished OD02/03 details and independent contract/cleanliness prerequisites.
EXIT_CONDITION = explicit owner ratification, then separate integrated contract and independent Astra audit; any phase still needs distinct authorization.
NEXT_SAFE_ACTION = owner review of this single package and an explicit owner decision artifact preserving unresolved dependencies; no integration or activation implied.
