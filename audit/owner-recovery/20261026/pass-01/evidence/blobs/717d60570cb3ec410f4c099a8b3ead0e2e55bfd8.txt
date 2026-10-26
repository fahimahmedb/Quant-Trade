# WEATHER FORWARD V2 — RESUME CHECKPOINT (D4 repairs R1, R2, R3) — 2026-09-29 / 2026-09-30

```text
ROLE                 = Weather Forward V2 Architect — bounded D4 repairs only: R1 (C1), R2 (C2), R3 (C3 + transportability)
PURPOSE              = durable restart surface: a fresh session (after token / context / container loss) resumes from
                       THIS FILE, never from chat memory
BRANCH               = claude/charming-allen-948kd8
STATUS               = WEATHER_FORWARD_SPEC_V2_D4_C3_TRANSPORT_REPAIR = READY_FOR_ASTRA_D4_C3_RECHECK   (R2 @e45d2ce7 BLOCKED C3 by Astra @92c2f706)
REAL_CAPITAL_AUTHORIZED = FALSE · LIVE_TRADING_AUTHORIZED = FALSE · t0 = NOT_DECLARED · BUILDER_AUTHORIZED = FALSE
```

## 1. Resume protocol (do this first, in order; stop at the first mismatch)

1. `git fetch origin --prune && git checkout claude/charming-allen-948kd8 && git pull --ff-only origin claude/charming-allen-948kd8`
2. Verify the authority chain (section 2): `git merge-base --is-ancestor <sha> HEAD` for 726070a, e1cf4ca, 5760ffa, 94b59348, 7d95c00.
3. Read, in this order: `QUANT_NORTH_STAR.md`; this file; `WEATHER_FORWARD_ARCHITECT_STATE_V2_2026-09-29.md`; Astra `ASTRA_WEATHER_V2_REAUDIT_STATE_2026-09-29.md`. Read the spec only in the sections named in section 5.
4. Find the first phase in section 3 whose status is not DONE and continue exactly there. Do not redo a DONE phase; do not re-derive a decision in section 4 unless new evidence contradicts it.
5. After finishing any phase: update its row in section 3, commit (message prefix `checkpoint(weather_forward):`), push, verify `git rev-parse HEAD == git rev-parse origin/claude/charming-allen-948kd8`.

## 2. Authority chain (immutable; never modify these objects)

| Object | Branch | SHA |
|---|---|---|
| V1 frozen spec | claude/intelligent-gates-msidml | 726070a199957a6fc05515ebb3027e945028fddc |
| Astra V1 feasibility review | claude/dreamy-franklin-1vki4t | e1cf4ca0851eace2912ce8a9bcd4a8400ebf4250 |
| Fable design challenge (advisory) | claude/zen-einstein-9moyry | 5760ffa5b5da2a988cfe6d1503c86c561acf9b1f |
| V2 audited object | claude/charming-allen-948kd8 | 94b59348d5b79cd3c53dcba0b791ce1daeb75d60 |
| Astra V2 re-audit (BLOCKED D4) | astra/weather-forward-v2-independent-reaudit-2026-09-29 | 7d95c00abccfbc805c0d8abca65a6b93268741a2 |
| D4 repair R1 head (audited) | claude/charming-allen-948kd8 | 24d2342fcff8fd78a769a9ecaf7551ab2578e2ef |
| Astra D4 recheck (BLOCKED C2) | astra/weather-forward-v2-independent-reaudit-2026-09-29 | 3d18085862f239a81936345989b4e26414cedcf3 (read only; not merged into this branch) |
| D4-C2 repair R2 head (audited) | claude/charming-allen-948kd8 | e45d2ce7e2605a4136804d2c1b31efa3aa8120e1 |
| Astra D4-C2 recheck (BLOCKED C3) | astra/weather-forward-v2-independent-reaudit-2026-09-29 | 92c2f706d2ac75af9ae9710061c60df520234410 (read only; not merged into this branch) |

## 3. Phase ledger (checkpoints)

| Phase | Content | Status | Checkpoint |
|---|---|---|---|
| P0 | fetch; read North Star, V2 @94b5934, Astra re-audit + state; fast-forward branch onto 7d95c00 (Astra files byte-identical) | DONE | local ff to 7d95c00 |
| P1 | committed sim: exact frozen contract for the retired bound (λ ≤ 1000, μ ≤ 50, 40 iterations, B = 20,000, frozen seed and per-draw order); repaired bound; run D (`python3 research/weather_forward/WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py d4`, ≈ 3 min on 4 cores) | DONE | raw output in section 6 |
| P2 | spec §8.2 / §8.5 / §6 / §17.3 / §17.6 / §20–21 / §24 / §27; manifest A + C; delta D4.d / D4.e; power table §4.5; architect state | DONE | 05836143a249f5571a29403727c6d90df2c8b7c8 (local commit, repair content) |
| P3 | this checkpoint file committed; push; verify remote == local | DONE | 020ec60444e0425ce01a59d5db91c5f0a397f814 (pushed; remote == local verified; Astra files and North Star unchanged) |
| P4 | final report to the user (≤ 10 lines): branch, exact SHA, repair, exclusion semantics, D4 bound status, reproductions, files, D1–D12 carry-forward, next action | DONE with the commit that marks this row | recheck target = branch tip (scientific content identical to 0583614) |

If P3 is found incomplete on resume: run `git log origin/claude/charming-allen-948kd8..HEAD --oneline`; if 0583614 and the checkpoint commit are local only, push them (`git push -u origin claude/charming-allen-948kd8`, retry 2 / 4 / 8 / 16 s on network errors only), then verify. If the container was lost before the push, the local commits are gone: rebuild from this file only if it exists on the remote; otherwise redo P1–P2 from the decisions in section 4 (they need no new research).

## 3b. Phase ledger — D4-C2 repair R2 (2026-09-30)

| Phase | Content | Status | Checkpoint |
|---|---|---|---|
| Q0 | fetch; verify remote head = 24d2342; read North Star, this file, Astra D4 recheck + state @3d18085 | DONE | — |
| Q1 | `WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py` modes ceiling / scenarios 4000 / counts 4000 / confirm 4000 / grid 200 (≈ 15 min on 4 cores); raw output `WEATHER_FORWARD_V2_D4_C2_RUN_E_OUTPUT_2026-09-30.jsonl` | DONE | 4845d32 |
| Q2 | spec (5.1, 6, 8.5, 8.5b, 8.6, 10.3, 11.2, 17.2–17.8, 20, 21, 24, 26, 27), manifest (A rows + D), delta D4-C2, power table 4.6 / 5, architect state (incl. self-attack) | DONE | 4845d32 |
| Q3 | this ledger; commit; push; verify remote == local | DONE with the commit that marks this row | recheck target = branch tip |

R2 decisions (do not re-derive): identification theorem 8.5b ⇒ PROSPECTIVE_EXCLUSION = NOT_IDENTIFIED_IN_V2; economic axis PROSPECTIVE_VALUE_{CONFIRMED, NOT_ROBUST, INDETERMINATE}; R1 bound kept as θ_W report field REALIZED_WINDOW_BOUND; R*_REJECTED_AS_NET_STRATEGY never issued; CORE_ADVERSE drives R*_CORE_INFORMATION_REJECTED and the forward signal (Astra m2); R2-A rejected (independence assumption, never excludes), R2-C only as report field. Evidence: power table §4.6. Next: ASTRA BOUNDED D4-C2 RECHECK ONLY.

## 3c. Phase ledger — D4-C3 transport repair R3 (2026-09-30)

| Phase | Content | Status | Checkpoint |
|---|---|---|---|
| S0 | fetch; verify remote head = e45d2ce7; read North Star, this file, architect state, Astra D4-C2 recheck + state @92c2f706 | DONE | — |
| S1 | `WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py` modes frontier / c3 20000 / scenarios 4000 / grid 1000 / coverage 20000 (≈ 25 min on 4 cores); raw output `WEATHER_FORWARD_V2_D4_C3_RUN_F_OUTPUT_2026-09-30.jsonl`; frontier / scenarios / c3 re-run byte-identical | DONE | 3086efb |
| S2 | spec (header, 1, 2, 4.1, 5.1, 6.1, 6.3, 8.5b wording, new 8.5c, 17.2, 17.3, 17.5–17.8, 21, 24, 26, 27), manifest (A rows + C / D markers + E), delta D4-C3, power table 4.7, architect state, this file (m4) | DONE | 3086efb |
| S3 | this ledger; commit; push; verify remote == local | DONE with the commit that marks this row | recheck target = branch tip |

R3 decisions (do not re-derive without new evidence):
- θ_P is a strategic target, not a V2 estimand. No unconditional label in either direction: exclusion has the 8.5b ceiling; confirmation has the 8.5c mirror theorem.
- ECONOMIC_RESULT is REALIZED_WINDOW_VALUE_{SUPPORTED, NOT_ROBUST, INDETERMINATE} on θ_W, with T2 unchanged.
- Transport uses the cost-mass class 𝒯_H(ε, δ), the deductive bound L_T = (1 − ε)(L_W − δ) − ε (Proposition 1 exact), and the frontier ε*(δ, τ), k*(H) and concentration report. Only reporting grids exist; no threshold is chosen.
- Observable invalidation can only revoke.
- SHADOW_CONTINUATION_SIGNAL replaces the forward signal.
- Minors m3–m7 fixed.

## 4. Decisions already made (do not re-derive)

1. (SUPERSEDED in scope by R2: the bound is the θ_W report field REALIZED_WINDOW_BOUND; Astra m4) Repair R1 = exclusion bound `U(θ) = w_core (θ̂_core + t_{df,0.975} SE_CR(θ̂_core)) + M_tail`, `M_tail = Σ_TAIL (n_j − C_j) / Σ C_j` (every TAIL leg wins). Coverage ≥ core coverage for every tail geometry and dependence (spec §8.5 proof).
2. TPM / SHR tail models retired from every role; PINM gates only T1b.
3. (SUPERSEDED by R2: R*_REJECTED_AS_NET_STRATEGY is never issued; Astra m4) Rule 17.6: `R*_REJECTED_AS_NET_STRATEGY` iff `NET_VALUE_EXCLUDED`; `NEGATIVE_INFORMATION` → `R*_CORE_INFORMATION_REJECTED` (information-level). Reason: the old NEG clause false-rejected θ = 0.0315 in 32% of Astra A1 runs.
4. Routes: A subsumed by `M_tail`; B adopted in assumption-free form; C cannot restrict true tail probabilities; nothing smaller is valid.
5. (Partly SUPERSEDED: the SCIENTIFIC partition has 11 values since R2; the forward signal is SHADOW_CONTINUATION_SIGNAL since R3; Astra m4) Unchanged: R*, h, W, model, T_entry, cohort, strata, θ, κ_core, T1a, T1b, T2, NEG test, engines, dependence, PCE / GO, gates G1–G3, 14-value SCIENTIFIC partition, validity, operability, forward-signal rule, analysis time. D1, D2, D3, D5–D9, D11, D12 CLOSED; D10 CLOSED_ACCEPTED_AND_DISCLOSED.
6. No live data, no outcomes, no wallet data used in the repair (synthetic only).

## 5. Where the repair lives (targeted reading only)

Spec: header, §2 rows D4-ENG / D4-UB / D4-REJ, §6.1 EXCL row, §6.3, §8.2 "Uses", §8.5, §10.3 drift note, §11.2 readiness report, §17.3, §17.6, §17.7, §20 item 9, §21 items 7, 9, 21–24, §24, §26, §27. Manifest: header, A5 rows EXCLUSION_UPPER_BOUND / RETIRED / REJECTION_RULE / ALPHA / PINM, section C. Delta: D4.c note, D4.d, D4.e. Power table: §4 intro note, §4.4 item 4, §4.5, §5.

## 6. Evidence snapshot (run D raw output, synthetic; copied from the ephemeral scratchpad)

```json
{"cov_old": 0.8885, "cov_new": 1.0, "exERT_old": 0.0742, "exERT_new": 0.0, "exPCE_old": 0.4119, "exPCE_new": 0.0, "rej_old": 0.3204, "rej_new": 0.0, "T2": 0.0014, "NEG": 0.3224, "T1": 0.0324, "scenario": "A1_positive_tail_negative_core", "reps": 8000, "theta_true": 0.0315, "pce": 0.08, "M_tail": 0.9685, "readiness": {"pce": 0.08, "se0_theta": 0.03093, "se0_kappa": 0.01296, "sigma0_sq": 1.32587, "stations": 46, "kish": 26.2}, "GO": true, "lookup_W0_to_4": [0.2633, 1.3313, 2.2442, 3.1038, 3.8748]}
{"cov_old": 0.8632, "cov_new": 1.0, "exERT_old": 0.0082, "exERT_new": 0.0, "exPCE_old": 0.1126, "exPCE_new": 0.0, "rej_old": 0.0292, "rej_new": 0.0, "T2": 0.0322, "NEG": 0.0264, "T1": 0.0556, "scenario": "A2_pure_hidden_lottery", "reps": 5000, "theta_true": 0.0852, "pce": 0.08, "M_tail": 0.9685, "readiness": {"pce": 0.08, "se0_theta": 0.03093, "se0_kappa": 0.01296, "sigma0_sq": 1.32587, "stations": 46, "kish": 26.2}, "GO": true, "lookup_W0_to_4": [0.2633, 1.3313, 2.2442, 3.1038, 3.8748]}
{"cov_old": 0.9985, "cov_new": 1.0, "exERT_old": 0.3815, "exERT_new": 0.0, "exPCE_old": 0.7975, "exPCE_new": 0.0, "rej_old": 0.829, "rej_new": 0.0, "T2": 0.0, "NEG": 0.8415, "T1": 0.0185, "scenario": "P3_negative_core_fair_tail", "reps": 2000, "theta_true": -0.098, "pce": 0.08, "M_tail": 0.9685, "readiness": {"pce": 0.08, "se0_theta": 0.03093, "se0_kappa": 0.01296, "sigma0_sq": 1.32587, "stations": 46, "kish": 26.2}, "GO": true, "lookup_W0_to_4": [0.2633, 1.3313, 2.2442, 3.1038, 3.8748]}
{"cov": 0.9782, "exERT": 0.0217, "exERT_false": 0.0217, "T2": 0.1528, "kind": "uniform", "target": 0.02, "rho": [0.05, 0.05, 0.1], "reps": 4000, "D": 120, "S": 48, "theta_true_mean": 0.02, "pce_median": 0.07, "rho_name": "TRUE"}
{"cov": 0.9705, "exERT": 0.0295, "exERT_false": 0.0295, "T2": 0.1082, "kind": "uniform", "target": 0.02, "rho": [0.15, 0.15, 0.1], "reps": 4000, "D": 120, "S": 48, "theta_true_mean": 0.02, "pce_median": 0.07, "rho_name": "STRESS"}
{"cov": 0.9762, "exERT": 0.0238, "exERT_false": 0.0238, "T2": 0.1185, "kind": "uniform", "target": 0.02, "rho": [0.02, 0.15, 0.1], "reps": 4000, "D": 120, "S": 48, "theta_true_mean": 0.02, "pce_median": 0.07, "rho_name": "SST"}
{"cov": 0.981, "exERT": 0.019, "exERT_false": 0.019, "T2": 0.2758, "kind": "favourite", "target": 0.02, "rho": [0.05, 0.05, 0.1], "reps": 4000, "D": 120, "S": 48, "theta_true_mean": 0.02, "pce_median": 0.05, "rho_name": "TRUE"}
{"cov": 0.9745, "exERT": 0.0255, "exERT_false": 0.0255, "T2": 0.1362, "kind": "mid5", "target": 0.02, "rho": [0.05, 0.05, 0.1], "reps": 4000, "D": 120, "S": 48, "theta_true_mean": 0.02, "pce_median": 0.08, "rho_name": "TRUE"}
{"cov": 0.993, "exERT": 0.0052, "exERT_false": 0.0052, "T2": 0.03, "kind": "boundary_hidden", "target": 0.025, "rho": [0.05, 0.05, 0.1], "reps": 4000, "D": 120, "S": 48, "theta_true_mean": 0.025, "pce_median": 0.1, "rho_name": "TRUE"}
{"cov": 0.9705, "exERT": 0.0248, "exERT_false": 0.0248, "T2": 0.1072, "kind": "boundary_diffuse", "target": 0.025, "rho": [0.05, 0.05, 0.1], "reps": 4000, "D": 120, "S": 48, "theta_true_mean": 0.025, "pce_median": 0.1, "rho_name": "TRUE"}
{"cov": 0.9748, "exERT": 0.0253, "exERT_false": 0.0253, "T2": 0.1192, "kind": "min_geometry", "target": 0.02, "rho": [0.05, 0.05, 0.1], "reps": 4000, "D": 60, "S": 25, "theta_true_mean": 0.02, "pce_median": 0.07, "rho_name": "TRUE"}
{"cov": 0.974, "exERT": 0.026, "exERT_false": 0.026, "T2": 0.1035, "kind": "min_geometry", "target": 0.02, "rho": [0.02, 0.15, 0.1], "reps": 4000, "D": 60, "S": 25, "theta_true_mean": 0.02, "pce_median": 0.07, "rho_name": "SST"}
{"cov": 0.973, "exERT": 0.3388, "exERT_false": 0.0, "T2": 0.0058, "kind": "small_tail_allwin", "target": -0.05, "rho": [0.05, 0.05, 0.1], "reps": 4000, "D": 120, "S": 48, "theta_true_mean": -0.0324, "pce_median": 0.07, "rho_name": "TRUE"}
{"cov": 0.968, "exERT": 0.513, "exERT_false": 0.0, "T2": 0.002, "kind": "uniform", "target": -0.05, "rho": [0.05, 0.05, 0.1], "reps": 2000, "D": 120, "S": 48, "theta_true_mean": -0.05, "pce_median": 0.07, "rho_name": "TRUE"}
{"cov": 0.973, "exERT": 0.926, "exERT_false": 0.0, "T2": 0.0, "kind": "uniform", "target": -0.1, "rho": [0.05, 0.05, 0.1], "reps": 2000, "D": 120, "S": 48, "theta_true_mean": -0.1, "pce_median": 0.07, "rho_name": "TRUE"}
```

Key lines: A1 (θ = 0.0315, GO design, θ_PCE = 0.08) retired coverage 0.8885, false ERT exclusion 0.0742, false economic rejection 0.3204 → repaired 1.0 / 0 / 0; A2 (θ = 0.0852) retired coverage 0.8632, false LARGE exclusion 0.1126 → repaired 1.0 / 0; adversarial core class coverage 0.9705–0.993, false ERT exclusion 0.019–0.0295. Regression: tail-free run B row 1 and run C seed 11 reproduce bit-for-bit.

## 7. Checkpoint strategy for long Quant missions (standing practice)

- **Durable state lives in git, never in chat or the scratchpad.** The container and scratchpad are ephemeral; anything not pushed is lost with them.
- **One commit per completed phase**, prefixed `checkpoint(<area>):`, pushed immediately, with `REMOTE_HEAD == LOCAL_HEAD` verified each time.
- **One resume file per mission** (this pattern): authority chain with SHAs, phase ledger, frozen decisions, targeted reading list, next exact command, evidence snapshot.
- **Long computations write their raw output into the repo** (or into the resume file) before any analysis depends on them.
- **Split multi-step shell actions** (edit / commit / push / verify) into separate calls, so an interruption leaves an unambiguous state that the ledger can describe.
- **On resume, verify before acting:** SHAs, ancestry, clean tree, local-vs-remote difference; then continue at the first non-DONE phase.
