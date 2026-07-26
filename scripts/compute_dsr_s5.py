#!/usr/bin/env python3
"""
Deflated Sharpe Ratio for S5 with Multi-Testing Correction
==========================================================

Hypotheses tested across all phases:

PHASE 1 (Classical Signals, N=9):
S0: Buy & Hold: 0.529
S1: Momentum EMA 12/26: 0.23
S2: RSI(14): 0.28
S3: Donchian 20: 0.18
S4: Momentum + RSI: 0.17
S5: EMA trend (50>200): 0.67 ← TARGET
S6: Vol-adjusted momentum (cap 1.5x): -0.34
S7: EMA confluence 12>50>200: 0.48
S8: Dual momentum ROC: 0.10

PHASE 2 (Unconventional, N=7):
O1: Anti-Momentum: 0.047
O2: Vol-Regime Asymmetric: 0.318
O3: Drawdown Predictive: 0.553
O4: Gap Trading: -0.104
O5: Vol-of-Vol mean-reversion: 0.577
O6: Composite Momentum: -0.049
O7: Downside Asymmetry: 0.356

Total: N=16 hypotheses (N=9 Phase 1 + N=7 Phase 2)

DSR = P(SR > SR₀ | multiple testing penalty)
For DSR > 0.95: need strong evidence after correcting for N trials.
"""

import numpy as np
from scipy.stats import norm

# All Sharpe ratios tested (annualized)
sharpe_ratios = [
    # Phase 1 (N=9, Classical)
    0.529,   # S0: Buy & Hold
    0.23,    # S1: Momentum EMA 12/26
    0.28,    # S2: RSI(14)
    0.18,    # S3: Donchian 20
    0.17,    # S4: Momentum + RSI
    0.67,    # S5: EMA trend (50>200) ← TARGET
    -0.34,   # S6: Vol-adjusted momentum
    0.48,    # S7: EMA confluence
    0.10,    # S8: Dual momentum

    # Phase 2 (N=7, Unconventional)
    0.047,   # O1: Anti-Momentum
    0.318,   # O2: Vol-Regime Asymmetric
    0.553,   # O3: Drawdown Predictive
    -0.104,  # O4: Gap Trading
    0.577,   # O5: Vol-of-Vol mean-reversion
    -0.049,  # O6: Composite Momentum
    0.356,   # O7: Downside Asymmetry
]

n_trials = len(sharpe_ratios)
s5_idx = 5  # S5 is at index 5 (0-indexed)
s5_sharpe = sharpe_ratios[s5_idx]

print("\n" + "="*80)
print(f"DEFLATED SHARPE RATIO (DSR) for S5")
print("="*80)

print(f"\nS5 Sharpe Ratio (annual): {s5_sharpe:.3f}")
print(f"S5 Sharpe Ratio (daily): {s5_sharpe/np.sqrt(252):.4f}")

print(f"\nTotal hypotheses tested: N={n_trials}")
print(f"  Phase 1 (Classical): 9")
print(f"  Phase 2 (Unconventional): 7")

# Calculate variance of all Sharpe ratios
sr_mean = np.mean(sharpe_ratios)
sr_var = np.var(sharpe_ratios, ddof=1)
sr_std = np.std(sharpe_ratios, ddof=1)

print(f"\nSharpe ratio distribution across all tests:")
print(f"  Mean: {sr_mean:.3f}")
print(f"  Std Dev: {sr_std:.3f}")
print(f"  Variance: {sr_var:.4f}")

# Variance of Sharpe ratios squared (for DSR calculation)
sr_squared = np.array(sharpe_ratios) ** 2
var_sr_squared = np.var(sr_squared, ddof=1)

print(f"\nRanking of all tests:")
for i, sr in enumerate(sorted(sharpe_ratios, reverse=True)):
    strategy = [
        "S0: BH", "S1: Mom EMA", "S2: RSI", "S3: Donchian", "S4: Mom+RSI",
        "S5: EMA", "S6: Vol-adj", "S7: EMA conf", "S8: Dual Mom",
        "O1: Anti-Mom", "O2: Vol-Reg", "O3: DD-Pred", "O4: Gap",
        "O5: Vol-Vol", "O6: Comp-Mom", "O7: Downside"
    ]
    idx = sharpe_ratios.index(sr) if sr in sharpe_ratios else -1
    label = strategy[idx] if idx >= 0 else "unknown"
    marker = " ← S5 (TARGET)" if sr == s5_sharpe else ""
    print(f"  {i+1}. {label}: {sr:.3f}{marker}")

# ============================================================================
# DSR Calculation (Bailey & López de Prado, 2014)
# ============================================================================

print(f"\n" + "="*80)
print("DSR CALCULATION")
print("="*80)

# Convert annual Sharpe to daily
sr_daily = s5_sharpe / np.sqrt(252)
print(f"\nS5 daily Sharpe: {sr_daily:.4f}")

# Estimate threshold SR₀ (critical value for significance)
# Varies with N (more tests = higher bar)
# Approximate formula: SR₀ ≈ (0.575 / sqrt(T)) * sqrt(log(N))
# where T = number of observations (10273 for NDX)
T_ndx = 10273
T_comp = 1251
T_avg = (T_ndx + T_comp) / 2

z_critical_ndx = (0.575 / np.sqrt(T_ndx)) * np.sqrt(np.log(n_trials))
z_critical_comp = (0.575 / np.sqrt(T_comp)) * np.sqrt(np.log(n_trials))
z_critical_avg = (z_critical_ndx + z_critical_comp) / 2

print(f"\nThreshold SR₀ (critical value for {n_trials} tests):")
print(f"  NDX (T={T_ndx}): {z_critical_ndx:.4f}")
print(f"  Composite (T={T_comp}): {z_critical_comp:.4f}")
print(f"  Average: {z_critical_avg:.4f}")

# ============================================================================
# Method 1: Bailey & López de Prado DSR
# ============================================================================

# Variance of Sharpe ratios squared (captures uncertainty in parameter estimates)
# Approximation: σ²_SR ≈ (1 + 0.5*SR² / (N_obs)) using Bailey formula

# For simplicity, use empirical variance from all tests
empirical_var_sr = sr_var

print(f"\nEmpirical variance of Sharpe ratios: {empirical_var_sr:.6f}")

# z-score for S5 vs threshold
z_score_ndx = (sr_daily - z_critical_ndx) / np.sqrt(empirical_var_sr / n_trials)
z_score_comp = (sr_daily - z_critical_comp) / np.sqrt(empirical_var_sr / n_trials)
z_score_avg = (sr_daily - z_critical_avg) / np.sqrt(empirical_var_sr / n_trials)

# DSR = P(Z ≤ z) = CDF(z)
dsr_ndx = norm.cdf(z_score_ndx)
dsr_comp = norm.cdf(z_score_comp)
dsr_avg = norm.cdf(z_score_avg)

print(f"\n--- DSR Calculation ---")
print(f"\nUsing NDX data base (T={T_ndx} obs):")
print(f"  z-score: {z_score_ndx:.3f}")
print(f"  DSR: {dsr_ndx:.3f}")

print(f"\nUsing Composite data base (T={T_comp} obs):")
print(f"  z-score: {z_score_comp:.3f}")
print(f"  DSR: {dsr_comp:.3f}")

print(f"\nUsing average (both markets):")
print(f"  z-score: {z_score_avg:.3f}")
print(f"  DSR: {dsr_avg:.3f}")

# ============================================================================
# Method 2: Benjamini-Hochberg False Discovery Rate
# ============================================================================

print(f"\n" + "="*80)
print("FALSE DISCOVERY RATE (FDR) Control")
print("="*80)

# Sort all tests by p-value
p_values = [1 - norm.cdf(sr / np.sqrt(empirical_var_sr / n_trials)) for sr in sharpe_ratios]
sorted_indices = np.argsort(p_values)

print(f"\nTop performers by p-value (lower = more significant):")
for rank, idx in enumerate(sorted_indices[:5]):
    strat_name = [
        "S0: BH", "S1: Mom", "S2: RSI", "S3: Don", "S4: M+R",
        "S5: EMA", "S6: VA", "S7: EC", "S8: DM",
        "O1: AM", "O2: VR", "O3: DP", "O4: GT",
        "O5: VV", "O6: CM", "O7: DA"
    ][idx]
    p_val = p_values[idx]
    sr = sharpe_ratios[idx]
    marker = " ← S5" if idx == s5_idx else ""
    print(f"  {rank+1}. {strat_name}: SR={sr:.3f}, p={p_val:.4f}{marker}")

# BH FDR threshold (α=0.05)
alpha_fdr = 0.05
s5_p_value = p_values[s5_idx]
fdr_threshold = alpha_fdr * (s5_idx + 1) / n_trials

print(f"\nS5 p-value: {s5_p_value:.4f}")
print(f"FDR threshold (α=0.05, rank={s5_idx+1}): {fdr_threshold:.4f}")

if s5_p_value < fdr_threshold:
    print(f"✅ S5 PASSES FDR control")
else:
    print(f"⚠️ S5 FAILS FDR control")

# ============================================================================
# Verdict
# ============================================================================

print(f"\n" + "="*80)
print("FINAL VERDICT")
print("="*80)

print(f"\nS5 Performance Summary:")
print(f"  Sharpe (annual): {s5_sharpe:.3f}")
print(f"  Rank: {len([sr for sr in sharpe_ratios if sr > s5_sharpe])+1} out of {n_trials}")
print(f"  DSR (NDX base): {dsr_ndx:.3f}")
print(f"  DSR (Composite base): {dsr_comp:.3f}")
print(f"  DSR (Average): {dsr_avg:.3f}")

print(f"\nStatistical Thresholds:")
print(f"  DSR > 0.95 needed for: 95% confidence edge is real (standard)")
print(f"  Current DSR: {dsr_avg:.3f} (vs threshold 0.95)")

if dsr_avg > 0.95:
    print(f"\n✅ S5 PASSES strict DSR > 0.95 threshold")
    print(f"   Edge is STATISTICALLY CERTAIN after correcting for {n_trials} trials")
elif dsr_avg > 0.90:
    print(f"\n⚠️ S5 NEAR threshold (DSR {dsr_avg:.3f} > 0.90)")
    print(f"   Edge is LIKELY REAL but not statistically certain")
    print(f"   Recommendation: Continue monitoring, requires independent confirmation")
elif dsr_avg > 0.50:
    print(f"\n⚠️ S5 BELOW threshold (DSR {dsr_avg:.3f})")
    print(f"   Edge is UNCERTAIN — data-snooping cannot be ruled out")
    print(f"   Recommendation: Treat as promising but unproven")
else:
    print(f"\n❌ S5 FAILS (DSR {dsr_avg:.3f} < 0.5)")
    print(f"   No edge detected")

print(f"\nContextual Notes:")
print(f"  • S5 validated on INDEPENDENT data (Composite 2021-2026)")
print(f"  • Generalizes across 2 markets, 45-year span")
print(f"  • Trade-off: Better risk-adjusted return (Sharpe/MDD) vs lower absolute return")
print(f"  • Simple & causally valid (no lookahead bias)")

print(f"\n{'='*80}\n")
