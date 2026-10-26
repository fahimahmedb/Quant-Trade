# ASTRA — WEATHER FORWARD V2 — BOUNDED D4-C3-M1 RECHECK — 2026-10-01

```text
ASTRA_ROLE              = independent adversarial scientific reviewer (fresh context; bounded D4-C3-M1 recheck)
AUDIT_BRANCH            = astra/weather-forward-v2-independent-reaudit-2026-09-29
ASTRA_START_SHA         = 0a088356b84f85f287e471503d4635293c5bd5ff
PREVIOUS_ASTRA_SHA      = 5bb57eb2adf4cff35378f2c0e53e0316d45a4229
AUDITED_BRANCH          = claude/charming-allen-948kd8
AUDITED_SHA             = 4423c5c3fe36c1d425b832ef87a9a774913377b4   (content commit 81929e4)
AUDITED_TREE            = 82d0500ed7c91de7af7f9b3125c57d90199776bd
ASTRA_WEATHER_V2_D4_C3_M1_RECHECK = BLOCKED_D4_M1_SOURCE_BOUND_LEVEL_NOT_ATTAINED_OVER_DECLARED_CLASS_AND_FROZEN_SURFACE_UNDERCOVERAGE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
t0                      = NOT_DECLARED
BUILDER_AUTHORIZED      = FALSE
```

## 1. Authority

| Check | Result |
|---|---|
| `origin/claude/charming-allen-948kd8` after fetch | `4423c5c3fe36c1d425b832ef87a9a774913377b4`: MATCH. Re-verified at resume and before commit |
| Ancestors | 341e0b7a, e45d2ce7, 24d2342f and 94b59348 are ancestors: OK |
| Audited tree | `82d0500ed7c91de7af7f9b3125c57d90199776bd` |
| Astra start | local = remote = `0a088356`: MATCH |
| Files changed 341e0b7a → 4423c5c3 | spec, manifest, delta, power table, architect state, checkpoint, new run-G script and raw output only |
| `QUANT_NORTH_STAR.md` | unchanged since 94b59348 |
| Astra / Fable artifacts in the candidate | unchanged |
| Prior Astra artifacts on the Astra branch | unchanged since 5bb57eb2; only the orchestrator ledger changed after it |
| Prior simulation scripts and outputs (runs D, E, F) | unchanged |
| Spec section byte comparison (`out_spec_section_diff.txt`) | Identical: §2–§5.3, §6.3, §8, §8.1–§8.5b, §8.6, §8.7, §9–§10.2, §11–§17.2, §17.4–§17.7, §18–§20, §22, §23, §25. Changed: header, §1, §6.1, §6.2, §7, new §8.1b, §8.5c, §10.3, §17.3, §17.8, §21, §24, §26, §27 |

- **Trading rule unchanged.** §3, §5.2, §14 and §15 are byte-identical. So are R1 §8.5 (U_W) and §9 (dependence).
- **§8.5c.** The only changes are Theorem 2's L_W definition sentence and the new error statement. The R3 statement is kept under a SUPERSEDED heading.
- **Outcome information:** none was used, by the candidate or by this audit.

## 2. Independence disclosure

- This is a fresh Astra context. I wrote neither the D4-C3-M1 repair nor any earlier audit.
- The orchestrator ledger notes that the R3 audit @5bb57eb2 came from the same context that authored R3. I therefore re-verified the R3 surfaces independently (§8).
- All simulation uses my own engine (`astra_m1_engine.py`), written from the spec text, with fresh seeds `SeedSequence([77100101, plan, cell, chunk])`.
- The Architect's script was only re-run, to check that its committed output reproduces (§9).
- `test_engine.py` checks that my two-way CR equals a direct trade-level implementation. On one random window it also matches the Architect's `cr2w`; that is a numerics check only.
- A session interruption stopped the class run after 105 of 156 cells. Cells 105–155 were re-run with the same per-cell seeds, so the result equals a single run.

## 3. Reproduction: M1 old rule vs new rule (`out_repro_20k.jsonl`)

Design: 120 + 14 dates, 48 stations, latent copula (0.05, 0.05, 0.10) plus a daily AR(1) date regime. Each cell uses N = 20,000 replications, and both rules are evaluated on the same replications. Rates are joint with reach (GO ∧ INFO_SUFFICIENT).

| Cell | Reach | OLD 341e0b7a: estimate (MC SE) [95% MC] | NEW 4423c5c3 §8.1b: estimate (MC SE) [95% MC] | Astra @5bb57eb2 |
|---|---|---|---|---|
| False window positive: φ 0.8, rv 0.05, m 17 thin, θ_W = 0 | 0.716 | **0.0799** (0.0019) [0.0761, 0.0836] | **0.0274** (0.0012) [0.0251, 0.0297] | 0.0805 |
| L_W miss: φ 0.8, rv 0.05, m 17 full, θ 0.10 | 0.825 | **0.0916** (0.0020) [0.0876, 0.0956] | **0.0333** (0.0013) [0.0308, 0.0358] | 0.0902 |
| L_W miss: φ 0.8, rv 0.05, m 17 thin, θ 0.05 | 0.768 | 0.0849 (0.0020) [0.0810, 0.0888] | 0.0273 (0.0012) [0.0250, 0.0296] | 0.0828 |
| L_W miss: φ 0.9, rv 0.10, m 17 thin, θ 0.05 | 0.318 | 0.0833 (0.0020) [0.0794, 0.0871] | 0.0377 (0.0014) [0.0350, 0.0403] | 0.0866 |
| False positive: φ 0.9, rv 0.10, m 17 thin, θ_W = 0 | 0.268 | 0.0723 (0.0018) [0.0687, 0.0758] | 0.0338 (0.0013) [0.0313, 0.0363] | 0.0761 |

- M1 reproduces: every earlier Astra value lies within about 2 MC SE.
- On these cells the new rule repairs the counterexample.
- The new L_W was never above the old L_W in any of 3.12M class replications (`new_above_old` = 0), so the rule is monotone as claimed.

## 4. Class verification: the declared grid 𝒟_P (`out_class_20k.jsonl`, `out_worst_100k.jsonl`)

All 156 cells × 20,000, independent engine. The table gives the worst cell per persistence level.

| Persistence | OLD worst joint miss | NEW worst joint miss [95% MC] | NEW worst size at θ_W = 0 |
|---|---|---|---|
| none | 0.0557 | 0.0165 [0.0147, 0.0182] | 0.0154 |
| φ 0.5 | 0.0612 | 0.0245 | 0.0203 |
| φ 0.7 | 0.0732 | 0.0269 | 0.0245 |
| φ 0.8 | 0.0873 | 0.0319 | 0.0291 |
| φ 0.9 | 0.1269 | **0.0475 [0.0445, 0.0504]** (rv 0.05, m 17 thin, θ 0.10) | 0.0442 |

Worst cells re-run at 100,000 replications:
- rv 0.05, m 17 **thin**, θ 0.10: **0.0471** (SE 0.0007) [0.0457, 0.0484];
- the same cell with **full** fills: 0.0467 [0.0454, 0.0481].

The Architect reported 0.0458 / 0.0464.

**Finding: on the Architect's exact grid** (c ~ U(0.35, 0.80), no pauses, Gaussian AR(1), m ∈ {17, 35}), the claimed joint miss ≤ 0.05 holds. My numbers agree with run G within MC error.

The margin at the grid's edge is about 0.3 pp. The conditional miss given reach reaches 0.080 at φ ≤ 0.8 and 0.138 at φ = 0.9 (disclosed by the Architect).

## 5. Beyond the grid, and inside the class as the spec writes it (`out_beyond_20k`, `out_mech_20k`, `out_fav_20k`, `out_confirm_100k`)

**The level is not attained over the declared class as frozen in the spec.**
- Spec §8.1b defines 𝒟_P's geometry as "CORE prices", and the manifest's 𝒟_P rows name no price distribution at all.
- The evidence covers only c ~ U(0.35, 0.80) (power table §4.8).
- R* can buy CORE legs up to 0.90 (§5.2), and §8.4 itself documents left-skewed favourite NO legs.

With a favourite-heavy CORE mix, c ~ U(0.70, 0.90): every leg is CORE, GO passes and reach is 0.84–0.98. The dependence is exactly a declared grid point:

| Cell (m 17, favourite CORE prices) | N | Reach | NEW joint miss / size (MC SE) [95% MC] | OLD |
|---|---|---|---|---|
| φ 0.9, rv 0.05, thin, θ 0.10 (miss) | 100,000 | 0.978 | **0.0635** (0.0008) [0.0620, 0.0650] | 0.1564 |
| φ 0.9, rv 0.05, thin, θ_W = 0 (**false REALIZED_WINDOW positive**) | 100,000 | 0.903 | **0.0605** (0.0008) [0.0591, 0.0620] | 0.1536 |
| φ 0.9, rv 0.10, thin, θ 0.10 (miss) | 20,000 | 0.835 | **0.0852** [0.0813, 0.0891] | 0.1918 |
| φ 0.9, rv 0.10, thin, θ_W = 0 (size) | 20,000 | 0.593 | **0.0721** [0.0685, 0.0757] | 0.1631 |
| φ 0.9, rv 0.05, m 35 full, θ 0.10 | 20,000 | 0.536 | 0.0619 [0.0586, 0.0653] | 0.1414 |
| φ 0.8, rv 0.10, full, θ 0.10 | 20,000 | 0.877 | 0.0534 [0.0502, 0.0565] | 0.1326 |
| 50% favourites + 50% class range, φ 0.9, rv 0.05, thin, θ 0.10 | 20,000 | 0.926 | 0.0500 [0.0470, 0.0530] | 0.1407 |
| favourites, no persistence | 20,000 | 0.995 | 0.0198 | 0.0625 |

Other admissible departures from the grid at a declared grid point (φ 0.9, rv 0.05, m 17):

| Variation | N | NEW joint miss [95% MC] | Status |
|---|---|---|---|
| 120 counted dates + 30 paused dates (VALID: ≤ 30 paused, §11.3 / §17.1) | 100,000 | **0.0531** [0.0517, 0.0544] | inside the spec's admissible geometry; the 𝒟_P text does not exclude pauses |
| Two-state regime with the same autocorrelation 0.9^k (non-Gaussian) | 20,000 | 0.0526 [0.0495, 0.0557] | second moments identical to the grid point |
| Literal §9 mechanism: error of a 30-date trailing-mean bias correction = boxcar MA(29), autocorrelation 1 − k/30, rv 0.05 | 20,000 | **0.0597** [0.0564, 0.0629] (thin θ 0.10); size **0.0522**; full 0.0559 | outside AR(1)-𝒟_P, but §8.1b asserts the class has "the order of the 30-date trailing-bias lag that §9 names" and the level "holds under the persistence §9 names" |
| Grid gaps m 12 / 20 / 25 × rv 0.03 / 0.05 / 0.07 | 20,000 each | worst 0.0486 [0.0456, 0.0516] (m 17, rv 0.05); m 12, rv 0.05 0.0473 | consistent with the grid |
| φ 0.95, rv 0.05 | 20,000 | 0.0769 (θ 0.10) / 0.0736 (size) | outside 𝒟_P; disclosed (Architect 0.072) |
| Two-component (φ 0.5, rv 0.05) + (φ 0.97, rv 0.02) | 20,000 | 0.0706 | outside 𝒟_P |
| Hemisphere regimes (φ 0.9, rv 0.10) | 20,000 | 0.0452 | holds |
| Regime + station ρ 0.10 / station-specific AR / dominant station / dominant date / heterogeneous θ (sd 0.10) / thick m 35 | 20,000 each | 0.014–0.045 | holds |
| 60 dates / 25 stations | 20,000 | 0.0006 / 0.0016 | valid; nearly powerless (disclosed) |

**Diagnosis.**
- The multi-block max uses t references with df_30 = 3 (df_20 = 5). Its margin at the worst grid point is about 0.3 pp.
- Any further liberal factor breaks the level:
  - left-skewed per-trade returns (high-c CORE legs; the same skew §8.4 documents for κ);
  - calendar dilution by pauses;
  - non-Gaussian regimes;
  - longer memory of the literal 30-date mechanism.
- The rule was selected as the first candidate that passes one fixed price distribution on one grid (§6). The thin margin is a symptom of that.

## 6. Frozen and implementable?

| Item | Finding |
|---|---|
| Block lengths, calendar alignment `floor((D − D_0)/b)`, df_b = min(G_B(b), G_S) − 1, max-of-three per b, T2 ⟺ L_W > 0, headline interval | fully frozen, outcome-blind, mechanical |
| Too few clusters | Under INFO_SUFFICIENT, IF2 (≥ 12 non-empty 5-blocks) gives ≥ 6 / 3 / 2 non-empty 10 / 20 / 30-blocks (each b-block contains exactly b/5 five-blocks with the same origin), and IF3 gives G_S ≥ 25, so df_b ≥ 1. L_W is not computed otherwise (17.3 is evaluated only for evaluated states). VERIFIED |
| Pauses / truncated windows | Handled by the calendar blocks (paused dates contribute no trades). But the 30-paused-date geometry exceeds the level (§5), and the class text does not exclude it |
| Interaction with IF5 | Unchanged (κ̂_core, 5-date). The level is a joint-with-reach rate; IF5 screening explains most thick-design validity (reach 0.005–0.07 at φ 0.9, m 35) |
| Selection after results | Self-attested. RM {5, 10, 20} was declared first, then failed at φ 0.9, and the 30-date block was then added under a "validity first" criterion. Git cannot verify the order: everything lands in one content commit. RM's failure is published and reproducible (my RM column: 0.0726 at 100,000), and the class was not shrunk after the failure. The selection is on synthetic results only, which is legitimate. But it is a pass-the-grid selection, and §5 shows it overfits the one price distribution and the Gaussian AR shape. **Not a separate finding; it is the root cause of the primary blocker** |
| Class statement | §8.1b: "𝒟_P is this declared grid … no level is claimed between grid points beyond what the grid shows". The printed level text (17.3), sentence (c), the claim matrix and the manifest instead state a continuous class ("φ ≤ 0.9, latent variance ≤ 0.10") and omit the price distribution. A real experiment never sits on the grid. Price mix and pauses are not grid dimensions the spec names, so the stated class is incomplete (§5) |

## 7. T1a / NEG / U_W under 𝒟_P (frozen 5-date-block surfaces)

Reproduced independently (`out_class_20k`, `out_frozen_20k`). Rates are joint with reach at the κ_core = 0 boundary (θ = 0), worst over the 𝒟_P grid; 20,000 each.

| Surface (declared level) | none | φ 0.8 | φ 0.9 | Given reach, φ 0.9 | Architect (φ 0.9) |
|---|---|---|---|---|---|
| T1a → INFORMATION_DETECTED (0.025; FWER 0.05) | 0.0265 | 0.0543 [0.0511, 0.0574] | **0.0888** [0.0848, 0.0927] | 0.131 | 0.0893 |
| NEG → NEGATIVE_INFORMATION / CORE_ADVERSE / R*_CORE_INFORMATION_REJECTED (0.025) | 0.0271 | 0.0445 [0.0416, 0.0473] | **0.0707** [0.0672, 0.0743] | 0.105 | 0.0694 |
| U_W miss → REALIZED_WINDOW_BOUND (declared 95%) | 0.0279 | 0.0480 (θ 0.10) | **0.0755** [0.0718, 0.0792] | 0.106 | 0.0765 |

Additional geometry: favourite CORE prices at φ 0.9 / rv 0.05 give T1a 0.115 and NEG 0.068–0.070. The literal §9 boxcar gives T1a 0.12, NEG 0.094 and U_W 0.096.

Judgement:
- **The magnitudes are real and material.**
  - NEG runs at 2.8× and T1a at 3.6× the declared 0.025 inside the persistence class the spec itself now declares. The overshoot is larger under the literal §9 mechanism.
  - By the project's own D8 precedent (date-only κ test 0.095–0.205 at nominal 0.025 was MAJOR), this order of overshoot on a label-issuing test is material.
- **The claim language is only partly honest.**
  - Qualified: claim matrix 17.8, §8.1b disclosure table, §21 row 41, §27 and the manifest ALPHA row ("can be exceeded").
  - Unqualified, and false inside 𝒟_P:
    - §6.3 ("T1 is a union test at familywise α = 0.05"; IUT "≤ α" for joint states);
    - §6.1 and §10.1 levels;
    - §8.4 (NEG "inside the 0.05 guarantee");
    - §8.5 / §8.5b line 468 (U_W "declared level 95%");
    - §9 ("the two-way max-of-three test holds size");
    - §10.3 (NEG as "V2's only real negative-result instrument");
    - §24 ("including a real negative result").
  - The 17.3 report fields INFO_SOURCE, CORE_ADVERSE and REALIZED_WINDOW_BOUND print no level text. L_W does.
  - 17.8's INFORMATION_DETECTED row lists the assumption "no cross-block date persistence", which §8.1b says §9 names.
  - The qualifiers quote point estimates from one price distribution, and they are already exceeded under favourite-heavy CORE mixes.
- **Downstream consequences.**
  - A false NEG issues the information-level falsification R*_CORE_INFORMATION_REJECTED and the scientific state NEGATIVE_INFORMATION__*, and vetoes SHADOW_CONTINUATION_SIGNAL (CORE_ADVERSE = TRUE).
  - A false T1a issues INFORMATION_DETECTED ("chosen legs underpriced net of all-in cost").
  - A false U_W issues REALIZED_WINDOW_LOSS_CONFIRMED and related fields (report only).
  - Second-order: the 8.1b headline 90% interval now uses multi-block SEs, while U_W keeps 5-date blocks. One report can therefore print REALIZED_WINDOW_LOSS_CONFIRMED (U_W < 0) beside a headline interval that contains 0, an internal inconsistency created by the asymmetric repair.
  - No capital, prospective or R*-net path is involved, so this is not CRITICAL.
- **Severity: MAJOR (M2).**
  - Declared probabilities on label-issuing tests are materially violated inside the class the spec declares for persistence, while the error-control, engine and report sections still market them as nominal.
  - The Architect explicitly left the severity to Astra. This is not the Architect's fault: the orchestrator's frozen repair surface listed T1a, NEG and U_W as unchanged. But the candidate spec as a whole now carries the defect knowingly.
  - REPAIRABLE_BOUNDED (§15).

## 8. R3 re-verification (independent)

All checks are in `out_r3_algebra.json` and `out_states.json`.

| Surface | Result |
|---|---|
| Proposition 1 (θ_F = E_Q[N]/E_Q[C] = (1 − ε_Q)θ_A + ε_Q θ_B, ε = cost-mass share) | 59,600 random epoch laws (1–5 worlds; random, worst-return-first and single-max-cost, outcome-dependent partitions; partial fills; fee-inclusive): **0** identity violations, max rel. error 6e-12 |
| N_j ≥ −C_j; θ_B ≥ −1 | 300,000 fee-inclusive trades with y ∈ {0, ½, 1}: min N/C = −1.000 exactly; min θ_B −0.99975 |
| Theorem 2 L_T = (1 − ε)(L_W − δ) − ε | **0** violations; algebra holds for any L_W, so the new L_W is a valid input |
| Cost mass vs dates / trades | One cap date among 119 ordinary dates (θ_F = −0.0567): the date-count ε (0.0083) and trade-count ε (0.0453) give false bounds (+0.091 / +0.050); cost mass (0.1424) is exact |
| Frontier ε*(δ, τ) closed form + domain guard | 3,000 cases vs a 400,001-point brute force: 0 mismatches; 0 monotonicity violations; the unguarded form prints 3 / 6 at L_W = −1.5 / −1.2, where the guarded form gives 0 |
| k*(H) | 3,000 cases: 0 mismatches |
| Thresholds | No ε / δ / H / τ threshold anywhere; grids are reporting-only |
| Prospective labels | No unconditional prospective label in either direction; PROSPECTIVE_* constants; no R* rejection (R*_REJECTED_AS_NET_STRATEGY has no issuing condition) |
| SHADOW_CONTINUATION_SIGNAL | Shadow-only; reachable only from {INFORMATION_DETECTED, NO_INFORMATION_DETECTED}__REALIZED_WINDOW_VALUE_SUPPORTED with CORE_ADVERSE = FALSE |
| State machine | 4,608 consistent combinations → exactly **11** SCIENTIFIC_STATE values, total and deterministic; no state name contains PROSPECTIVE / EXCLUDED / DEPLOY / CAPITAL / EDGE / CONFIRMED |
| Claim-language scan (all Weather V2 files) | READY_FOR_CAPITAL, DEPLOYABLE, deployment-ready, validated / confirmed / estimated / verified transport, "sufficiently robust", "future value confirmed": 0 hits. "edge exists" appears only in negations (17.5, 17.8). PROSPECTIVE_VALUE_CONFIRMED appears only as retired / history |
| Power-ceiling theorems | Unchanged (§8.5b byte-identical; §8.5c mirror theorem unchanged): SUPPORTED |

The R3 surfaces pass independently.

## 9. Raw-output reproduction

At 4423c5c3 the Architect's script was re-run with `repro 20000` and `c3 20000` (`arch_*_rerun.jsonl`):
- **byte-identical** to the committed repro block;
- **byte-identical** to the committed class lines with the same ids (that is, class cells);
- **byte-identical** to the committed c3 block.

The script is synthetic only.

## 10. Second-order search

- **New L_W used consistently** in T2, 17.3, sentence (c), frontier ε*, k*(H), Theorem 2 and the headline interval. No surviving reference elsewhere gives the old L_W as the current definition.
- **Old level statements** remain only under SUPERSEDED or history markers:
  - §8.5c R3 error statement;
  - 17.3 R3 parenthesis;
  - power table §4.7 reading 4;
  - delta D4-C3 conditional bullet.
- **Stale wording (minor m10).**
  - §8.5c line 495: "by the unchanged T2 / CR engine".
  - Delta D4-C3 CLAIM_STRENGTH: "REALIZED_WINDOW_VALUE_SUPPORTED: θ_W > 0 (size ≤ 0.05, IUT)" is unmarked, while the neighbouring line is marked.
  - §2 decision record has no D4-C3-M1 row.
  - "the level is lower" (§8.5c, 8.1b) is ambiguous: it means coverage is lower, i.e. the miss is higher.
- **No new semantic alias**, and no unconditional future-value language.
- **U_W vs headline interval inconsistency** (part of M2, §7).
- **Conditional-on-reach miss** (0.080 at φ ≤ 0.8 / 0.138 at φ 0.9) is disclosed in §8.1b and §8.5c. Sentence (c), printed only in reached runs, says "with 95% sampling confidence" without the joint-with-reach qualifier. Minor m11; the earlier Astra used the joint metric.

## 11. Claim matrix check (17.8 at 4423c5c3)

| Row | Stated level | Holds? |
|---|---|---|
| REALIZED_WINDOW_VALUE_SUPPORTED / NOT_ROBUST | size ≤ 0.05 over 𝒟_P | On the exact grid, yes (worst 0.0442). Over 𝒟_P as written ("CORE prices", pauses allowed), **no**: 0.0605 [0.0591, 0.0620] at a grid point, and 0.0721 at φ 0.9 / rv 0.10 |
| TRANSPORT / CONDITIONAL_PROSPECTIVE_SUPPORT | sampling event at 0.95 over 𝒟_P | as above (miss up to 0.0852) |
| REALIZED_WINDOW_BOUND | declared 95%, with the measured overshoot quoted | qualified in 17.8 only; not in §8.5 or the printed field |
| INFORMATION_DETECTED / NEGATIVE_INFORMATION | nominal, with the measured overshoot quoted | qualified in 17.8 only; §6.3 / §8.4 / §9 still guarantee nominal; favourite mixes exceed the quoted numbers |
| PROSPECTIVE_*, R*_REJECTED_AS_NET_STRATEGY, SHADOW, OPERABILITY | constants / no claim / shadow-only / descriptive | yes |
| Rejects R*? / Builder? / Capital? columns | all "no" | yes |

## 12. Regression table D1–D12

| Item | Status at 4423c5c3 |
|---|---|
| D1 power / PCE | θ_PCE formula and GO unchanged; the power shortfall of the calibrated T2 is disclosed (P(T2) at θ_PCE 0.46–0.55) — CLOSED (disclosed) |
| D2 | CLOSED |
| D3 | CLOSED |
| D4 | **OPEN_MAJOR.** C1 / C2 / C3 closed. M1 is repaired on the grid but not over the declared class as written (M1-R). M2 frozen-surface undercoverage |
| D5 | CLOSED |
| D6 | CLOSED |
| D7 | CLOSED |
| D8 | CLOSED with disclosed limitation; T2's engine re-qualified by 8.1b. The κ / θ_core engine limitation under persistence is now quantified as M2 |
| D9 | CLOSED |
| D10 | CLOSED_ACCEPTED_AND_DISCLOSED (11-value partition unchanged) |
| D11 | CLOSED |
| D12 | CLOSED |

## 13. Minors

| Minor | Status |
|---|---|
| m8 | **CLOSED**: domain guard in spec 17.3, the manifest ROBUST_BOUND / FRONTIER row and delta D4-C3; no unguarded `max(0, (L_W …` remains in any file |
| m9 | **CLOSED**: SUPERSEDED markers on power table §4.6 reading 5 (and its table) and on delta D4-C2 CLAIM STRENGTH |
| m10 (new) | stale "unchanged T2 / CR engine" wording (§8.5c); unmarked D4-C3 size line in the delta; no §2 decision row for D4-C3-M1; ambiguous "the level is lower" |
| m11 (new) | sentence (c) prints "95% sampling confidence" in reached runs without the joint-with-reach qualifier (conditional miss up to 0.138 in 𝒟_P) |

## 14. Subverdicts

```text
M1_REPRODUCED_ON_OLD_RULE                  = TRUE (0.0799 [0.0761, 0.0836] size; 0.0916 [0.0876, 0.0956] miss)
D4_M1_SOURCE_BOUND_CALIBRATION             = BLOCKED (holds on the exact run-G grid: worst 0.0471 [0.0457, 0.0484] at 100,000;
                                             fails over 𝒟_P as frozen: favourite CORE prices 0.0605 [0.0591, 0.0620] size,
                                             0.0635 [0.0620, 0.0650] miss at 100,000; up to 0.0852 [0.0813, 0.0891];
                                             30 paused dates 0.0531 [0.0517, 0.0544])
D4_INFORMATION_AND_UW_CALIBRATION          = BLOCKED (M2: T1a 0.0888, NEG 0.0707, U_W miss 0.0755 inside 𝒟_P vs 0.025 / 0.025 / 0.05;
                                             nominal still asserted in 6.3 / 8.4 / 8.5 / 9 and the printed fields)
D4_R1_REALIZED_WINDOW_BOUND                = PASS for its algebra and tail supremum (8.5 byte-identical); its core level is part of M2
D4_R2_PROSPECTIVE_EXCLUSION_REMOVAL        = PASS
D4_C3_UNCONDITIONAL_CONFIRMATION_REMOVAL   = PASS
D4_R3_COST_MASS_TRANSPORT_BOUND            = PASS (independent fuzz; 0 violations)
D4_R3_ROBUSTNESS_FRONTIER                  = PASS (closed form, guard, monotonicity, k*)
D4_R3_CLAIM_SEMANTICS                      = PASS for prospective / capital language; the economic and information level statements are
                                             carried by M1-R / M2; m10, m11
D4_R3_STATE_MACHINE                        = PASS (11 values, total; shadow only from SUPPORTED ∧ ¬CORE_ADVERSE)
D4_R3_POWER_CEILING_THEOREM                = SUPPORTED (unchanged)
m8                                         = CLOSED
m9                                         = CLOSED
RAW_OUTPUT_REPRODUCTION                    = PASS (repro, class-id and c3 lines byte-identical)
TRADING_RULE_CHANGED                       = FALSE
OUTCOME_LEAKAGE                            = NONE
```

## 15. Verdict and blocker

```text
ASTRA_WEATHER_V2_D4_C3_M1_RECHECK = BLOCKED_D4_M1_SOURCE_BOUND_LEVEL_NOT_ATTAINED_OVER_DECLARED_CLASS_AND_FROZEN_SURFACE_UNDERCOVERAGE
EXPERIMENT_FEASIBILITY_V2         = BLOCKED_D4_M1_SOURCE_BOUND_LEVEL_NOT_ATTAINED_OVER_DECLARED_CLASS_AND_FROZEN_SURFACE_UNDERCOVERAGE
NEXT_AUTHORIZED_ACTION            = BOUNDED ARCHITECT REPAIR ONLY
```

### Primary blocker: M1-R (MAJOR)

**Root cause.** The 8.1b rule was selected as the first candidate that passes one simulated grid with c ~ U(0.35, 0.80), no pauses and a Gaussian AR(1) shape. It passes there by about 0.3 pp. The frozen class text instead says "CORE prices", omits the price distribution in the manifest, and does not exclude pauses. Left-skewed high-c CORE returns, which §8.4 itself documents, push the joint miss above 0.05 at declared grid points. So do calendar dilution by up to 30 paused dates and non-Gaussian regimes. The stated "≤ 0.05 over 𝒟_P" is printed in 17.3, the claim matrix, the manifest and sentence (c).

**Counterexample** (`astra_m1_run.py confirm 100000`). Seeds `[77100101, 8, i, 1..4]`, synthetic only:
- Setup: 120 + 14 dates, 48 stations, m = 17, thin fills U(5, 25). CORE favourites c ~ U(0.70, 0.90), p = c(1 + θ). Latent (0.05, 0.05, 0.10) plus AR(1) date regime with φ = 0.9 and rv = 0.05, a 𝒟_P grid point. Reach 0.90–0.98.
- False REALIZED_WINDOW positive at θ_W = 0: **0.0605 [0.0591, 0.0620]**.
- L_W miss at θ = 0.10: **0.0635 [0.0620, 0.0650]**.
- At rv = 0.10 (20,000 reps): 0.0721 / 0.0852.
- Also: 30 paused dates in the class geometry give **0.0531 [0.0517, 0.0544]** at 100,000.

### Second blocker: M2 (MAJOR)

T1a, NEG and U_W keep 5-date blocks and run at 0.089 / 0.071 / 0.076 (joint; 0.13 / 0.10 / 0.11 given reach) inside 𝒟_P, against 0.025 / 0.025 / 0.05. Nominal control is still asserted in §6.1, §6.3 (FWER and IUT), §8.4, §8.5, §9, §10.1, §10.3, §24 and the 17.3 printed fields. NEG drives R*_CORE_INFORMATION_REJECTED and vetoes the shadow signal.

### Minimal repair surface (Architect's choice per item; bounded)

- **M1-R.**
  - Either (a) calibrate L_W over a completely stated class that includes the admissible CORE price range (up to c = 0.90, favourite-heavy mixes) and pauses up to 30. A non-Gaussian regime check (two-state, same autocorrelation) and the literal §9 30-date trailing-mean mechanism should be explicitly inside or explicitly outside. Re-show ≥ 20,000 per cell and ≥ 100,000 at the worst cell, with margin.
  - Or (b) state the class completely and honestly: price distribution, no pauses, Gaussian AR shape. Then state the measured level for favourite-heavy mixes, paused calendars and the boxcar mechanism (up to 0.085), propagated to §8.1b, the §8.5c error statement, 17.3 level text, sentence (c), 17.8 and the manifest T2_SOURCE_BOUND / ROBUST_BOUND / ALPHA / 𝒟_P rows.
  - Remove the "level that holds under the persistence §9 names" sentence unless (a) covers the literal mechanism.
- **M2.**
  - Either (a) apply the same multi-block (or the M1-R-repaired) construction to κ̂_core for T1a / NEG and to θ̂_core for U_W, and disclose the NEG / T1a power change (§10.3 NEG power ≈ 0.9 claim);
  - or (b) propagate the qualified levels to every surface that states them: §6.1, §6.3 (FWER, IUT clause), §8.4, §8.5 / §8.5b line 468, §9 last paragraph, §10.1, §10.3, §24, the 17.3 printed fields (level text with INFO_SOURCE, CORE_ADVERSE, REALIZED_WINDOW_BOUND), and the manifest NULLS / NEG RULE / ALPHA rows, using bounds valid over the completed class.
  - Either way, resolve the U_W vs headline-interval inconsistency.
- **Minors m10 and m11** as listed in §13.

Governance must authorise touching T1a / NEG / U_W if option (a) is chosen for M2. They were frozen in the cycle-1 repair surface.

**AFFECTED_FILES:**
- spec: §6.1, §6.3, §8.1b, §8.4 (statement only under b), §8.5 (statement only under b), §8.5c, §9 (statement), §10.3, §17.3, §17.8, §21, §24, §27;
- manifest: 𝒟_P, T2_SOURCE_BOUND, ROBUST_BOUND, ALPHA, NULLS, NEG RULE, section F;
- delta: new entry;
- power table: §4.8, new rows;
- run-G script or a successor;
- architect state and checkpoint.

**UNCHANGED_SURFACES:**
- R*, h, W, signal, cohort, entry, T_entry, S_ref sizing, execution, 0.04 strata;
- PCE formula and GO (except disclosed power);
- R1 tail supremum, R2 exclusion removal;
- R3 transport algebra (Proposition 1, Theorem 2), cost-mass ε, frontier definition with guard, k*(H);
- constants, label vocabulary, SHADOW_CONTINUATION_SIGNAL, 11-value state machine.

**REQUIRED_REAUDIT_SURFACE:**
- L_W joint miss and size over the completed class, including favourite-heavy CORE mixes, 30 paused dates and the two-state regime, at ≥ 20,000 per cell and ≥ 100,000 at the worst cell;
- T1a / NEG / U_W levels or their propagated statements;
- every place a level is stated;
- m10, m11;
- R1 / R2 / R3 regression.

**Classification: REPAIRABLE_BOUNDED.** Both are calibration or statement repairs of existing inference objects. Neither touches the trading rule, the estimands or the transport algebra.

```text
CRITICAL_FINDINGS = NONE
MAJOR_FINDINGS    = M1-R (source-bound level not attained over the declared class as frozen), M2 (T1a / NEG / U_W undercoverage inside 𝒟_P while marketed as nominal)
MINOR_FINDINGS    = m10, m11 (m8, m9 CLOSED)
MISSING_PROOF     = T1b (PINM) behaviour under cross-block persistence is unmeasured (tail stratum absent from all run-G / Astra designs); level of L_W for price mixes other than U(0.35, 0.80)
BUILDER_AUTHORIZED = FALSE; REAL_CAPITAL_AUTHORIZED = FALSE; LIVE_TRADING_AUTHORIZED = FALSE; t0 = NOT_DECLARED
```
