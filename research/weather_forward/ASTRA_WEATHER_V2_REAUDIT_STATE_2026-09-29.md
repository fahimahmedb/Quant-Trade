# ASTRA — WEATHER FORWARD V2 RE-AUDIT STATE — updated 2026-10-01 (D4-C3-M1 recheck, cycle 1, fresh Astra context)

CURRENT STATE (supersedes the 2026-10-01 D4-C3 + transportability state below; prior file preserved verbatim under section H4)

AUDIT_ROLE = ASTRA independent adversarial reviewer (fresh context; did not write the repair or any earlier audit)
AUDIT_BRANCH = astra/weather-forward-v2-independent-reaudit-2026-09-29
AUDIT_ARTIFACT = research/weather_forward/ASTRA_WEATHER_V2_D4_C3_M1_RECHECK_2026-10-01.md
AUDIT_EVIDENCE = research/weather_forward/astra_d4_c3_m1_recheck_2026-10-01/ (independent synthetic engine + raw outputs)

AUDITED_BRANCH = claude/charming-allen-948kd8
AUDITED_SHA = 4423c5c3fe36c1d425b832ef87a9a774913377b4 (content commit 81929e4)
AUDITED_TREE = 82d0500ed7c91de7af7f9b3125c57d90199776bd
PREVIOUS_ASTRA_SHA = 5bb57eb2adf4cff35378f2c0e53e0316d45a4229
ASTRA_START_SHA = 0a088356b84f85f287e471503d4635293c5bd5ff

ASTRA_WEATHER_V2_D4_C3_M1_RECHECK = BLOCKED_D4_M1_SOURCE_BOUND_LEVEL_NOT_ATTAINED_OVER_DECLARED_CLASS_AND_FROZEN_SURFACE_UNDERCOVERAGE

M1_REPRODUCED_ON_OLD_RULE = TRUE (341e0b7a rule: size 0.0799 [0.0761, 0.0836]; miss 0.0916 [0.0876, 0.0956]; new rule same cells 0.0274 / 0.0333)
D4_M1_SOURCE_BOUND_CALIBRATION = BLOCKED (M1-R): holds on the exact run-G grid (worst 0.0471 [0.0457, 0.0484] at 100,000);
  fails over D_P as frozen ("CORE prices", pauses allowed): favourite CORE c~U(0.70,0.90), phi 0.9, rv 0.05, m 17 thin:
  size 0.0605 [0.0591, 0.0620], miss 0.0635 [0.0620, 0.0650] (100,000); rv 0.10: 0.0721 / 0.0852 [0.0813, 0.0891];
  30 paused dates 0.0531 [0.0517, 0.0544] (100,000); two-state regime with AR(0.9) autocorrelation 0.0526; literal spec-9
  30-date trailing-mean (boxcar) mechanism 0.0597 (outside AR class, but spec claims the level holds under that mechanism)
D4_INFORMATION_AND_UW_CALIBRATION = BLOCKED (M2): inside D_P (phi 0.9) T1a 0.0888, NEG 0.0707, U_W miss 0.0755 (joint; given
  reach 0.131 / 0.105 / 0.106) vs declared 0.025 / 0.025 / 0.05; nominal control still asserted in spec 6.1, 6.3 (FWER, IUT),
  8.4, 8.5, 9, 10.1, 10.3, 24 and in the 17.3 printed fields; qualified only in 17.8 / 8.1b / 21 / 27 / manifest ALPHA
D4_R1_REALIZED_WINDOW_BOUND = PASS (algebra / tail supremum; 8.5 byte-identical); core level part of M2
D4_R2_PROSPECTIVE_EXCLUSION_REMOVAL = PASS
D4_C3_UNCONDITIONAL_CONFIRMATION_REMOVAL = PASS
D4_R3_COST_MASS_TRANSPORT_BOUND = PASS (independent fuzz 59,600 laws, 0 identity / Theorem-2 violations; min N/C = -1 exactly)
D4_R3_ROBUSTNESS_FRONTIER = PASS (closed form vs brute force 0 mismatches; guard; monotone; k*(H) exact)
D4_R3_CLAIM_SEMANTICS = PASS for prospective / capital language (0 forbidden hits); level statements carried by M1-R / M2; m10, m11
D4_R3_STATE_MACHINE = PASS (4,608 combinations -> 11 values; shadow only from SUPPORTED and not CORE_ADVERSE)
D4_R3_POWER_CEILING_THEOREM = SUPPORTED (unchanged)
m8 = CLOSED
m9 = CLOSED
RAW_OUTPUT_REPRODUCTION = PASS (Architect script repro / c3 modes byte-identical to committed run-G output)
TRADING_RULE_CHANGED = FALSE
OUTCOME_LEAKAGE = NONE

CRITICAL_FINDINGS = NONE
MAJOR_FINDINGS =
M1-R: the 8.1b multi-block L_W attains joint miss / size <= 0.05 only on the simulated grid (c ~ U(0.35, 0.80), no pauses,
  Gaussian AR(1)), with ~0.3 pp margin; the frozen class text ("CORE prices", pauses permitted) is not covered: false
  REALIZED_WINDOW positive 0.0605 [0.0591, 0.0620] and L_W miss 0.0635 [0.0620, 0.0650] at a declared grid point with
  favourite-heavy CORE prices (100,000 reps), up to 0.0852 at phi 0.9 / rv 0.10; 30 paused dates 0.0531 [0.0517, 0.0544].
M2: T1a / NEG / U_W (frozen 5-date blocks) at 0.089 / 0.071 / 0.076 inside D_P vs 0.025 / 0.025 / 0.05 while 6.3 / 8.4 /
  8.5 / 9 / printed fields still assert nominal control; NEG drives R*_CORE_INFORMATION_REJECTED and vetoes the shadow signal.
MINOR_FINDINGS =
m10: stale "unchanged T2 / CR engine" (8.5c), unmarked delta D4-C3 size line, no section-2 decision row for D4-C3-M1,
  ambiguous "the level is lower"
m11: sentence (c) prints "95% sampling confidence" in reached runs without the joint-with-reach qualifier (given reach up to 0.138)
MISSING_PROOF = T1b (PINM) under cross-block persistence unmeasured; L_W level for CORE price mixes other than U(0.35, 0.80)
REPAIR_CLASS = REPAIRABLE_BOUNDED (calibrate over a completely stated class, or state the class and measured levels
  completely and propagate; same for T1a / NEG / U_W; governance authority needed to touch the frozen T1a / NEG / U_W tests)

D1_D12_SUMMARY =
D1 CLOSED (power shortfall of calibrated T2 disclosed)
D2 CLOSED
D3 CLOSED
D4 OPEN_MAJOR (C1, C2, C3 closed; M1 repaired on the grid only -> M1-R; M2 frozen-surface undercoverage)
D5 CLOSED
D6 CLOSED
D7 CLOSED
D8 CLOSED with disclosed limitation (T2 engine re-qualified by 8.1b; kappa / theta_core limitation now M2)
D9 CLOSED
D10 CLOSED_ACCEPTED_AND_DISCLOSED
D11 CLOSED
D12 CLOSED

EXPERIMENT_FEASIBILITY_V2 = BLOCKED_D4_M1_SOURCE_BOUND_LEVEL_NOT_ATTAINED_OVER_DECLARED_CLASS_AND_FROZEN_SURFACE_UNDERCOVERAGE
NEXT_AUTHORIZED_ACTION = BOUNDED ARCHITECT REPAIR ONLY
BUILDER_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED

---

## H4. History — state file as it stood at 0a088356 (verbatim)

# ASTRA — WEATHER FORWARD V2 RE-AUDIT STATE — updated 2026-10-01 (D4-C3 + transportability recheck)

CURRENT STATE (supersedes the 2026-09-30 D4-C2-recheck state below; all history preserved verbatim in section H3)

AUDIT_ROLE = ASTRA independent adversarial reviewer
AUDIT_BRANCH = astra/weather-forward-v2-independent-reaudit-2026-09-29
AUDIT_ARTIFACT = research/weather_forward/ASTRA_WEATHER_V2_D4_C3_TRANSPORT_RECHECK_2026-09-30.md
AUDIT_EVIDENCE = research/weather_forward/astra_d4_c3_recheck_2026-10-01/ (independent synthetic code + raw outputs)

AUDITED_BRANCH = claude/charming-allen-948kd8
AUDITED_SHA = 341e0b7aede716fdb68e2c9806cc1a09fdd50b82
AUDITED_TREE = 37412bdc3e0307ec3073f091552d6ab2d5332783
PREVIOUS_ASTRA_SHA = 92c2f706d2ac75af9ae9710061c60df520234410
ASTRA_START_SHA = 92c2f706d2ac75af9ae9710061c60df520234410
C3_REPRODUCED = TRUE (retired R2 label false 0.4324 [0.4255, 0.4393] thin / 0.1193 [0.1148, 0.1238] full; fresh seeds)

ASTRA_WEATHER_V2_D4_C3_TRANSPORT_RECHECK = BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE

D4_R1_REALIZED_WINDOW_BOUND = PASS (spec 8.5 byte-identical to e45d2ce7)
D4_R2_PROSPECTIVE_EXCLUSION_REMOVAL = PASS
D4_C3_UNCONDITIONAL_CONFIRMATION_REMOVAL = PASS (0 unconditional prospective labels / exclusions / R* rejections by construction)
D4_R3_COST_MASS_TRANSPORT_BOUND = PASS (exact for E[N]/E[C]; 99,239 fuzz cases 0 violations; worst N/C = -1 exactly;
  date- and trade-count epsilon fail on a one-cap-date counterexample, cost-mass epsilon is exact)
D4_R3_ROBUSTNESS_FRONTIER = PASS (closed form and monotonicity verified in domain; m8)
D4_R3_LW_CALIBRATION = BLOCKED (M1)
D4_R3_CLAIM_SEMANTICS = PASS (no unconditional future verdict; SHADOW_CONTINUATION_SIGNAL shadow-only; m9)
D4_R3_STATE_MACHINE = PASS (3,072 combinations -> 11 values, total, deterministic)
D4_R3_POWER_CEILING_THEOREM = SUPPORTED (finite-horizon wording; D_obs ~174 consistent; ceilings reproduced)

m3 = CLOSED
m4 = CLOSED
m5 = CLOSED
m6 = CLOSED
m7 = CLOSED

CRITICAL_FINDINGS = NONE
MAJOR_FINDINGS =
M1: L_W (T2's bound) is the only probability behind REALIZED_WINDOW_VALUE_* (claimed size <= 0.05) and every conditional
  prospective statement (claimed P(theta_W >= L_W) >= 0.95). Under the cross-block persistence that spec 9 itself names
  (30-date trailing-bias lag through seasonal transitions; latent var 0.05, daily AR phi 0.8), in 17-trades/date
  geometries passing the information floor 72-82% of the time, 20,000 reps each:
  false REALIZED_WINDOW positive claim at theta_W = 0: 0.0805 [0.0767, 0.0843];
  L_W miss: 0.0828 [0.0790, 0.0867] (thin), 0.0902 [0.0863, 0.0942] (full).
  Without persistence: 0.0524-0.0534 (the 0.5 pp R3 disclosed). R3 discloses only the 0.5 pp.
MINOR_FINDINGS =
m8: spec 17.3 ROBUSTNESS_FRONTIER and manifest ROBUST_BOUND / FRONTIER omit the 8.5c domain guard (L_W - delta > tau); prints
  epsilon* > 0 (e.g. 3) when L_W - delta < -1 and divides by zero at -1
m9: power table 4.6 reading 5 and delta D4-C2 "CLAIM STRENGTH AFTER REPAIR" still assert R2's refuted
  prospective-confirmation validity without a SUPERSEDED marker
MISSING_PROOF = NONE beyond M1
REGRESSIONS = NONE in D1-D3, D5-D12; trading rule unchanged; outcome leakage none
RUN_F_INTEGRITY = Architect modes frontier and c3 20000 re-run at 341e0b7a: byte-identical
INDEPENDENCE_DISCLOSURE = all repairs and rechecks in this chain ran in one agent session under different roles

D1_D12_SUMMARY =
D1 CLOSED
D2 CLOSED
D3 CLOSED
D4 OPEN_MAJOR (C1, C2, C3 closed; M1 open: source-bound calibration under cross-block persistence)
D5 CLOSED
D6 CLOSED
D7 CLOSED
D8 CLOSED (finite-cluster limitation carried; quantified more sharply by M1)
D9 CLOSED
D10 CLOSED_ACCEPTED_AND_DISCLOSED
D11 CLOSED
D12 CLOSED

PRIMARY_BLOCKER = D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE
MINIMAL_REPAIR_SURFACE = (a) calibrate L_W robustly to cross-block persistence (frozen outcome-blind rule, e.g. max CR
  variance over block lengths {5, 10, 20}; re-show coverage >= 0.95 over a declared persistence class; disclose the D1 / PCE
  power change) OR (b) weaken the stated level honestly (nominal 95% under the 5-date-block model; >= 0.90 under tested
  persistence) everywhere it appears; plus m8, m9. Keep the R3 transport algebra, vocabulary, shadow signal, R1, R2.
AFFECTED_FILES = spec 8.5c error statement (6.1 / 8.1 under a), 17.3, 17.8, 21; manifest ROBUST_BOUND / FRONTIER (ALPHA / NULLS
  under a); delta; power table 4.6 / 4.7; C3 simulation (persistence mode)
REQUIRED_REAUDIT_SURFACE = L_W coverage over the declared persistence class (>= 20,000 reps per cell); stated level everywhere; m8, m9

EXPERIMENT_FEASIBILITY_V2 = BLOCKED_D4_R3_SOURCE_BOUND_UNDERCOVERAGE_CROSS_BLOCK_PERSISTENCE
NEXT_AUTHORIZED_ACTION = BOUNDED ARCHITECT REPAIR ONLY
BUILDER_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED

## H3. HISTORY — superseded state of 2026-09-30 (D4-C2 recheck of e45d2ce7, commit 92c2f706), preserved verbatim

# ASTRA — WEATHER FORWARD V2 RE-AUDIT STATE — updated 2026-09-30 (D4-C2 recheck)

CURRENT STATE (supersedes the 2026-09-30 D4-recheck state below; all history preserved verbatim in section H2)

AUDIT_ROLE = ASTRA independent adversarial reviewer
AUDIT_BRANCH = astra/weather-forward-v2-independent-reaudit-2026-09-29
AUDIT_ARTIFACT = research/weather_forward/ASTRA_WEATHER_V2_D4_C2_RECHECK_2026-09-30.md
AUDIT_EVIDENCE = research/weather_forward/astra_d4_c2_recheck_2026-09-30/ (independent synthetic code + raw outputs)

AUDITED_BRANCH = claude/charming-allen-948kd8
AUDITED_SHA = e45d2ce7e2605a4136804d2c1b31efa3aa8120e1
AUDITED_TREE = 5d750291710f8261d55e96ae5c02e35146940bee
PREVIOUS_ASTRA_SHA = 3d18085862f239a81936345989b4e26414cedcf3
PREVIOUS_ARCHITECT_HEAD = 24d2342fcff8fd78a769a9ecaf7551ab2578e2ef

ASTRA_WEATHER_V2_D4_C2_RECHECK = BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION

D4_R1_REALIZED_WINDOW_BOUND = PASS (U_W formula identical to R1; proof correctly scoped to theta_W)
D4_C2_PROSPECTIVE_EXCLUSION_REMOVAL = PASS (C2 reproduced: retired rule false ERT exclusion 0.0415 S1 / 0.1785 p=0.5 /
  0.327 p=1 / 0.558 jackpot dates, false LARGE 0.1332 at theta_P=0.10, all from zero-count windows; R2: 0 prospective
  exclusions, 0 R* rejections, no alias; forward signal never from INDETERMINATE)
D4_PROSPECTIVE_CONFIRMATION = BLOCKED (C3 CRITICAL)
D4_STATE_MACHINE = PASS (exhaustive: 9,216 combinations -> 11 SCIENTIFIC values, total, deterministic; EXCLUDED unreachable)
D4_IDENTIFICATION_THEOREM = OVERSTATED (construction valid and reproduced; ceiling ~0.060 once pre-t0 resolved dates are
  counted, not 0.058; a finite-horizon power ceiling, not asymptotic non-identification; its confirmation-asymmetry
  corollary is false in general)

CRITICAL_FINDINGS =
C3: PROSPECTIVE_VALUE_CONFIRMED (and WEATHER_EDGE_FORWARD_SIGNAL) is issued with theta_P = -0.005 far above alpha = 0.05
  inside the admissible class R2 freezes for theta_P: rare date-level loss regimes (R* triggers on all 96 events at full
  S_ref, every leg loses) need only a 0.3-1% per-date rate and are missed by 120 dates 30-80% of the time. 20,000 reps each:
  0.4266 [0.4198, 0.4335] (m=17, thin ordinary fills); 0.2652; 0.1764; 0.1245 [0.1200, 0.1291] (full fills);
  0.0599 [0.0566, 0.0632] (LOWEST-template regime). Scan: 65/88 cells > 0.05. Mirror of R2's own theorem: any valid
  level-0.05 confirmation test has power <= 0.094 at theta=0.10 with 17 x 15 USD ordinary dates, T2 has ~0.43.
MAJOR_FINDINGS = NONE separate from C3
MISSING_PROOF = MP2: no frozen bridge assumption from the 120-date window to prospective theta_P for T2 (subsumed by C3)
MINOR = m3 manifest section C (R1 record) not marked superseded; m4 checkpoint section 4 still lists R1 rule 17.6 and the
  14-value partition as frozen decisions; m5 REALIZED_WINDOW_* wording could be misread prospectively (mitigated);
  m6 theorem D omits pre-t0 resolved dates; m7 "not identified" should read "no useful power within V2's horizon"
REGRESSIONS = NONE in D1-D3, D5-D12 (D10 still CLOSED_ACCEPTED_AND_DISCLOSED); trading rule, PCE / GO unchanged
RUN_E_INTEGRITY = Architect modes ceiling / confirm / counts / scenarios re-run at e45d2ce7: byte-identical to raw output
OUTCOME_LEAKAGE = NONE FOUND
INDEPENDENCE_DISCLOSURE = the D4 recheck, the R2 repair and this recheck ran in one agent session under different roles

D1_D12_SUMMARY =
D1 CLOSED
D2 CLOSED
D3 CLOSED
D4 OPEN_CRITICAL (C1 closed; C2 closed by R2; C3 open: prospective confirmation)
D5 CLOSED
D6 CLOSED
D7 CLOSED
D8 CLOSED
D9 CLOSED
D10 CLOSED_ACCEPTED_AND_DISCLOSED
D11 CLOSED
D12 CLOSED

PRIMARY_BLOCKER = D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION
EXACT_INVARIANT_TO_ADD = No label may claim theta_P > 0 (or any prospective positive value) at level alpha unless its size
  is <= alpha over the admissible class the protocol declares for theta_P; a narrower confirmation class must be frozen,
  named in the label and disclosed next to the exclusion class.
MINIMAL_REPAIR_SURFACE = confirmation side only: (a) frozen outcome-blind confirmation assumption + qualified label, or
  (b) distribution-free unsampled-loss allowance (downside mirror of M_tail, per-date capital cap 96 x S_ref, declared date
  independence), or (c) no prospective confirmation in V2; plus m3-m7. Keep the R2 exclusion removal and the R1 theta_W bound.
AFFECTED_FILES = spec 6.1 (T2), 6.3, 8.5b confirmation paragraph, 17.2 E1/E2, 17.5, 17.8, 21 item 27, 24, 27; manifest A rows
  NULLS / ALPHA / TERMINAL_STATE_MACHINE / FORWARD_SIGNAL_RULE, sections C and D; delta D4-C2; power table 4.6; resume
  checkpoint section 4; a synthetic confirmation-size run
REQUIRED_REAUDIT_SURFACE = prospective confirmation size over the declared class (96-event loss dates, thin ordinary depth,
  template- and station-comonotone regimes, m in {17, 35}); forward-signal rule; claim matrix 17.8; m3-m7

EXPERIMENT_FEASIBILITY_V2 = BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION
NEXT_AUTHORIZED_ACTION = BOUNDED ARCHITECT REPAIR ONLY
BUILDER_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED

## H2. HISTORY — superseded state of 2026-09-30 (D4 recheck of 24d2342, commit 3d18085), preserved verbatim

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
