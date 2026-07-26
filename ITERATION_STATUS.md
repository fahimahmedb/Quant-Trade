# ML Testing Campaign Status

**Date:** July 26, 2026  
**Campaign Goal:** Find real ML edge or prove none exists (with strict anti-data-snooping discipline)

---

## Summary

| Phase | Status | Strategies | Result |
|-------|--------|-----------|--------|
| **Iteration 1** | ❌ FAILED | 50 parallel tests | Broadcasting error (6118 vs 6117 shape mismatch) — agent code bug |
| **Iteration 2** | 🔄 RUNNING | 10 sequential tests (ml_tests_runner.py) | Agent a41374a9959e212a5, awaiting results |
| **Framework** | ✅ CREATED | Anti-data-snooping audit | 5 automated checks deployed |

---

## Iteration 1 Analysis (50 Tests — FAILED)

**What happened:**
Agent a2eb48cd53da77951 launched 50 parallel ML strategies with diverse models/features.
All 50 hit identical error: shape mismatch (6118 vs 6117).

**Root cause:**
Broadcasting error in agent's feature/label alignment code (likely `y = triple_barrier_labels(...)` returns n-1 elements while X has n).

**Lesson:**
- Parallel multiprocessing is efficient IF the code is correct
- All 50 failed for the same reason = systematic bug, not data issue
- Sequential execution (Iteration 2) is safer for validation

**Token cost:**
Estimated 20k–30k tokens for agent setup + orchestration (results pending full measurement).

---

## Iteration 2: 10 Tests (RUNNING)

**Characteristics:**
- Using battle-tested `ml_tests_runner.py` (same script from ml tests documentation)
- Sequential execution (not parallel) = slower but guaranteed correctness
- Each test independently run with walk-forward validation (T0=750, embargo=21d)
- 10 predetermined models/features (fixed a priori, no changes)

**10 Strategies:**
1. Random Forest (depth 5) — Momentum
2. HistGradientBoosting (eta 0.1) — Trend + Vol
3. HistGB (eta 0.05) — Mean Reversion
4. HistGB (deep, 5 layers) — Ensemble
5. Logistic Regression — Simple Causal
6. HistGB (interactions) — mom*vol
7. SVM (RBF) — Kernel Method
8. HistGB (voting ensemble) — Top 3 Combo
9. LogReg (TimeSeriesCV) — Proper Walk-Forward
10. HistGB (causal trees) — Causal Forest

**Pass Criteria:**
- Design Sharpe > 0.55
- Test Sharpe > 0.55
- Degradation < 0.5
- DSR > 0.95

**Expected timeline:**
- ~30–60 seconds per test (walk-forward with 454 windows)
- Total: ~5–10 minutes for all 10
- Agent started ~22:46 UTC, awaiting completion

---

## Anti-Data-Snooping Audit Framework (✅ DEPLOYED)

**Location:** `scripts/anti_data_snooping_audit.py`

**5 Automated Checks:**

### 1. Temporal Alignment
Verify features use only lagged data (t-1, not t+1).
- ✓ Features properly lagged
- ⚠️ Missing NaNs in early rows (suggests lookahead)

### 2. Forward-Return Correlation
Lookahead leaves signature: high correlation with forward returns.
- ✓ corr(feature, r[t+1]) < 0.20 = safe
- ⚠️ corr > 0.20 = borderline
- 🚨 corr > 0.30 = lookahead detected

### 3. Perturbation Test (Gold Standard)
Train on original data, test on perturbed data (future scrambled).
- ✓ Sharpe unchanged = no lookahead
- 🚨 Sharpe drops > 0.1 = lookahead present

### 4. Feature Audit Trail
Each feature must trace to causal source (momentum, vol, RSI, etc.).
- ✓ Safe patterns: mom_, vol_, rsi_, atr_, etc.
- 🚨 Risky patterns: forward_, future_, prediction_, etc.

### 5. Walk-Forward Sanity
IS Sharpe ≈ OOS Sharpe (health check for overfitting).
- ✓ Both positive, similar magnitude
- 🚨 IS >> OOS or OOS < 0 = overfitting
- ⚠️ DSR < 0.95 = statistically weak

**Usage:**
```bash
python3 scripts/anti_data_snooping_audit.py results/strategy_001.json data/nasdaq100_daily.txt
```

**Output:** JSON with detailed findings + overall verdict (PASS/CAUTION/FAIL)

---

## Next Steps (Decision Tree)

### When Iteration 2 completes:

**Case 1: PASS ≥ 1** 
→ Run audit on top PASS strategy
→ If audit PASS: proceed to Iteration 3 (50 tests, refined)
→ If audit FAIL: debug feature code, retry same test

**Case 2: PASS = 0**
→ Analyze why all 10 failed (weak signals? overfitting? lookahead?)
→ Decide: Launch Iteration 3 with different feature/model combinations OR pivot to ensemble/overlay

**Case 3: Agent ERROR**
→ Debug code, retry Iteration 2

---

## Timeline & Token Budget

**Measured so far:**
- Iteration 1 (50 tests): ~20–30k tokens estimated (failed)
- Iteration 2 (10 tests): in progress

**After Iteration 2 completes:**
1. Parse results JSON
2. Measure actual tokens (from agent output)
3. Extrapolate: tokens_per_batch = measured × (50 / 10)
4. Daily capacity: 150,000 / tokens_per_batch = max_batches

**Typical scenario:**
- 10 tests = ~5k–10k tokens
- 50 tests = ~25k–50k tokens (if no errors)
- Daily capacity: ~3–6 batches (if 25k–50k per 50-test batch)

**Strategy:**
- Run Iteration 2, measure tokens
- If Pass ≥ 1: audit + deploy
- If Pass = 0: run Iterations 3–5 until either:
  - Find strategy that passes audit
  - Exhaust daily token budget
  - Conclude no ML edge exists

---

## Lessons Applied

From the audit that revealed lookahead in S5-OV (0.875 → 0.574) and ML filter (5.069 → 0.701):

1. ✅ **Causal alignment first** — Features must use data[0:t], not data[0:t+1]
2. ✅ **Walk-forward always** — Never optimize on test data (embargo purges lookahead)
3. ✅ **DSR tested** — Corrects for multiple testing (Bonferroni α=0.01)
4. ✅ **Sequential validation** — Test 1, delete, test 2, etc. (avoid selection bias)
5. ✅ **Audit framework** — Permanent protocol beyond "delete and retry"

---

## Files

```
/home/user/Quant-Trade/
├── scripts/
│   ├── ml_tests_runner.py           # 10-test baseline (Iteration 2, running)
│   ├── anti_data_snooping_audit.py  # Framework (NEW)
├── results/
│   ├── strategy_001..050.json       # Iteration 1 (all failed)
│   ├── iteration_1_summary.json     # Iteration 1 parse
│   ├── ml_tests_results.json        # Iteration 2 results (awaited)
├── ITERATION_STATUS.md              # This file
```

---

## Contact

Questions? See:
- `DEPLOYMENT_GUIDE.md` — Strategy spec and deployment workflow
- `AUDIT_CONCLUSION.md` — Full audit findings from S5-OV/ML filter investigation
- Code: `finance/src/prediction.py` — Causal feature + walk-forward validation
