# ASTRA — WEATHER FORWARD V2 RE-AUDIT STATE — updated 2026-09-30 (D4 recheck)

CURRENT STATE (supersedes the 2026-09-29 D4 state below; history preserved verbatim in section H)

AUDIT_ROLE = ASTRA independent adversarial reviewer
AUDIT_BRANCH = astra/weather-forward-v2-independent-reaudit-2026-09-29
AUDIT_ARTIFACT = research/weather_forward/ASTRA_WEATHER_V2_D4_RECHECK_2026-09-30.md
AUDIT_EVIDENCE = research/weather_forward/astra_d4_recheck_2026-09-30/ (independent synthetic code + raw outputs)

AUDITED_BRANCH = claude/charming-allen-948kd8
AUDITED_SHA = 24d2342fcff8fd78a769a9ecaf7551ab2578e2ef
AUDITED_TREE = 5ebe96e59b104318fbcc3b837583a43c20976171
D4_REPAIR_COMMIT = 05836143a249f5571a29403727c6d90df2c8b7c8
PREVIOUS_ASTRA_SHA = 7d95c00abccfbc805c0d8abca65a6b93268741a2
PREVIOUS_AUDITED_SHA = 94b59348d5b79cd3c53dcba0b791ce1daeb75d60

D4_RECHECK_STATUS = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION
ASTRA_WEATHER_V2_D4_RECHECK = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION

D4_STRUCTURED_BOUND = VALID_FOR_REALISED_WINDOW_ESTIMAND_ONLY; INVALID_FOR_FROZEN_PROSPECTIVE_THETA (spec 5.1)
  - R1 exclusion bound U = w_core U_core + M_tail deterministically dominates every tail outcome conditional on the realised
    trade set (proved; 99,310 deterministic + 240,000 adversarial MC checks, zero violations).
  - C2 CRITICAL: spec 5.1 freezes prospective theta = E[N]/E[C]; M_tail bounds only sampled tail legs. Rare sub-cent legs
    absent from a GO-compatible window -> U < theta_ERT while prospective theta > theta_ERT.
D4_CORE_COVERAGE = DEFENSIBLE: cov_core 0.946-0.992 over 24 adversarial geometries (nominal 0.975); protocol false-claim rate
  at theta_true in {0.02, 0.021, 0.025, 0.03} <= 0.044 incl. 60/25 minimum geometry; regime dependence beyond 5-date blocks
  under-covers (~0.88) but IF5 holds its false-claim rate <= 0.010 (carried D8 limitation)
D4_FALSE_EXCLUSION = C1 reproduced (A1 false ERT exclusion 0.0774 [0.0715, 0.0832], coverage 0.882) and closed by R1 (A1/A2 0);
  C2 new: prospective theta = 0.025, p_tail = 0.17 at c = 0.001: false NET_VALUE_EXCLUDED 0.0592 [0.0519, 0.0666];
  p_tail 0.5-1.0: 0.19-0.35; false LARGE_VALUE_EXCLUDED 0.153 at prospective theta = 0.10; GO passes 82-94%
D4_RSTAR_SEMANTICS = RULE CORRECT (R*_REJECTED_AS_NET_STRATEGY iff NET_VALUE_EXCLUDED; NEGATIVE_INFORMATION ->
  R*_CORE_INFORMATION_REJECTED, information-only); inherits C2 through E1; MINOR m2: T1-via-tail + NEG cell issues no
  core-information rejection and 17.5 does not refuse the forward signal, contrary to the new 17.6 prose
MP1_STATUS = CLOSED (lambda [0.05,1000], mu [0,50], 40 iterations, B = 20,000, frozen seed/draw order in committed sim)
REGRESSIONS = NONE in D1-D3, D5-D12, T1a/T1b/T2/NEG, PINM (T1b only), 14-value partition, trading rule;
  MINOR m1: spec 24 still says "model-conditional upper bound"
OBSERVATIONS = O1 IF5 (DEFF <= 6) fails ~37% at 120/48 under TRUE dependence (feasibility risk, not D4);
  O2 cross-block regime dependence (carried D8)
OUTCOME_LEAKAGE = NONE FOUND
TRADING_RULE_CHANGED = FALSE (confirmed)

D1_D12_SUMMARY =
D1 CLOSED
D2 CLOSED
D3 CLOSED
D4 OPEN_CRITICAL (C1 closed for the realised trade set; C2 open)
D5 CLOSED
D6 CLOSED
D7 CLOSED
D8 CLOSED (finite-cluster / block-length limitation carried)
D9 CLOSED
D10 CLOSED_ACCEPTED_AND_DISCLOSED
D11 CLOSED
D12 CLOSED

PRIMARY_BLOCKER = D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION
EXACT_INVARIANT_TO_ADD = An exclusion label may assert only the estimand its bound covers: either the exclusion estimand is
  explicitly the realised-window theta_W, or the bound must cover prospective theta over the full admissible class,
  including tail leg types whose arrival rate the window cannot resolve.
SMALLEST_REPAIR = R2-a (recommended): freeze theta_W as the E1 / ECONOMIC_BOUND estimand; rename/qualify E1, ECONOMIC_BOUND and
  17.6 (no prospective "R* rejected as a net strategy" claim); mandatory sentence that prospective theta incl. unsampled
  tail leg types is not excluded; add C2 attack to sim + power table. Alternatives R2-b (prospective Poisson tail allowance,
  exclusion practically unreachable) / R2-c (declared p/c cap; not recommended).
AFFECTED_FILES = spec 5.1, 8.5, 17.2, 17.3, 17.6, 17.7, 24, 27; manifest A5 EXCLUSION_UPPER_BOUND / REJECTION_RULE + C;
  delta D4.f; power table 4.5; synthetic sim
REQUIRED_RECHECK_SURFACE = E1 / ECONOMIC_BOUND / 17.6 estimand and labels; fresh prospective-estimand MC (S1-S9 class); claim matrix

EXPERIMENT_FEASIBILITY_V2 = BLOCKED_D4_PROSPECTIVE_ESTIMAND_UNSAMPLED_TAIL_FALSE_EXCLUSION
NEXT_AUTHORIZED_ACTION = BOUNDED ARCHITECT REPAIR ONLY
BUILDER_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED

## H. HISTORY — superseded state of 2026-09-29 (Astra re-audit of V2@94b59348, commit 7d95c00), preserved verbatim

# ASTRA — WEATHER FORWARD V2 RE-AUDIT STATE — 2026-09-29

AUDIT_ROLE = ASTRA independent adversarial reviewer
AUDIT_BRANCH = astra/weather-forward-v2-independent-reaudit-2026-09-29

AUDITED_BRANCH = claude/charming-allen-948kd8
AUDITED_SHA = 94b59348d5b79cd3c53dcba0b791ce1daeb75d60
AUDITED_TREE = 044b3c43aade01ea72996a273c3176579b259471

STATUS = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION
ASTRA_WEATHER_V2_REAUDIT = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION
EXPERIMENT_FEASIBILITY_V2 = BLOCKED_D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION

D1_D12_SUMMARY =
D1 CLOSED
D2 CLOSED
D3 CLOSED
D4 OPEN_CRITICAL
D5 CLOSED
D6 CLOSED
D7 CLOSED
D8 CLOSED
D9 CLOSED
D10 CLOSED_ACCEPTED_AND_DISCLOSED
D11 CLOSED
D12 CLOSED

D4_STRUCTURED_BOUND = BLOCKED_FALSE_ECONOMIC_EXCLUSION
D4_T1_ERROR_CONTROL = PASS
D4_T2_ERROR_CONTROL = PASS
D4_TAIL_PINM = PASS

CRITICAL_FINDINGS =
C1: In an outcome-blind pre-t0 GO-compatible synthetic design, the frozen model-conditional structured bound can issue U(theta)<theta_ERT while true pooled theta>theta_ERT. Independent positive-tail/negative-core attack: true theta=0.0315, 8,000 replications, false NET_VALUE_EXCLUDED=0.0746, MC 95% interval [0.0689,0.0804], structured-bound coverage=0.8854 [0.8784,0.8924]. The result then triggers R*_REJECTED_AS_NET_STRATEGY.

MAJOR_FINDINGS =
NONE separate from the primary CRITICAL D4 defect.

MISSING_PROOF =
MP1: WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py is not an exact implementation of the frozen structured-bound numerical contract. Frozen: lambda upper=1000, mu upper=50, 40 bisection iterations. Committed script: lambda upper=200, mu upper=20, 30 iterations.

PRIMARY_BLOCKER = D4_STRUCTURED_BOUND_FALSE_ECONOMIC_EXCLUSION

AFFECTED_FILES =
research/weather_forward/WEATHER_FORWARD_FALSIFICATION_SPEC_V2_2026-09-29.md
research/weather_forward/WEATHER_FORWARD_FREEZE_MANIFEST_V2_2026-09-29.md
research/weather_forward/WEATHER_FORWARD_V2_POWER_TABLE_2026-09-29.md
research/weather_forward/WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py
research/weather_forward/WEATHER_FORWARD_V1_TO_V2_DELTA_2026-09-29.md if exclusion semantics change

EXACT_INVARIANT_TO_CHANGE =
No economic exclusion state or report field may be driven by a tail upper bound unless its declared coverage is valid over the frozen admissible tail outcome class. If that coverage is unavailable, tail-bearing runs remain economically INDETERMINATE for exclusion while confirmatory T2 and information-axis results may still be reported.

REQUIRED_REAUDIT_SURFACE =
D4 bound construction and coverage
E1 NET_VALUE_EXCLUDED
ECONOMIC_BOUND ERT/PCE exclusion fields
PCE/GO interaction with tail-price drift
claim matrix
exact simulation implementation
fresh independent false-exclusion Monte Carlo

NEXT_AUTHORIZED_ACTION = BOUNDED ARCHITECT REPAIR ONLY

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED
