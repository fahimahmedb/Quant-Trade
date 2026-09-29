# ASTRA — WEATHER FORWARD V2 INDEPENDENT RE-AUDIT — 2026-09-29

ASTRA_ROLE = independent adversarial scientific reviewer
MISSION_TYPE = INDEPENDENT ADVERSARIAL RE-AUDIT + SCIENTIFIC FEASIBILITY + PRE-REGISTRATION INTEGRITY
AUDITED_BRANCH = claude/charming-allen-948kd8
AUDITED_SHA = 94b59348d5b79cd3c53dcba0b791ce1daeb75d60
AUDITED_TREE = 044b3c43aade01ea72996a273c3176579b259471
AUDIT_BRANCH = astra/weather-forward-v2-independent-reaudit-2026-09-29
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED

## 1. Executive verdict

ASTRA_WEATHER_V2_REAUDIT = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION
EXPERIMENT_FEASIBILITY_V2 = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION
PRIMARY_BLOCKER = D4 structured upper bound can issue a materially false economic exclusion inside a pre-t0 GO region.
NEXT_AUTHORIZED_ACTION = BOUNDED ARCHITECT REPAIR ONLY

The V2 revision materially improves V1. D1, D2, D3, D5, D6, D7 and D8 are closed at the specification level, the ERT/PCE distinction is explicit, outcome-blind pre-t0 readiness is coherent, the scientific/operability separation is correct, and the terminal scientific partition is total.

V2 nevertheless fails the mission's most important pass/fail question. The structured upper bound is not merely conservative/model-dependent: under a plausible heterogeneous tail geometry that the frozen experiment cannot rule out, it under-covers and can emit NET_VALUE_EXCLUDED when true theta exceeds theta_ERT. The 14-date PCE GO/NO_GO screen does not structurally prevent that case.

This is CRITICAL under the mission severity rule because it can generate a materially false terminal economic claim.

## 2. Exact-candidate and immutability checks

The candidate branch was checked at the beginning and immediately before writing this audit. It resolved exactly to 94b59348d5b79cd3c53dcba0b791ce1daeb75d60 both times. No later candidate commit was audited.

Audited candidate tree: 044b3c43aade01ea72996a273c3176579b259471.

Authoritative predecessor immutability:

| Incorporated predecessor | Source commit | Source blob | Blob in V2 tree | Byte-identical |
|---|---|---:|---:|---|
| V1 FALSIFICATION_SPEC | 726070a199957a6fc05515ebb3027e945028fddc | f2db9b29731848779acc9e7e8e6fd72a8c14e18f | f2db9b29731848779acc9e7e8e6fd72a8c14e18f | TRUE |
| V1 FREEZE_MANIFEST | 726070a199957a6fc05515ebb3027e945028fddc | aad4a78ebc5d92d82e8dc74866c8e046bd9f5898 | aad4a78ebc5d92d82e8dc74866c8e046bd9f5898 | TRUE |
| V1 ARCHITECT_STATE | 726070a199957a6fc05515ebb3027e945028fddc | 434bea4134b6eae48b8fb4065e37340e769392b8 | 434bea4134b6eae48b8fb4065e37340e769392b8 | TRUE |
| Prior Astra review | e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250 | 29d4d1aaa9839c72c638348853b56f795e1d53fd | 29d4d1aaa9839c72c638348853b56f795e1d53fd | TRUE |
| Fable challenge | 5760ffa5b5da2a988cfe6d1503c86c561acf9b1f | 45d031f914fb5721ca772e31637edfb08104bac3 | 45d031f914fb5721ca772e31637edfb08104bac3 | TRUE |

No silent predecessor mutation was found.

## 3. Outcome-blindness

No resolved Weather winner, settlement outcome, historical hit rate, historical Weather P&L, wallet performance, leaderboard performance or post-signal outcome was used in this re-audit.

The numerical attacks below are synthetic and generated from declared prices, capital, dependence and hypothetical win probabilities. Current public mechanical metadata was used only to check protocol geometry. An independently retrieved current Polymarket Atlanta temperature page displayed exactly 11 outcomes, two tails and nine contiguous 2°F interior buckets, and the rule text stated whole-degree NOAA settlement. That independently supports the V2 °F interval treatment.

OUTCOME_INFORMATION_USED_BY_ASTRA = FALSE.

## 4. D1 reproduced from zero

For one-sided alpha = 0.05 and power 0.80, z_0.95 + z_0.80 = 2.4864749 and

N = ((2.4864749 * sigma_eff) / theta)^2.

Independent reproduction:

| theta | sigma=1.0 | sigma=2.0 | sigma=2.9 |
|---:|---:|---:|---:|
| 0.02 | 15,456 | 61,826 | 129,988 |
| 0.05 | 2,473 | 9,892 | 20,798 |
| 0.10 | 618 | 2,473 | 5,200 |

At 90% power, using z_0.95 + z_0.90 = 2.9264052:

| theta | sigma=1.0 | sigma=2.0 | sigma=2.9 |
|---:|---:|---:|---:|
| 0.02 | 21,410 | 85,639 | 180,055 |
| 0.05 | 3,426 | 13,702 | 28,809 |
| 0.10 | 856 | 3,426 | 7,202 |

The V2 planning DEFF formula DEFF(m)=1.5*(1+0.03*(m-1)) reproduces the 60/90/120-date table:

| Dates | m | raw N | DEFF | planning n_eff |
|---:|---:|---:|---:|---:|
| 60 | 17 | 1,020 | 2.22 | 459 |
| 60 | 35 | 2,100 | 3.03 | 693 |
| 60 | 55 | 3,300 | 3.93 | 840 |
| 90 | 17 | 1,530 | 2.22 | 689 |
| 90 | 35 | 3,150 | 3.03 | 1,040 |
| 90 | 55 | 4,950 | 3.93 | 1,260 |
| 120 | 17 | 2,040 | 2.22 | 919 |
| 120 | 35 | 4,200 | 3.03 | 1,386 |
| 120 | 55 | 6,600 | 3.93 | 1,679 |

The target-date ceiling n_eff <= D/rho_date is mathematically correct for an exchangeable within-date component. V2 correctly calls DEFF_PLAN an ASSUMED PLANNING VALUE rather than an estimate. It is not double-counted inside the final two-way CR inference; it is used for pre-t0 PCE planning, while final inference uses realised cluster residuals.

D1 conclusion: CLOSED. theta_ERT remains 0.02; theta_PCE is a confirmability threshold, not an economic redefinition; [ERT,PCE) remains explicitly unresolved.

## 5. PCE / GO attack

The frozen PCE mechanism itself is outcome-blind, total and deterministic. The problem is that 14 dates cannot guarantee that the future executable price geometry stays inside the tail family for which the exclusion bound has coverage.

I constructed a fixed 120-date synthetic design with:
- 35 trades/date = 4,200 trades;
- 48 stations with gamma-distributed activity;
- equal 50 USD capital per trade;
- 86 TAIL trades: 84 at c=0.039 and 2 at c=0.001;
- exactly 9 ordinary tail trades and zero 0.001 trades in the first 14 PRE_T0 dates;
- q = min(0.999,c+0.12), so the cheap legs satisfy the frozen R* hurdle without using outcomes;
- 5-date blocks and crossed date/station dependence.

The 14-date outcome-free readiness calculation gives:
- sigma0^2 = 1.32263;
- SE0_theta = 0.03089;
- theta_PCE = 0.08;
- SE0_kappa = 0.01296;
- 46 distinct traded stations;
- Kish-effective stations = 26.20.

Therefore the statistical GO criteria pass: PCE <= 0.10, SE0_kappa <= 0.020, stations >= 25, Kish >= 15. GLOBAL_READY is a separate mechanical precondition and can be assumed satisfied in this synthetic attack.

Over the full 120-date price mix, outcome-free price-implied SE0_theta becomes 0.03596. The ratio to the pre-t0 plan is 1.164, below the V2 PCE_DRIFT threshold of 1.5. Therefore the frozen drift flag does not protect this case.

This directly falsifies the defense that a dangerous tail mix necessarily produces PCE > 0.10 and therefore NO_GO.

## 6. Primary D4 attack — structured upper bound

### 6.1 Independent implementation

I did not use the Architect's bound implementation as evidence. I independently implemented the frozen construction.

For the tail, common-random-number uniforms were generated from the declared latent Gaussian copula rho_date=rho_station=rho_cell=0.10. Instead of reproducing the committed bisection code, I inverted the monotone count statistic by order statistics:

- for TPM, each draw/trade has threshold U_j/c_j; the (W+1)-th smallest threshold determines when the simulated count exceeds observed W;
- lambda_U is the 97.5% quantile of that threshold distribution, clipped to the frozen [0.05,1000];
- for SHR, the corresponding threshold is (U_j-c_j)/(q_j-c_j);
- mu_U is its 97.5% quantile, clipped to [0,50];
- U_tail is max(TPM,SHR);
- U_core is the frozen two-way max-of-one-way/two-way 97.5% CR upper bound;
- U(theta)=w_core U_core + w_tail U_tail.

100,000 declared-copula tail simulations were used to freeze the W -> U_tail lookup for the attack. The forward data-generating dependence was independently set to latent (0.05,0.05,0.10), not copied from the declared PINM values.

### 6.2 Hidden-tail / negative-core scenario

The decisive scenario is one of the mission's required geometries: positive tail / negative core.

Truth:
- CORE: p_j = 0.95 c_j, i.e. true core theta = -0.05;
- 84 ordinary TAIL legs at c=0.039 are fair, p=c;
- the two c=0.001 legs have p=0.170;
- no parameter was selected from outcomes;
- pooled true theta = +0.0315, which is above theta_ERT=0.02.

The two cheap legs are plausible R* trades because q≈0.121 gives ex-ante edge above h=0.10 while true p may differ from q. The protocol has no scientific mechanism that rules out an edge concentrated in those legs.

8,000 independent forward replications produced:

| Quantity | Estimate | MC SE | 95% MC interval |
|---|---:|---:|---:|
| nominal structured-bound coverage | 0.8854 | 0.00356 | [0.8784, 0.8924] |
| false U(theta) < theta_ERT | 0.0746 | 0.00294 | [0.0689, 0.0804] |
| U(theta) < frozen PCE=0.08 | 0.4230 | 0.00552 | [0.4122, 0.4338] |

The key line is false U(theta)<0.02 = 7.46% while true theta=3.15%. Under the V2 state machine, U<theta_ERT is evaluated first and produces ECONOMIC_RESULT=NET_VALUE_EXCLUDED. R*_REJECTED_AS_NET_STRATEGY then fires.

This is a false terminal economic exclusion, not merely a wide interval or loss of power.

### 6.3 Pure hidden-lottery check above PCE

A second scenario leaves the core fair and puts the hidden edge only in the same two c=0.001 legs, with p=0.18. True pooled theta = 0.08524, above frozen theta_PCE=0.08.

5,000 replications:
- structured-bound coverage = 0.8682; MC SE 0.00478; 95% MC interval [0.8588,0.8776];
- false LARGE_VALUE_EXCLUDED, U<0.08 = 0.1120; MC SE 0.00446; interval [0.1033,0.1207];
- false ERT exclusion = 0.0080.

Thus the PCE/LARGE_VALUE exclusion semantics also fail in a GO region.

### 6.4 Severity

CRITICAL.

Reason: the mission's severity rule defines CRITICAL as a defect that can generate a materially false scientific/economic terminal claim. The first scenario does exactly that. The label MODEL_CONDITIONAL_TAIL(TPM∨SHR) does not cure the problem because V2 uses the bound to drive NET_VALUE_EXCLUDED and R*_REJECTED_AS_NET_STRATEGY while the experiment cannot establish that true tail geometry lies in TPM∨SHR.

D4_STRUCTURED_BOUND = BLOCKED_FALSE_ECONOMIC_EXCLUSION

## 7. Error-control rechecks independent of Architect tables

### 7.1 Two-way CR T1a / T2 / NEG

Independent synthetic engine: Poisson/fixed ≈35 trades/date, gamma station activity, two-way 5-date-block × station max-of-three CR1, t reference with min(cluster counts)-1.

At the normal 120-date/48-station scale, 3,000 null replications under latent dependence (0.05,0.05,0.10):
- T1a nominal 0.025: 0.0287, MC 95% approximately [0.0227,0.0346];
- T2 nominal 0.05: 0.0537, [0.0456,0.0617];
- NEG frozen 0.025: 0.0230, [0.0176,0.0284].

At the minimum truncated information geometry, 60 dates / 25 stations / 12 blocks:
- TRUE dependence: T1a 0.0297; T2 0.0497; NEG 0.0250;
- strong-station dependence (0.02,0.15,0.10): T1a 0.0310; T2 0.0497; NEG 0.0273;
- stress (0.15,0.15,0.10): T1a 0.0323; T2 0.0573; NEG 0.0247.

T1a is mildly liberal relative to its nominal 0.025 component level, but the deviations are much smaller than the D4 bound failure and do not establish a separate CRITICAL terminal defect.

### 7.2 T1 union

A separate fixed-design null simulation precomputed the T1b critical win count under the declared PINM copula and then simulated T1a and T1b jointly under independent truth draws.

GO-compatible 2% tail share with c_tail=0.039, 5,000 replications:
- TRUE dependence: T1a=0.0296, T1b=0.0202, T1 union=0.0482;
- stress dependence: T1a=0.0256, T1b=0.0244, T1 union=0.0482.

A 5% log-uniform tail mix outside the typical PCE GO region reached union 0.0596 under stress. This is a limitation of the component calibration, but the tested GO-compatible configuration stayed at the declared familywise 0.05.

Special verdicts:
- D4_T1_ERROR_CONTROL = PASS
- D4_T2_ERROR_CONTROL = PASS
- D4_TAIL_PINM = PASS

These PASS labels do not repair D4_STRUCTURED_BOUND.

## 8. Committed simulation evidence is not exact frozen-protocol evidence

The full committed WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py source was inspected.

The frozen spec/manifest requires:
- lambda in [0.05,1000];
- mu in [0,50];
- 40 bisection iterations.

The committed simulation code instead uses:
- lambda upper bound 200;
- mu upper bound 20;
- 30 bisection iterations.

Run B also uses NEG_ALPHA=0.05 and relies on a separate Run C for the frozen 0.025 NEG check.

Therefore the committed simulation table is not an exact executable reproduction of the frozen V2 procedure. This is recorded as MISSING_PROOF, not as the primary blocker, because the independent attack above implements the frozen ranges directly and already produces a stronger validity failure.

The audit environment exposed repository text through the GitHub connector but not an executable repository checkout. The committed script was therefore source-inspected rather than invoked directly; all verdict-changing tests were independently reimplemented with different seeds and algorithms.

MISSING_PROOF_MP1 = COMMITTED_SIMULATION_NOT_EXACT_FROZEN_BOUND

## 9. State-machine exhaustion

I independently enumerated the ordered scientific logic over all Boolean combinations of:
- validity valid/invalid;
- INFO_SUFFICIENT;
- T1;
- NEG;
- U<ERT;
- T2;
- theta_hat>=ERT;
- GATES.

Exactly 14 SCIENTIFIC_STATE values are reachable:
- NOT_EVALUATED;
- INFORMATION_INSUFFICIENT;
- 3 INFORMATION_RESULT values × 4 ECONOMIC_RESULT values.

No combination maps to zero or multiple scientific states because each sub-axis is ordered with an otherwise row.

Precedence is coherent:
- INVALID pre-empts science;
- INFORMATION_INSUFFICIENT never becomes NO_EDGE;
- operability is orthogonal and cannot erase science;
- PRE_T0 NO_GO is a design result, not Weather failure;
- mechanics change truncates or invalidates by frozen timing rather than economic direction.

D2 = CLOSED.

## 10. D3 / D5 / D6 / D7 / D8 focused checks

D3 — CLOSED. V2 correctly gates on captured_at in the entry window, treats exchange_book_timestamp as last-change metadata, rejects only future timestamps beyond tolerance, and places no lower bound on quiet books. Missing, malformed, clock and provenance cases are deterministic.

D5 — CLOSED. SCIENTIFIC_STATE and OPERABILITY_STATE are orthogonal. science-positive/inaccessible, science-negative/inaccessible and science-indeterminate/accessible all retain their scientific result.

D6 — CLOSED. W=30 is explicitly 30 PRIOR USABLE RESOLVED dates, not calendar days. A date is usable only if the archived vintage exists and the final outcome was available before the later decision's T_entry. The current target date cannot enter its own bias. PRE_T0 decision rows are forbidden from joining settlement/PNL for experiment evaluation.

D7 — CLOSED. The four regexes, integer-set representation and half-degree continuous boundaries completely determine °C and 2°F arithmetic, including tails. A live/current public Polymarket US temperature example independently confirmed the expected 11-outcome / nine 2°F interior / two-tail shape and whole-degree NOAA rule. Adding °F materially expands the cohort, but V2 explicitly records COHORT_CHANGED=TRUE and re-freezes the domain; the mathematical R* rule itself is unchanged.

D8 — CLOSED with finite-cluster limitation carried. Crossed 5-date-block × ICAO clustering is primary; date-only is never fallback; max(V_block,V_station,V_2w) handles non-PSD finite-sample cases. Independent 60-date/25-station stress simulations did not show gross T2 size failure, although T1a is mildly liberal.

## 11. D9–D12

D9 = CLOSED. n>=1000 is no longer a scientific feasibility criterion; dates, blocks, stations, Kish, SE and DEFF define the information floor.

D10 = CLOSED_ACCEPTED_AND_DISCLOSED. NO_DATA_LOWEST / fallback can still enter the frozen bias estimator, but V2 flags BIAS_CONTAMINATED and does not claim pure NWP attribution from that fact. This can affect what strategy is being tested, but it does not invalidate prospective theta economics when reported honestly.

D11 = CLOSED. Structural/readiness ineligibility is excluded from the venue-deterioration denominator; fee/tick/template/unit/source/API changes have deterministic reason codes and truncation behavior.

D12 = CLOSED. T_entry order is causal; same-instant ties use a neutral deterministic hash; tier results are explicitly CAPACITY_CONSTRAINED_SUBSAMPLE and retain regional-composition reporting.

## 12. Required D1–D12 verdict table

| Defect | Verdict | Severity if non-closed | Failure mode / reproduction / minimal repair |
|---|---|---|---|
| D1 power / ERT-PCE | CLOSED | — | ERT and PCE separated; D1 arithmetic reproduced |
| D2 state machine | CLOSED | — | 14-state scientific partition exhaustively enumerated |
| D3 book timestamp | CLOSED | — | captured_at observation contract deterministic |
| D4 heavy-tail inference | OPEN | CRITICAL | structured bound can false-exclude true theta>ERT at 7.46% in GO-region hidden-tail scenario; replace exclusion semantics/bound |
| D5 science vs operability | CLOSED | — | orthogonal axes |
| D6 readiness | CLOSED | — | 30 prior usable resolved dates + PRE_T0 isolation |
| D7 °F geometry | CLOSED | — | exact interval arithmetic; live geometry sample matches |
| D8 crossed dependence | CLOSED | — | two-way primary; finite-cluster limitation carried |
| D9 1,000-trade illusion | CLOSED | — | retired |
| D10 bias contamination | CLOSED | — | accepted/disclosed/flagged |
| D11 mechanics | CLOSED | — | baseline/reason codes/truncation deterministic |
| D12 tier selection | CLOSED | — | deterministic causal allocation + subsample label |

For D4:
SEVERITY = CRITICAL
FAILURE_MODE = model-conditioned tail upper bound drives unconditional-looking economic exclusion outside the tail model class
REPRODUCTION = sections 5-6 above
MINIMAL_REPAIR = section 15 below

## 13. Claim matrix

| Claim | Estimand | Test / bound | Alpha | Power target | Inference | Dependence | Min information | Confirm? | Exclude? | Model-conditional? | Limitation |
|---|---|---|---:|---|---|---|---|---|---|---|---|
| INFORMATION_FAVOURABLE_CORE | kappa_core | T1a | 0.025 | design SE target | two-way CR | block×station | IF1-IF5 | YES | adverse handled by NEG | NO | mild finite-cluster liberalism |
| INFORMATION_FAVOURABLE_TAIL | lambda_tail / W_tail | T1b | 0.025 | scenario-dependent | PINM count | declared copula | IF floor + tail trades | YES | NO | YES | exact only under copula |
| NEGATIVE_INFORMATION | kappa_core | upper 97.5% <0 | 0.025 | high at material negative kappa | two-way CR | block×station | IF1-IF5 | adverse YES | n/a | NO | label refers core information, not theta |
| THETA_POSITIVE | theta | T2 | 0.05 | 0.80 at PCE nominal | two-way CR | block×station | IF1-IF5 | YES | NO | NO | not powered at ERT |
| THETA_ERT_EXCLUDED | theta | U(theta)<0.02 | 0.05 nominal | not separately powered | structured core+tail | CR + PINM | IF1-IF5 | n/a | YES | YES tail | INVALID under hidden-tail geometry |
| LARGE_EDGE_EXCLUDED | theta | U(theta)<PCE | 0.05 nominal | n/a | structured core+tail | CR + PINM | IF1-IF5 | n/a | YES | YES tail | INVALID under hidden-tail geometry |
| NET_VALUE_CONFIRMED | theta | T2 + theta_hat>=ERT + G1-G3 | 0.05 test | 0.80 at PCE | two-way CR + robustness | crossed | IF1-IF5 | YES | NO | NO for T2 | robustness gates reduce power |
| NET_VALUE_NOT_ROBUST | theta | T2 but gate failure | 0.05 test | as above | two-way CR | crossed | IF1-IF5 | qualified | NO | NO | not a deployment claim |
| INFORMATION_INSUFFICIENT | n/a | IF1-IF5 fail | n/a | n/a | reliability gate | n/a | explicit | NO | NO | NO | non-result |

The failing rows are the structured-bound exclusion claims.

## 14. V1 -> V2 delta integrity

The material changes named in the mission are disclosed in the delta/manifest:
- °F cohort expansion;
- core/tail stratification;
- ERT/PCE split and ceiling;
- parallel information/economic axes;
- structured bound;
- tick-aware conservative slippage;
- two-way clustering;
- readiness and observation phase;
- one final analysis time;
- total state machine;
- tier hash tie-break;
- attribution demotion.

No material V2 semantic change identified in the audited files was hidden only in prose outside the delta.

TRADING_RULE_CHANGED=FALSE is defensible only in the narrow functional sense: the R* mapping is unchanged. The eligible application domain is materially expanded, but V2 separately and correctly declares COHORT_CHANGED=TRUE and re-freezes before t0.

## 15. Smallest repair surface

PRIMARY_BLOCKER = D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION

AFFECTED_FILES:
1. research/weather_forward/WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md
2. research/weather_forward/WEATHER_FORWARD_FREEZE_MANIFEST_V2_2026-09-29.md
3. research/weather_forward/WEATHER_FORWARD_V2_POWER_TABLE_2026-09-29.md
4. research/weather_forward/WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py
5. research/weather_forward/WEATHER_FORWARD_V1_TO_V2_DELTA_2026-09-29.md if semantics change

EXACT_INVARIANT_TO_CHANGE:
No ECONOMIC_RESULT=NET_VALUE_EXCLUDED, ECONOMIC_BOUND=RELEVANT_VALUE_EXCLUDED or LARGE_VALUE_EXCLUDED may be emitted from a tail model whose declared 95% upper-bound coverage is not guaranteed over the frozen admissible tail outcome class.

Bounded repair options:
A. simplest: if any economically material TAIL exposure exists, structured U may be reported diagnostically but cannot drive E1 or the PCE/LARGE exclusion fields; those states remain INDETERMINATE unless a valid broader upper bound excludes the threshold;
or
B. replace TPM∨SHR by an upper-bound procedure with demonstrated >=95% coverage over a pre-declared tail class broad enough to include heterogeneous hidden-lottery and positive-tail/negative-core geometries, then independently validate it on fresh Monte Carlo seeds.

Do not change R*, theta, h, sizing, t0 logic, D1 architecture, or the already-closed D2/D3/D5/D6/D7/D8 surfaces unless the repair necessarily touches them.

REQUIRED_REAUDIT_SURFACE:
- revised D4 bound and proof;
- state-machine exclusion rows E1 / ECONOMIC_BOUND;
- claim matrix;
- PCE/GO interaction with tail drift;
- exact committed simulation implementation;
- fresh independent coverage / false-exclusion Monte Carlo.

## 16. Final status

D4_STRUCTURED_BOUND = BLOCKED_FALSE_ECONOMIC_EXCLUSION
D4_T1_ERROR_CONTROL = PASS
D4_T2_ERROR_CONTROL = PASS
D4_TAIL_PINM = PASS

CRITICAL_FINDINGS:
- C1: structured tail bound can false-exclude true theta>ERT and cause R*_REJECTED_AS_NET_STRATEGY in a pre-t0 GO region.

MAJOR_FINDINGS:
- NONE separate from C1.

MISSING_PROOF:
- MP1: committed synthetic simulation script is not an exact implementation of the frozen structured-bound ranges/iteration counts.

ASTRA_WEATHER_V2_REAUDIT = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION
EXPERIMENT_FEASIBILITY_V2 = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION
NEXT_AUTHORIZED_ACTION = BOUNDED ARCHITECT REPAIR ONLY
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED
