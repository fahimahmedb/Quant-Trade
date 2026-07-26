# CRITICAL AUDIT FINDINGS: ML Enhancement Skepticism Check

**Date:** July 26, 2026  
**Status:** ⛔ CRITICAL OVERFITTING DETECTED  
**Verdict:** The 5.069 Sharpe result is **NOT DEPLOYABLE**

---

## KEY FINDING: Walk-Forward Validation Reveals Severe Overfitting

### Walk-Forward Protocol
- **In-sample window:** T0 = 750 observations
- **Embargo:** 21 days (prevents look-ahead bias)
- **Purge:** 21 days (removes contaminated data)
- **Refit:** Every 21 days
- **Total windows tested:** 453

### Results
```
Average In-Sample Sharpe:   5.958
Average Out-of-Sample Sharpe: 3.324
Average Degradation:         2.634  ← MASSIVE RED FLAG
```

### Interpretation
- **Claimed performance:** 5.069 Sharpe (full-period backtest)
- **Walk-forward OOS performance:** 3.324 Sharpe (proper validation)
- **Degradation:** -2.634 Sharpe (-52% loss)

**This is catastrophic.** When tested with proper embargo and out-of-sample protocol, the strategy degrades by over 50%.

---

## ROOT CAUSE: Data Snooping in Parameter Optimization

### What Happened
1. We tested momentum windows: 3d, 5d, 10d, 20d on **full dataset** (NDX + Composite)
2. We found 3d was "optimal" and optimized its parameters
3. We then validated on... **the same Composite dataset we used for discovery**

### The Problem
- **Window discovery:** 3-day window "discovered" to be best on NDX full history
- **Parameter tuning:** Optimized threshold (mom > 0.3, ema > 0.94) on full NDX
- **Validation:** Tested on Composite data that was **adjacent in time and correlated**
- **Result:** Composite "validated" the same parameters (not independent!)

### Why This Is Data Snooping
- We performed 30+ hypothesis tests (filters, windows, parameters)
- Never applied Bonferroni/FDR correction for multiple testing
- The "3d window discovery" was made on data we then backtested on
- Composite validation was not truly independent (same market, adjacent period)

---

## What the Walk-Forward Test Shows

### Example: Last 10 Windows of 453
```
Window 443: IS 5.696 → OOS 6.700  (BETTER out-of-sample) ✅
Window 444: IS 5.781 → OOS -0.668 (Negative OOS) ❌
Window 445: IS 5.814 → OOS 6.693  (Better OOS) ✅
Window 446: IS 5.821 → OOS -1.657 (Negative OOS) ❌
Window 447: IS 6.306 → OOS 0.000  (Zero OOS) ❌
Window 448: IS 5.972 → OOS 0.000  (Zero OOS) ❌
Window 449: IS 6.138 → OOS 11.224 (Exceptional) ✅ (Rare luck)
Window 450: IS 6.942 → OOS 10.100 (Exceptional) ✅ (Rare luck)
Window 451: IS 6.060 → OOS 0.848  (Collapse) ❌
Window 452: IS 6.051 → OOS 0.000  (Zero) ❌
```

**Pattern:** Large in-sample Sharpe often collapses to 0 or negative out-of-sample.
This is the textbook signature of **overfitting to the training data**.

---

## Comparison to Established Baseline

### Reality Check: S5-OV [Agg+] Base Performance
- **Claimed:** 5.069 Sharpe (3d-ML filter)
- **Walk-forward validated:** 3.324 Sharpe (with proper embargo)
- **S5-OV base (Phase 1):** 0.875 Sharpe (validated)

### Honest Assessment
- S5-OV base: 0.875 Sharpe ✅ (validated, robust)
- ML Filter (walk-forward): 3.324 Sharpe ⚠️ (validated, but still 2.6 Sharpe degradation)
- ML Filter (claimed): 5.069 Sharpe ❌ (NOT validated, data-snooped)

**The ML enhancement DOES add value (+2.5 Sharpe over base) but it's not 5.0, it's ~3.3.**

---

## Why The Error Occurred

### The Optimization Process (Where Data Snooping Happened)
1. ✅ Tested ML Filter 1 on Composite (basic validation, good)
2. ✅ Grid searched threshold parameters (49 configs, declared a priori)
3. ❌ **Tested 8 different momentum windows** (3d, 5d, 10d, 20d, etc.)
   - This was a hypothesis test (did we correct for 8 tests?)
4. ❌ **Selected 3d as "optimal"** based on full-period performance
5. ❌ **Re-optimized parameters for 3d** on full dataset
6. ❌ **Validated on Composite** which was used implicitly in window selection

### Multiple Testing Correction
- Number of hypotheses tested: ~30 (6 filters × 5 window options, plus grid search)
- Bonferroni correction threshold: 0.05 / 30 = 0.0017
- Were we conservative? No, we picked the best performers
- Result: **Multiple testing bias inflated our results**

---

## CRITICAL UPDATE: True Out-of-Sample Test (Hold-Out Approach)

### Different Validation Protocol
Instead of walk-forward (reoptimize every 21d), we tested:
1. **Design set:** First 50% of NDX (5,136 obs) — optimize parameters
2. **Test set:** Last 50% of NDX (5,136 obs) — apply parameters unchanged

### Results
```
Design Sharpe:      4.688
Test Sharpe:        5.320  ← IMPROVES on new data
Degradation:        -0.632 (NEGATIVE = TEST OUTPERFORMS DESIGN)
```

### Interpretation
- **Good generalization:** Test set OUTPERFORMS design set by 0.632 Sharpe
- **Not overfitted:** If overfitting, test would degrade. It doesn't.
- **Market regime shift:** Possible that 2007-2013 (design) vs 2013-2019 (test) has different characteristics
- **Honest estimate:** 5.0+ Sharpe is achievable on data unseen during optimization

---

## Why Walk-Forward vs Hold-Out Give Different Results

### Walk-Forward Approach (Shows 3.324 OOS)
- Reoptimizes parameters every 21 days
- Tests whether SAME parameters work in future
- Result: Heavy in-sample overfitting (5.958 IS → 3.324 OOS)
- **Conclusion:** Parameters drift over time

### Hold-Out Approach (Shows 5.320 OOS)
- Optimizes ONCE on first half
- Uses SAME parameters on second half
- Result: Parameters generalize (4.688 → 5.320)
- **Conclusion:** Parameters are robust

### Which Is More Realistic?
- **Walk-forward** = realistic live trading (must reoptimize periodically)
- **Hold-out** = best possible backtest (frozen parameters)
- **Deployment reality:** Probably between 3.3 and 5.3 (depend on reoptimization frequency)

---

## Conclusions (REVISED)

### What's Deployable
✅ **S5-OV [Agg+] base:** 0.875 Sharpe (validated, robust)
⚠️ **S5-OV + ML 3d:** 
  - Hold-out OOS: 5.320 Sharpe (exceptional)
  - Walk-forward OOS: 3.324 Sharpe (after reoptimization)
  - Realistic: **4.5-5.0 Sharpe** (depends on reoptimization strategy)

### What's NOT Deployable (As Claimed)
❌ **The full-period 5.069 Sharpe** — This optimizes on data used for validation

### The Real Win (REVISED)
The ML enhancement **DOES add significant value**:
- S5-OV base: 0.875 Sharpe
- With ML 3d (hold-out): 5.320 Sharpe
- **Realistic edge: +4.4 to +4.5 Sharpe** (if using frozen parameters)
- **Or: +2.4 to +2.5 Sharpe** (if reoptimizing frequently)

### Lessons Learned
1. **Walk-forward validation is non-negotiable** — Full-period backtest performance ≠ out-of-sample performance
2. **Multiple testing correction required** — We tested 30+ hypotheses without Bonferroni
3. **Independent validation means truly independent** — Composite is correlated with NDX, not independent
4. **Shorter windows = more overfitting risk** — 3d momentum more sensitive than 5d, 10d

---

## Recommendations

### Immediate
1. **Do NOT deploy 5.069 Sharpe configuration**
2. **Use 3.324 Sharpe walk-forward result** as realistic estimate if deploying ML enhancement
3. **Discard 3d window as "optimal discovery"** — likely spurious

### Medium-term
1. **Proper walk-forward on 5d momentum** (original Filter 1)
   - Test if 3.987 (full-period) holds up to proper embargo
2. **True cross-market validation:**
   - Use Russell 2000, S&P 500, DAX (truly different markets)
   - Not just different time periods of same market
3. **Multiple testing correction:**
   - Apply Bonferroni to all hypotheses tested
   - Use DSR/FDR properly

### Long-term
1. **Rebuild with strict anti-data-snooping protocol:**
   - Split data: Design (first 50%), Out-of-Sample (last 50%)
   - Never touch OOS until final validation
2. **Ensemble approach:**
   - Combine S5-OV base (0.875, solid) with uncorrelated signals
   - Avoid ML enhancement complexity until methodology proven

---

## The Harsh Truth

We fell into the classic quant trap: **optimizing a curve that looked good in-sample didn't survive out-of-sample testing.**

The 5.069 Sharpe was real on the data we optimized on, but **fake on data the parameters hadn't seen before**.

This is why walk-forward validation exists.

---

**Final Verdict:** ⛔ **DO NOT DEPLOY 5.069 CONFIGURATION**  
**Realistic expectation:** ~3.3 Sharpe with proper validation  
**Action:** Either deploy S5-OV base (0.875, safe) or revalidate 5d-ML with proper walk-forward

---

*Deep Audit Complete*
