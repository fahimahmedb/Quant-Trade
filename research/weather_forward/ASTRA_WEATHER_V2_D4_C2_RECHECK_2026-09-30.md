# ASTRA — WEATHER FORWARD V2 — BOUNDED D4-C2 RECHECK — 2026-09-30

```text
ASTRA_ROLE              = independent adversarial scientific reviewer (bounded D4-C2 recheck only)
AUDIT_BRANCH            = astra/weather-forward-v2-independent-reaudit-2026-09-29
AUDITED_BRANCH          = claude/charming-allen-948kd8
AUDITED_SHA             = e45d2ce7e2605a4136804d2c1b31efa3aa8120e1
AUDITED_TREE            = 5d750291710f8261d55e96ae5c02e35146940bee
R2_CONTENT_COMMIT       = 4845d32 (e45d2ce = resume-checkpoint commit on top)
PREVIOUS_ARCHITECT_HEAD = 24d2342fcff8fd78a769a9ecaf7551ab2578e2ef
PREVIOUS_ASTRA_SHA      = 3d18085862f239a81936345989b4e26414cedcf3
ASTRA_WEATHER_V2_D4_C2_RECHECK = BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0                      = NOT_DECLARED
BUILDER_AUTHORIZED      = FALSE
```

## 0. Independence disclosure

The Astra D4 recheck @3d18085, the Architect R2 repair @e45d2ce7 and this recheck were produced in the same agent session under different role instructions. The Architect's own state file discloses this. To limit self-confirmation:
- this recheck uses a separate engine (`astra_d4_c2_recheck_2026-09-30/`) with fresh seeds (990 000 – 996 500);
- it aims most of its compute at the one surface the Architect declared safe without an adversarial search: prospective confirmation.

Governance may still prefer a separate reviewer session.

## 1. Executive verdict

R2 does what it claims on the exclusion side:
- C2 reproduces, and under R2 it is structurally dead: 0 prospective exclusions and 0 R* rejections in every attack, with no alias that can do either (§3–§5).
- The R1 bound survives correctly as a θ_W report field.
- The 11-value partition is total.

R2 fails the mission's P1 question. R2 makes **PROSPECTIVE_VALUE_CONFIRMED** the only economic claim V2 can issue, and spec §8.5b / §17.8 assert that it is valid for θ_P at size ≤ 0.05 because "bounded downside makes an unsampled type that could overturn a confirmation visible". That argument silently assumes an unsampled loss regime carries no more capital per date than an ordinary date.

The frozen admissible class, the same class R2 uses to prove exclusion non-identified, allows otherwise:
- up to 96 triggered events per date at full S_ref depth;
- date common modes;
- `p ∈ [0,1]`.

A rare loss regime (a date on which R* triggers on every event and every leg loses) can therefore carry several times an ordinary date's capital. It then needs a per-date rate of only 0.3–1%, which a 120-date window misses 30–80% of the time. Fresh independent Monte Carlo at θ_P = −0.005, i.e. strictly inside the confirmation null, 20,000 replications each:

| Loss-regime geometry (frozen admissible class) | False PROSPECTIVE_VALUE_CONFIRMED (joint; MC SE; 95% MC) |
|---|---|
| 17 trades/date, ordinary fills 5–25 USD, loss dates = 96 events at 50 USD, θ_core = 0.10 | **0.4266** (0.0035) [0.4198, 0.4335] |
| same, θ_core = 0.05 | **0.2652** (0.0031) [0.2591, 0.2714] |
| 35 trades/date, thin ordinary fills, 96-event loss dates, θ_core = 0.08 | **0.1764** (0.0027) [0.1711, 0.1816] |
| 17 trades/date, **full** 50 USD fills everywhere, 96-event loss dates, θ_core = 0.05 | **0.1245** (0.0023) [0.1200, 0.1291] |
| 17 trades/date, full fills, loss regime = every LOWEST leg of a date (48), θ_core = 0.04 | **0.0599** (0.0017) [0.0566, 0.0632] |

`WEATHER_EDGE_FORWARD_SIGNAL` fires at the same rates (these runs have CORE_ADVERSE = FALSE). This is a false positive prospective economic claim plus a promotion path, inside the frozen class, well above the declared α = 0.05. By the mission's §14 and §36 rules it is **CRITICAL**.

Most of the T2 machinery predates R2. What R2 did was make confirmation the load-bearing economic claim and write the unsupported validity statements into the spec, so the blocker sits on the D4 surface under review.

## 2. Authority verification

| Check | Result |
|---|---|
| `origin/claude/charming-allen-948kd8` | `e45d2ce7e2605a4136804d2c1b31efa3aa8120e1`: MATCH (checked at start and before writing) |
| Audited tree | `5d750291710f8261d55e96ae5c02e35146940bee` |
| Ancestry | 94b59348, 7d95c00 and 24d2342 are all ancestors; R2 = 4845d32 → e45d2ce, fast-forward, no rewrite |
| `QUANT_NORTH_STAR.md` | blob 8295041a…, unchanged |
| Astra files in candidate | `ASTRA_WEATHER_V2_INDEPENDENT_REAUDIT` 957d28e7… and `ASTRA_WEATHER_V2_REAUDIT_STATE` 7e6dec3e…, byte-identical to 7d95c00; the 3d18085 recheck is not merged into the candidate (correct) |
| Diff 24d2342 → e45d2ce7 | 8 files, all under `research/weather_forward/` |

## 3. C2 reproduced (independent engine `astra_c2r2.py`, seeds 991 000+, 4,000 replications each)

A fresh prospective realisation per replication: 14 OP dates + 120 window dates, Poisson(35) trades/date, 48 gamma(2) stations. Counting is the protocol's own path: GO ∧ INFO_SUFFICIENT ∧ label ∧ θ_P ≥ threshold.

| Attack | θ_P | Retired R1: false ERT exclusion (joint, 95% MC) | Retired R1: false LARGE exclusion | **R2: prospective exclusions / R* rejections** | R2 label distribution |
|---|---|---|---|---|---|
| S1: 0.001 legs, p = 0.17, core −0.05 | 0.025 | 0.0415 [0.0353, 0.0477] | 0.0665 | **0 / 0** | INDETERMINATE 0.49, CONFIRMED 0.0003, rest not reached |
| p = 0.5, core −0.10 | 0.025 | 0.1785 [0.1666, 0.1904] | 0.1875 | **0 / 0** | INDETERMINATE 0.52 |
| p = 1.0, core −0.10 | 0.025 | 0.3270 [0.3125, 0.3415] | 0.3450 | **0 / 0** | INDETERMINATE 0.57 |
| PCE: p = 0.5, core 0 | 0.10 | 0.0262 | **0.1332** (false LARGE) | **0 / 0** | INDETERMINATE 0.53, CONFIRMED 0.025 (true) |
| jackpot dates (96 legs, p = 1), core −0.10 | 0.025 | 0.5580 [0.5426, 0.5734] | 0.5875 | **0 / 0** | INDETERMINATE 0.59 |

The mechanism reproduces:
- S1 is lower than Astra's earlier 0.0592 because here the OP dates are separate from the window. The Architect's run E found 0.0475.
- The stronger cases reproduce clearly.
- By observed count, every retired-rule false exclusion occurs with **0** observed sub-cent legs: 0.27 / 0.50 / 0.53 / 0.06 / 0.56 of those windows. With ≥ 1 observed leg the rate is 0.
- R2 issues no prospective exclusion at any count (0, 1, 2, …, 10). In the zero-count windows the realised-window bound is often negative (REALIZED_WINDOW_LOSS_CONFIRMED 0.01–0.51 joint), correctly scoped to θ_W, while ECONOMIC_RESULT stays PROSPECTIVE_VALUE_INDETERMINATE.

## 4. Exclusion removal: no alias survives (P0)

The semantic audit of every economic-sounding field at e45d2ce7 (spec §17.2–17.8, manifest A rows, power table §4.6 / §5, delta D4-C2, architect state, checkpoint) found:

| Field | Can it say "prospective R* lacks relevant value"? |
|---|---|
| ECONOMIC_RESULT | No. Values are CONFIRMED / NOT_ROBUST / INDETERMINATE only; the EXCLUDED row is deleted (enumeration §6) |
| R*_REJECTED_AS_NET_STRATEGY | No. It is never issued; printed as NOT_IDENTIFIED_IN_V2 (spec 17.6, manifest REJECTION_RULE (D4-R2)) |
| PROSPECTIVE_EXCLUSION | No. It is a constant NOT_IDENTIFIED_IN_V2 |
| REALIZED_WINDOW_BOUND (LOSS_CONFIRMED / RELEVANT / LARGE / NOT_EXCLUDED) | No. The estimand is explicitly θ_W; it is report-only; no rule reads it; mandatory sentence (b) and claim matrix 17.8 forbid prospective reading |
| R*_CORE_INFORMATION_REJECTED / CORE_ADVERSE | No. It is information-level (κ_core via NEG at 0.025) and cannot change ECONOMIC_RESULT (enumeration §6). It can block the forward signal, which is a deliberate tightening, not a verdict |
| WEATHER_EDGE_FORWARD_SIGNAL | No. It requires PROSPECTIVE_VALUE_CONFIRMED; INDETERMINATE never promotes |

Stale, non-reachable text (MINOR, Builder-visible):
- **m3.** Manifest section C (the R1 record) still lists "Economic rejection | only via `U(θ) < θ_ERT`" and "14-value SCIENTIFIC partition … forward-signal rule unchanged" without a SUPERSEDED marker. Section A (D4-R2 rows) and section D contradict it.
- **m4.** Resume checkpoint §4 items 1, 3 and 5 still state the R1 rule 17.6 and the 14-value partition as "do not re-derive" decisions (§3b below them adds R2).

Neither changes a frozen A-row. A Builder reading only section C could implement the retired rule, so both should be marked superseded.

**D4_C2_PROSPECTIVE_EXCLUSION_REMOVAL = PASS.**

## 5. θ_W vs θ_P and the R1 bound (P2)

- The U_W formula at e45d2ce7 is identical to R1: `w_core (θ̂_core + t_{df,0.975} SE_CR) + M_tail`, `M_tail = Σ_TAIL (n_j − C_j)/Σ_all C_j`. Its proof is now explicitly conditional on the realised trade set and labelled θ_W.
- My C2 engine's θ_W coverage and the Architect's run E (coverage 0.9705–1.0 per scenario) agree. Earlier Astra evidence carries over: 240,000 adversarial replications with no domination violation.
- θ_W is defined in spec §5.1 as the expected value of the executed window trades, not realised P&L.

Remaining semantic tension (MINOR m5): the label words "LOSS_CONFIRMED" and "VALUE_EXCLUDED" could be read prospectively by a non-specialist. The REALIZED_WINDOW_ prefix, sentence (b) and matrix 17.8 mitigate this adequately.

**D4_R1_REALIZED_WINDOW_BOUND = PASS.**

## 6. State machine (P3; `enumerate_states.py`, exhaustive)

- Scope: 9,216 admissible combinations of VALIDITY (8) × INFO_SUFFICIENT × T1 × NEG × T2 × θ̂ ≥ θ_ERT × GATES × U_W bands × OPERABILITY (6), under the R1 invariant U_W ≥ θ̂.
- Result: exactly **11** SCIENTIFIC_STATE values, with each combination mapping to exactly one. No EXCLUDED value is reachable.
- The forward signal is reachable only from `{INFORMATION_DETECTED, NO_INFORMATION_DETECTED}__PROSPECTIVE_VALUE_CONFIRMED` with CORE_ADVERSE = FALSE.
- Flipping U_W or CORE_ADVERSE never changes ECONOMIC_RESULT. R*_REJECTED_AS_NET_STRATEGY is never TRUE.
- NOT_ROBUST (T2 ∧ θ̂ ≥ θ_ERT ∧ ¬GATES) and INDETERMINATE are distinct.
- Case check: `CORE_ADVERSE = TRUE` with θ_P positive through the tail gives INFORMATION_DETECTED (T1b) or NEGATIVE_INFORMATION × PROSPECTIVE_VALUE_*, R*_CORE_INFORMATION_REJECTED = TRUE, and forward signal FALSE. This is consistent and intended.
- No table still expects 14 values apart from m3 / m4.

**D4_STATE_MACHINE = PASS.** The partition is valid; the blocker concerns what one of its labels may truthfully claim, not totality.

## 7. PRIMARY FINDING C3 (CRITICAL): prospective confirmation is not valid under the frozen admissible class (P1)

### 7.1 What T2 tests

T2 (spec §6.1, §8.1) is the two-way CR one-sided t-test of `θ̂ = ΣN/ΣC` against 0 at α = 0.05, over the 120 window dates with 5-date blocks × ICAO clusters.
- As a statement about θ_P it needs a bridge: the window's date clusters must be representative independent draws from the prospective executed-trade process, and the CR t-reference must be adequate for their distribution.
- R2 does not freeze any such bridge. §8.5b instead asserts that confirmation has "no structural non-identification", and §17.8 lists "size ≤ 0.05" against θ_P.
- For exclusion, the same §8.5b declares the admissible class to be "any dependence, including date / regime common modes" with p ∈ [0, 1]. Confirmation is thus implicitly judged under a narrower, undeclared class than exclusion (mission §18).

### 7.2 Why "bounded downside" is not enough

A loss regime lowers θ_P by its **capital share** times (1 + θ), not by its date frequency. The Architect's catastrophe check held the trade count on loss dates equal to ordinary dates (η = θ_0/(1+θ_0) per date).

The frozen mechanics allow loss dates to carry the maximum 96 events × S_ref, while ordinary dates carry `m̄ · C̄`. The per-date rate needed to pull θ_P to 0 is then

```text
η = θ_0 A / (θ_0 A + B),   A = m̄ C̄ (ordinary date capital),  B = 96 × 50 (maximum date capital)
```

which is 0.3–1% per date in realistic geometries. The window then contains no loss date with probability `(1 − η)^120` ≈ 0.3–0.8.

### 7.3 Mirror of the Architect's own theorem

Apply the §8.5b construction to confirmation, with loss dates in place of jackpot dates. For any level-α test of `θ_P ≤ 0`, power at θ_0 is at most `α (1 − η)^(−120)`.

| Ordinary date capital (trades × avg fill) | θ_0 = 0.02 | 0.05 | 0.10 |
|---|---|---|---|
| 17 × 15 USD | 0.057 | 0.069 | 0.094 |
| 35 × 15 USD | 0.065 | 0.096 | 0.184 |
| 17 × 50 USD | 0.076 | 0.144 | 0.411 |
| 35 × 50 USD | 0.120 | 0.437 | 1.0 |

T2 has far more power than these ceilings in the thin-capital rows (for example ≈ 0.43 against a ceiling of 0.094). **It therefore cannot be a valid level-0.05 test of θ_P over the frozen class**, and the Monte Carlo in §1 confirms it directly.

The asymmetry the Architect relied on is real only when ordinary dates already carry capital comparable to the maximum date capital (35 × 50 row).

### 7.4 Monte Carlo evidence

Engine: `run_confirm_attack.py` scan, 88 cells × 2,000 replications, then `run_confirm_refine.py` at 20,000 replications per cell in 5 seed chunks. All cells use θ_P ≤ 0: θ_P = 0 exactly for the scan and −0.005 for the refinement, computed analytically. The protocol path is simulated in full:
- OP GO;
- INFO_SUFFICIENT IF2–IF5;
- T2;
- θ̂ ≥ θ_ERT;
- G1 (CONSERVATIVE one tick) and G2 (top-5, date and station concentration); G3 true.

Refinement (θ_P = −0.005):

| Cell | η per date | False CONFIRMED | 95% MC | Given reachable state | Forward signal |
|---|---|---|---|---|---|
| 96-event loss dates, m = 17, thin fills, θ_core = 0.10 | 0.0056 | **0.4266** | [0.4198, 0.4335] | 0.84 | 0.4266 |
| same, θ_core = 0.05 | 0.0029 | **0.2652** | [0.2591, 0.2714] | — | 0.2652 |
| 96-event, m = 35, thin, θ_core = 0.08 | 0.0093 | **0.1764** | [0.1711, 0.1816] | — | 0.1764 |
| 96-event, m = 17, full fills, θ_core = 0.05 | 0.0097 | **0.1245** | [0.1200, 0.1291] | — | 0.1245 |
| LOWEST-template (48), m = 17, full, θ_core = 0.04 | 0.0158 | **0.0599** | [0.0566, 0.0632] | — | 0.0599 |
| 96-event, m = 35, full, θ_core = 0.03 | 0.0127 | 0.0387 | [0.0360, 0.0414] | — | 0.0387 |
| Architect-type (loss dates = ordinary count), m = 17, θ_core = 0.04 | 0.0433 | 0.0424 | [0.0396, 0.0452] | — | 0.0424 |
| Architect-type, m = 35, θ_core = 0.02 | 0.0245 | 0.0259 | [0.0237, 0.0280] | — | 0.0259 |

In the 88-cell scan (2,000 replications each), 65 cells had a point estimate above 0.05, and 53 had their whole 95% MC interval above 0.05. These include the station-comonotone variant (0.11 at m = 17). The Architect's own confirm rows reproduce bit-for-bit (§9). They sit in the safe corner (equal capital on loss dates, m = 35).

### 7.5 Classification

**CRITICAL.** This is a false prospective economic claim, "R*'s prospective net value is positive", at 0.06–0.43 against the declared 0.05. It occurs inside the admissible class that R2 freezes for θ_P. It also opens the forward-signal promotion path that mission §31 requires to be impossible ("the cost should be failure to reject bad candidates, not false authorization"). No capital path exists (§11), but a paper/shadow promotion proposal is a hidden economic verdict built on a false claim.

**D4_PROSPECTIVE_CONFIRMATION = BLOCKED.**

## 8. Identification theorem (P4)

The reconstruction holds:
- The jackpot-date alternative Q is admissible under the declared class (0.001 asks, `p = 1`, independent date common mode, same capital).
- The algebra `θ_P(Q) = (1 − η) θ_0 + η (1/c_min − 1)` is exact.
- The coupling on "no jackpot date" gives `P_P(φ) ≤ α (1 − η*)^(−D)`.
- c_min = 0.00104995 and 1/c_min − 1 = 951.43. The ceiling table reproduces exactly: `ceiling` mode output is identical to the raw output.

Two overstatements (MINOR, non-blocking for exclusion, since R2 is safe simply because exclusion is disabled):
- **m6 (numeric).** D = 134 omits resolved pre-t0 dates that V2 observes: BIAS_HISTORY (≥ 30 usable resolved dates, span ≤ 40) and the GR3 parser history (≥ 30 dates). With D ≈ 174 the ceiling at θ_0 = −1 is 0.0602 (ERT) and 0.0611 (0.10). "≤ 0.058" should read "≈ 0.06".
- **m7 (wording).** The result is a finite-horizon power ceiling, not non-identification in the asymptotic sense; the bound grows without limit in D. The spec half-acknowledges this ("D · η* ≫ 1"), but the constant is named `PROSPECTIVE_EXCLUSION_IDENTIFIABLE = FALSE`. Precise wording: "not identifiable with useful power within V2's observable horizon".

R2-A rejection check (mission §9): a distribution-free arrival bound without IID, Poisson, stationarity or known clustering is not available. With arbitrary dependence the zero-count window is compatible with any arrival mass, and the theorem makes this rigorous. The minimality claim for the exclusion side is therefore correct.

The mirror result in §7.3 is the missing half: the same class makes low-to-moderate prospective confirmation essentially unidentifiable when ordinary date capital is small relative to the 96 × S_ref date cap.

**D4_IDENTIFICATION_THEOREM = OVERSTATED** (valid construction; numeric and wording overstated; its asymmetry corollary for confirmation is false in general).

## 9. Simulation and raw-output integrity (Architect run E)

At e45d2ce7 I re-ran `WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py` in modes `ceiling` (55 rows), `confirm 4000` (4), `counts 4000` (4) and `scenarios 4000` (13). All outputs are **byte-for-byte identical** to the committed `WEATHER_FORWARD_V2_D4_C2_RUN_E_OUTPUT_2026-09-30.jsonl` rows. That includes the renamed scenario (the rename is label-only; seeds are index-based). The grid (1,002 rows) was not re-run.

The script is synthetic only and reads no files or network. Seeds are documented. I found no selective reporting: every row of every mode is in the raw file.

## 10. Other checks

- **Trading rule and PCE / GO.** Spec §3, §5.2, §8.1–8.4, §9, §10.1–10.2, §11.1 / 11.3 / 11.4, §12, §14, §15, §16, §17.1, §17.4, §18, §19, §22 and §23 are byte-identical to 24d2342. §10.3 changed only in its descriptive drift note, which correctly says PCE / GO is not an arrival-sufficiency check. θ_ERT, the PCE formula, PCE_CEILING, the 14-date OP and GO / NO_GO are unchanged. TRADING_RULE_CHANGED = FALSE is confirmed.
- **Outcome leakage.** None. R2 is synthetic plus algebra, and no Weather outcome, wallet or P&L data was used here.
- **Builder authority.** BUILDER_AUTHORIZED = FALSE in the spec header, spec §27, manifest header, architect state and checkpoint. No sentence implies that Builder may start.
- **North Star (mission §32).** INDETERMINATE is never favourable, and no capital path reads INDETERMINATE or REALIZED_WINDOW. Capital requires governance beyond the forward signal: "TRUE authorises nothing beyond proposing a further paper/shadow phase". The only promotion hole is C3 (false CONFIRMED).

## 11. Claim matrix (reconstructed at e45d2ce7; Astra assessment)

| Label | Estimand | Null | Test | α | Assumptions actually needed | Proves | Does not prove | Rejects R*? | Builder? | Capital? |
|---|---|---|---|---|---|---|---|---|---|---|
| PROSPECTIVE_VALUE_CONFIRMED | θ_P | θ_P ≤ 0 | T2 + θ̂ ≥ θ_ERT + G1–G3 | claimed 0.05; **actual up to 0.43** | undeclared: no unsampled date-level loss regime whose capital share exceeds what 120 dates reveal | (C3) only θ_W > 0 under CR asymptotics | θ_P > 0 over the frozen class | no | no (proposal only) | no |
| PROSPECTIVE_VALUE_NOT_ROBUST | θ_P | as above | T2 + θ̂ ≥ θ_ERT, gate fails | as above | as above | as above | as above | no | no | no |
| PROSPECTIVE_VALUE_INDETERMINATE | θ_P | — | — | — | none | nothing | "no edge" | no | no | no |
| PROSPECTIVE_EXCLUSION = NOT_IDENTIFIED_IN_V2 | θ_P | — | ceiling theorem | — | declared class | exclusion is powerless (≈ 0.06 ceiling) | — | no | no | no |
| REALIZED_WINDOW_BOUND | θ_W | θ_W ≥ threshold | U_W | declared 95% (core 0.975 nominal) | CR adequacy for the core | window trades' expected value below threshold | anything about θ_P | no | no | no |
| CORE_ADVERSE / R*_CORE_INFORMATION_REJECTED | κ_core | κ_core ≥ 0 | NEG CR | 0.025 | CR adequacy | core legs overpriced net of costs | tail, θ_W, θ_P | no (information-level) | no | no |
| INFORMATION_DETECTED (T1a ∪ T1b) | κ_core, λ_tail | both nulls | CR ∪ PINM | 0.05 | PINM copula for T1b | chosen legs underpriced | net value | no | no | no |
| OPERABILITY_STATE | depth, ρ_30, mechanics, access | — | 17.4 | descriptive | — | accessibility | science | no | no | no |

## 12. Regression scan (D1–D3, D5–D12, only for R2-caused changes)

| Item | Regression |
|---|---|
| D1 | NONE |
| D2 | NONE: the partition was re-derived (11 values, total); m3 / m4 are stale records only |
| D3 | NONE |
| D5 | NONE |
| D6 | NONE |
| D7 | NONE |
| D8 | NONE |
| D9 | NONE |
| D10 | NONE (still CLOSED_ACCEPTED_AND_DISCLOSED) |
| D11 | NONE |
| D12 | NONE |

C3 is not a regression of a closed item. It is a validity defect in the D4 surface's only remaining economic claim, exposed by R2's reliance on it and by R2's own admissible class.

## 13. Final self-attack (mission §43)

1. θ_P > θ_ERT and R2 rejects R*: **no**.
2. Any prospective LARGE_VALUE_EXCLUDED: **no**.
3. θ_P ≤ 0 with an omitted rare catastrophe produces PROSPECTIVE_VALUE_CONFIRMED: **yes, at up to 0.43 (C3)**.
4. T2 infers θ_P only under an undeclared bridge assumption. Without it, it infers the window mean.
5. Assumptions for prospective confirmation frozen: **no**.
6. θ_W report-only: yes (m5 minor).
7. REALIZED_WINDOW_LOSS_CONFIRMED influences rejection: no.
8. CORE_ADVERSE a hidden net-value rejection: no.
9. INDETERMINATE treated as favourable: no.
10. An indeterminate strategy reaches Builder or capital: no. A *falsely confirmed* one reaches a forward-signal proposal (C3).
11. R*_REJECTED_AS_NET_STRATEGY unreachable: yes.
12. Trading rule changed: no.
13. Real outcomes used: no.
14. 11-state partition total: yes.
15. Builder can implement mechanically: yes for the states. However, the claim a Builder would print (CONFIRMED ⇒ θ_P > 0 at 5%) is false in the class.

## 14. Minimal repair surface (bounded Architect repair only)

PRIMARY_BLOCKER: `D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION`

EXACT_INVARIANT_TO_ADD: no label may claim θ_P > 0 (or any prospective positive value) at level α unless its size is ≤ α over the admissible class the protocol declares for θ_P. If a narrower class is used for confirmation, it must be frozen, named in the label and disclosed alongside the exclusion class.

Options (Architect's choice; listed, not designed):
- **(a)** Freeze an explicit, outcome-blind confirmation assumption (for example a declared cap on the capital share of date-level regimes absent from 120 dates, or cross-date stationarity with bounded per-date capital relative to the window mean) and qualify the label accordingly. Re-show size ≤ α at the frozen boundary.
- **(b)** Add a distribution-free unsampled-loss allowance to confirmation, the mirror of R1's M_tail on the downside. Require the CR lower bound on θ to exceed the maximum θ_P reduction from loss regimes that 120 dates could miss with probability ≥ α, using the frozen per-date capital cap (96 × S_ref, or the observed window maximum if frozen as such) and date independence (to be declared). Show size ≤ α over the class, and accept the power cost that §7.3 quantifies.
- **(c)** Conclude that prospective confirmation is also unavailable at the scales V2 can reach, and restrict positive claims to θ_W or the information axis. Governance-level consequence: V2 could then never propose a forward signal on economic grounds.

AFFECTED_FILES: spec §6.1 T2 row, §6.3, §8.5b "Prospective confirmation" paragraph, §17.2 E1 / E2 conditions, §17.5, §17.8, §21 item 27, §24, §27; manifest A rows NULLS / ALPHA / TERMINAL_STATE_MACHINE / FORWARD_SIGNAL_RULE and section D; delta D4-C2 claim strength; power table §4.6 (confirmation rows); a synthetic confirmation-size run over the loss-regime class above. Also fix m3 (manifest section C superseded marker), m4 (checkpoint §4), m6 / m7 (theorem numeric and wording).

DO NOT CHANGE: R*, h, W, cohort, strata, S_ref sizing, execution, T1a / T1b / NEG, dependence, PCE / GO, the R2 exclusion removal, or the R1 θ_W bound.

REQUIRED_REAUDIT_SURFACE: prospective confirmation size over the declared class (including 96-event loss dates, thin ordinary depth, template- and station-comonotone regimes, m ∈ {17, 35}); the forward-signal rule; claim matrix 17.8; m3–m7.

## 15. Verdict

```text
ASTRA_WEATHER_V2_D4_C2_RECHECK        = BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION
D4_R1_REALIZED_WINDOW_BOUND           = PASS
D4_C2_PROSPECTIVE_EXCLUSION_REMOVAL   = PASS   (C2 reproduced; 0 prospective exclusions / 0 R* rejections; no alias)
D4_PROSPECTIVE_CONFIRMATION           = BLOCKED (C3 CRITICAL: false CONFIRMED at θ_P = −0.005 up to 0.4266 [0.4198, 0.4335];
                                                 0.1245 with full fills; forward signal at the same rates)
D4_STATE_MACHINE                      = PASS   (11 values, total, deterministic; EXCLUDED unreachable)
D4_IDENTIFICATION_THEOREM             = OVERSTATED (construction valid; ≈ 0.06 with pre-t0 resolved dates; finite-horizon
                                                    power ceiling, not asymptotic non-identification; confirmation corollary false)
REGRESSIONS                           = NONE in D1–D3, D5–D12
CRITICAL_FINDINGS                     = C3
MAJOR_FINDINGS                        = NONE separate from C3
MINOR                                 = m3 manifest §C stale, m4 checkpoint §4 stale, m5 REALIZED_WINDOW wording, m6 theorem D, m7 theorem wording
MISSING_PROOF                         = MP2: no frozen bridge assumption from window to θ_P for T2 (subsumed by C3)
EXPERIMENT_FEASIBILITY_V2             = BLOCKED_D4_PROSPECTIVE_CONFIRMATION_UNSAMPLED_LOSS_REGIME_FALSE_CONFIRMATION
NEXT_AUTHORIZED_ACTION                = BOUNDED ARCHITECT REPAIR ONLY (section 14)
BUILDER_AUTHORIZED                    = FALSE
REAL_CAPITAL_AUTHORIZED               = FALSE
LIVE_TRADING_AUTHORIZED               = FALSE
t0                                    = NOT_DECLARED
```
