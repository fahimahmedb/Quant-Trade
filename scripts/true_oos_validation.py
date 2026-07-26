#!/usr/bin/env python3
"""
TRUE OUT-OF-SAMPLE VALIDATION
==============================
Strictest possible test: Never touch test set during optimization

Protocol:
1. Split NDX 50/50: Design (first 5136 obs) | Test (last 5136 obs)
2. Discover parameters ONLY on Design set
3. Apply to Test set WITHOUT any re-optimization
4. Report honest performance
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "finance" / "src"))
from data_loader import load_ohlc, log_returns_pct

def calc_sharpe(returns, ann=252):
    if len(returns) < 2: return 0.0
    mu, sigma = np.mean(returns), np.std(returns, ddof=1)
    return float(mu / sigma * np.sqrt(ann)) if sigma > 0 else 0.0

def calc_mdd(returns_pct):
    if len(returns_pct) == 0: return np.nan
    cumsum_pct = np.cumsum(returns_pct)
    equity = np.exp(cumsum_pct / 100.0)
    peak = np.maximum.accumulate(equity)
    return float(((equity - peak) / peak).min() * 100)

def backtest_simple(positions, returns, cost_bps=5):
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    return pnl - turn * (turn * (cost_bps / 1e4))

print("\n" + "="*80)
print("TRUE OUT-OF-SAMPLE VALIDATION")
print("="*80)
print("\nProtocol: Design on first 50% (NEVER touch second 50%)")

# Load full data
df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)
min_len = min(len(df), len(r))
df = df.iloc[:min_len].copy()
r = r.iloc[:min_len].copy()

# Split 50/50
split = len(df) // 2
df_design = df.iloc[:split].copy()
r_design = r.iloc[:split].copy()
df_test = df.iloc[split:].copy()
r_test = r.iloc[split:].copy()

print(f"\nDesign set: {len(df_design)} obs ({df_design.index[0]} to {df_design.index[-1]})")
print(f"Test set:   {len(df_test)} obs ({df_test.index[0]} to {df_test.index[-1]})")
print("\n" + "="*80)
print("STEP 1: OPTIMIZE PARAMETERS ON DESIGN SET ONLY")
print("="*80)

# Design set: Test different 3d momentum parameters
ema50_d = df_design['close'].ewm(span=50).mean().values
ema200_d = df_design['close'].ewm(span=200).mean().values
ema_trend_d = ema50_d / ema200_d

momentum_3d_d = np.array([np.sum(r_design.iloc[max(0,i-3):i+1]) if i > 0 else 0 for i in range(len(r_design))])

# S5-OV base
signal_base_d = np.where(ema50_d > ema200_d, 1.0, 0.0)
vol_20_d = pd.Series(r_design).rolling(20).std()
vol_low_d = vol_20_d.quantile(0.25)
vol_high_d = vol_20_d.quantile(0.75)

overlay_d = np.ones(len(signal_base_d))
for i in range(len(overlay_d)):
    if pd.notna(vol_20_d.iloc[i]):
        if vol_20_d.iloc[i] < vol_low_d:
            overlay_d[i] = 1.5
        elif vol_20_d.iloc[i] > vol_high_d:
            overlay_d[i] = 0.3

signal_s5ov_d = signal_base_d * overlay_d

# Grid search on design set
best_sharpe_d = -np.inf
best_config_d = (0, 0.96)

print("\nTesting 3d momentum thresholds on DESIGN SET:")
for mom_t in np.arange(-0.2, 0.5, 0.1):
    for ema_t in [0.94, 0.96, 0.98]:
        filter_d = (momentum_3d_d > mom_t) & (ema_trend_d > ema_t)
        signal_d = signal_s5ov_d * filter_d.astype(float)
        pnl_d = backtest_simple(signal_d, r_design.values)
        sharpe_d = calc_sharpe(pnl_d)

        if sharpe_d > best_sharpe_d:
            best_sharpe_d = sharpe_d
            best_config_d = (mom_t, ema_t)

print(f"\n✅ Optimal config found on DESIGN SET:")
print(f"   Parameters: momentum > {best_config_d[0]:+.1f} & ema > {best_config_d[1]:.2f}")
print(f"   Design Sharpe: {best_sharpe_d:.3f}")

# ============================================================================
print("\n" + "="*80)
print("STEP 2: APPLY SAME PARAMETERS TO TEST SET (NO RE-OPTIMIZATION)")
print("="*80)

ema50_t = df_test['close'].ewm(span=50).mean().values
ema200_t = df_test['close'].ewm(span=200).mean().values
ema_trend_t = ema50_t / ema200_t

momentum_3d_t = np.array([np.sum(r_test.iloc[max(0,i-3):i+1]) if i > 0 else 0 for i in range(len(r_test))])

signal_base_t = np.where(ema50_t > ema200_t, 1.0, 0.0)
vol_20_t = pd.Series(r_test).rolling(20).std()
vol_low_t = vol_20_t.quantile(0.25)
vol_high_t = vol_20_t.quantile(0.75)

overlay_t = np.ones(len(signal_base_t))
for i in range(len(overlay_t)):
    if pd.notna(vol_20_t.iloc[i]):
        if vol_20_t.iloc[i] < vol_low_t:
            overlay_t[i] = 1.5
        elif vol_20_t.iloc[i] > vol_high_t:
            overlay_t[i] = 0.3

signal_s5ov_t = signal_base_t * overlay_t

# Apply DESIGN parameters to TEST set (no changes)
filter_t = (momentum_3d_t > best_config_d[0]) & (ema_trend_t > best_config_d[1])
signal_t = signal_s5ov_t * filter_t.astype(float)
pnl_t = backtest_simple(signal_t, r_test.values)
sharpe_t = calc_sharpe(pnl_t)
mdd_t = calc_mdd(pnl_t)

print(f"\n📊 TEST SET RESULTS (using DESIGN parameters, NO re-optimization):")
print(f"   Test Sharpe: {sharpe_t:.3f}")
print(f"   Test MDD: {mdd_t:.1f}%")
print(f"   Exposure: {filter_t.mean()*100:.1f}%")

# ============================================================================
print("\n" + "="*80)
print("COMPARISON: CLAIMED vs HONEST PERFORMANCE")
print("="*80)

print(f"\n{'Metric':30s} | {'Claimed':>12} | {'Design/Test':>20} | {'Difference':>12}")
print("─" * 80)

print(f"{'Full-period (claimed)':30s} | {5.069:>12.3f} | {'-':>20} | {'-':>12}")
print(f"{'Walk-forward OOS':30s} | {3.324:>12.3f} | {'-':>20} | {'-':>12}")
print(f"{'Design/Test True OOS':30s} | {'N/A':>12} | {best_sharpe_d:.3f} / {sharpe_t:.3f} | {best_sharpe_d - sharpe_t:+12.3f}")

print(f"\n" + "="*80)
print("VERDICT")
print("="*80)

degradation = best_sharpe_d - sharpe_t

if degradation > 2.0:
    print(f"\n🚨 CRITICAL OVERFITTING: Design→Test degradation {degradation:.3f}")
    print(f"   Design set overfits by {(degradation/best_sharpe_d)*100:.1f}%")
    print(f"   Realistic performance: {sharpe_t:.3f} Sharpe")
elif degradation > 1.0:
    print(f"\n⚠️ SIGNIFICANT OVERFITTING: Design→Test degradation {degradation:.3f}")
    print(f"   Strategy underperforms in new regime")
    print(f"   Realistic performance: {sharpe_t:.3f} Sharpe")
elif degradation > 0.5:
    print(f"\n⚠️ MODERATE DEGRADATION: Design→Test degradation {degradation:.3f}")
    print(f"   Expected in time-series data, but concerning")
    print(f"   Realistic performance: {sharpe_t:.3f} Sharpe")
else:
    print(f"\n✅ GOOD GENERALIZATION: Design→Test degradation only {degradation:.3f}")
    print(f"   Strategy generalizes well to new data")
    print(f"   Realistic performance: {sharpe_t:.3f} Sharpe")

print(f"\nHONEST ESTIMATE:")
print(f"  - S5-OV base: 0.875 Sharpe")
print(f"  - ML 3d filter (design/test): {sharpe_t:.3f} Sharpe")
print(f"  - Improvement: {sharpe_t - 0.875:+.3f}")

print("\n✅ True OOS validation complete\n")
