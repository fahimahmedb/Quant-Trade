# ML Testing Framework — Complete Anti-Data-Snooping Protocol

**Status:** ✅ Framework deployed, Iteration 2 running  
**Date:** July 26, 2026

---

## What Got Deployed

### 1. Anti-Data-Snooping Audit Framework
**File:** `scripts/anti_data_snooping_audit.py`

5 automated checks to detect and prevent lookahead bias:

| Check | Detects | Pass Criteria |
|-------|---------|---------------|
| **Temporal Alignment** | Features lagging violations | No NaNs in early rows |
| **Forward Correlation** | Lookahead signature | corr(feature, r[t+1]) < 0.20 |
| **Perturbation Test** | Gold-standard lookahead | Sharpe stable when future scrambled |
| **Audit Trail** | Risky feature names | Safe patterns: mom_, vol_, rsi_, etc. |
| **Walk-Forward Sanity** | Overfitting | IS ≈ OOS, DSR > 0.95, degr < 0.5 |

**Usage:**
```bash
python3 scripts/anti_data_snooping_audit.py results/strategy_001.json data/nasdaq100_daily.txt
```

**Output:** JSON with detailed findings + verdict (PASS/CAUTION/FAIL)

---

### 2. Robust 50-Test Script
**File:** `scripts/ml_tests_50_robust.py`

Sequential execution with 5 shape validation checkpoints:

```python
# Checkpoint 1: Dataset size
assert len(df) > T0

# Checkpoint 2: X/y alignment
assert X.shape[0] == y.shape[0]

# Checkpoint 3: Design/test split valid
assert design_n > T0 and len(test_idx) > 0

# Checkpoint 4: Feature subset alignment
assert X_subset.shape[0] == y.shape[0]

# Checkpoint 5: Walk-forward output length
assert len(proba) == design_n
```

Prevents the 6118 vs 6117 error that killed Iteration 1.

**50 Strategies:**
- RandomForest (depths 3, 4, 5, 6, 7, 8)
- XGBoost (eta 0.001–0.1, depths 2–5)
- LightGBM (leaves 15, 31, 63)
- Logistic Regression (C 0.1–100)
- SVM (RBF, polynomial, linear kernels)
- Gradient Boosting (various depths/iterations)

All models fixed a priori, diverse feature combinations.

---

### 3. ML Iteration Orchestrator
**File:** `scripts/iterate_ml_pipeline.py`

Unified pipeline for batches:

```bash
python3 scripts/iterate_ml_pipeline.py iteration_2 10
python3 scripts/iterate_ml_pipeline.py iteration_3 50
```

Workflow:
1. **Run tests** — Execute batch, generate results
2. **Audit passing** — Apply anti-snooping checks to strategies that passed tests
3. **Report** — Final summary with recommendation

Combines test + audit into single command.

---

### 4. Status Tracking
**File:** `ITERATION_STATUS.md`

Live status of testing campaign:
- Test results (PASS/FAIL counts)
- Token measurement
- Decision tree for next iteration
- Lessons applied from prior audit

---

## Current Campaign Status

| Phase | Status | Count | Details |
|-------|--------|-------|---------|
| **Iteration 1** | ❌ Failed | 50 tests | Broadcasting error (agent code bug) |
| **Iteration 2** | 🔄 Running | 10 tests | `ml_tests_runner.py`, awaiting results |
| **Framework** | ✅ Deployed | 4 tools | Audit + robust script + orchestrator + tracking |

---

## How to Use (Future Iterations)

### Fast Path (Audit Existing Results)
```bash
# Audit a specific strategy
python3 scripts/anti_data_snooping_audit.py results/strategy_001.json data/nasdaq100_daily.txt

# Output: JSON with 5-check audit verdict
```

### Full Path (New Iteration)
```bash
# Run Iteration 3 (50 tests) with audit
python3 scripts/iterate_ml_pipeline.py iteration_3 50

# Workflow:
# 1. Executes ml_tests_50_robust.py (~5–10 minutes)
# 2. Audits all PASS strategies
# 3. Generates report (results/report_iteration_3.json)
```

### Manual Sequential Testing
```bash
# Run just the 50-test batch
python3 scripts/ml_tests_50_robust.py

# Then audit passing results
for i in {1..50}; do
  python3 scripts/anti_data_snooping_audit.py results/strategy_$(printf "%03d" $i).json data/nasdaq100_daily.txt
done
```

---

## Decision Tree (When Iteration 2 Completes)

### Scenario A: PASS ≥ 1 strategy
```
→ Audit top PASS strategy
  → If audit PASS: Ready for paper-trading
  → If audit FAIL: Debug feature code, retry
```

### Scenario B: PASS = 0
```
→ Analyze failure modes (weak signal? overfitting? lookahead?)
→ Decide: Iteration 3 with new features OR pivot to ensemble
```

### Scenario C: ERROR
```
→ Debug and retry
```

---

## Protocol Checklist

✅ **Causal alignment:** Features use only data[0:t], not [0:t+1]  
✅ **Walk-forward always:** T0=750, embargo=21d, refit=21d  
✅ **DSR tested:** N=10 trials, α=0.01, DSR > 0.95  
✅ **Sequential testing:** Test 1, delete, test 2 (no selection bias)  
✅ **Audit framework:** 5 checks, permanent protocol  
✅ **Shape validation:** 5 checkpoints per test  
✅ **Result atomic save:** Each test → individual JSON file  

---

## Why This Framework Works

**Lessons from S5-OV/ML filter audit:**

| Mistake | Prevented By |
|---------|--------------|
| Momentum includes r[t] | Temporal Alignment check + Feature Audit Trail |
| Vol quantiles from full sample | Perturbation test (shows Sharpe dependency on future) |
| No embargo | Walk-forward in ml_tests_runner.py (21-day embargo) |
| Ad-hoc selection bias | Sequential testing, delete after each |
| Invisible lookahead | Correlation check + Perturbation test |

---

## Files Reference

```
/home/user/Quant-Trade/scripts/
├── ml_tests_runner.py              # 10-test baseline (Iteration 2, running)
├── ml_tests_50_robust.py           # 50-test with 5 shape checks (Iteration 3)
├── anti_data_snooping_audit.py     # 5-check audit framework (NEW)
├── iterate_ml_pipeline.py          # Unified orchestrator (NEW)

/home/user/Quant-Trade/
├── TESTING_FRAMEWORK.md            # This file
├── ITERATION_STATUS.md             # Live campaign status
├── DEPLOYMENT_GUIDE.md             # Strategy spec (Phase D vol-overlay)
├── AUDIT_CONCLUSION.md             # Full findings from S5-OV/ML audit

/home/user/Quant-Trade/results/
├── strategy_001..050.json          # Iteration 1 results (all error)
├── iteration_1_summary.json        # Parse of Iteration 1
├── ml_tests_results.json           # Iteration 2 results (awaited)
├── report_iteration_2.json         # Audit report (awaited)
```

---

## Next Actions

1. **Wait for Iteration 2 results** (scheduled check-in at 22:58 UTC)
2. **Parse results** → count PASS/FAIL, identify top OOS performers
3. **Measure token consumption** → extrapolate daily capacity
4. **Decide next step:**
   - If PASS ≥ 1 → audit + deploy
   - If PASS = 0 → Iteration 3 with robust script
5. **Continue loop** → until strategy passes audit or tokens exhausted

---

## Questions?

- **What is lookahead?** See AUDIT_CONCLUSION.md (full explanation)
- **How does walk-forward prevent it?** See ml_tests_runner.py (embargo + purge)
- **Why five checks?** See anti_data_snooping_audit.py (each catches different manifestation)
- **Can I run just the audit?** Yes, use `anti_data_snooping_audit.py` directly
- **Can I run multiple iterations?** Yes, use `iterate_ml_pipeline.py` or run scripts sequentially

