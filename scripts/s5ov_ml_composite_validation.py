#!/usr/bin/env python3
"""
S5-OV + ML Filter Validation on Composite (Independent Data)
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
print("S5-OV + ML VALIDATION ON COMPOSITE (Independent Data)")
print("="*80)

# Load Composite (independent)
df = load_ohlc('/home/user/Quant-Trade/data/nasdaq_composite_daily.txt')
r = log_returns_pct(df)
min_len = min(len(df), len(r))
df = df.iloc[:min_len].copy()
r = r.iloc[:min_len].copy()

print(f"Composite data: {len(df)} obs")

# Build same features
ema50 = df['close'].ewm(span=50).mean().values
ema200 = df['close'].ewm(span=200).mean().values
ema_trend = ema50 / ema200

momentum_5d = np.array([np.sum(r.iloc[max(0,i-5):i+1]) if i > 0 else 0 for i in range(len(r))])

# S5-OV base
signal_base = np.where(ema50 > ema200, 1.0, 0.0)

vol_20_series = pd.Series(r).rolling(20).std()
vol_low = vol_20_series.quantile(0.25)
vol_high = vol_20_series.quantile(0.75)

overlay = np.ones(len(signal_base))
for i in range(len(overlay)):
    if pd.notna(vol_20_series.iloc[i]):
        if vol_20_series.iloc[i] < vol_low:
            overlay[i] = 1.5
        elif vol_20_series.iloc[i] > vol_high:
            overlay[i] = 0.3

signal_s5ov = signal_base * overlay

# S5-OV base
pnl_base = backtest_simple(signal_s5ov, r.values)
sharpe_base = calc_sharpe(pnl_base)
mdd_base = calc_mdd(pnl_base)

print(f"\nComposite S5-OV Base: Sharpe {sharpe_base:.3f}, MDD {mdd_base:.1f}%")

# ML Filter 1 (Momentum>0 AND EMA_trend>0.98)
ml_filter_1 = (momentum_5d > 0) & (ema_trend > 0.98)
signal_ml_1 = signal_s5ov * ml_filter_1.astype(float)
pnl_ml_1 = backtest_simple(signal_ml_1, r.values)
sharpe_ml_1 = calc_sharpe(pnl_ml_1)
mdd_ml_1 = calc_mdd(pnl_ml_1)

print(f"Composite ML Filter 1: Sharpe {sharpe_ml_1:.3f}, MDD {mdd_ml_1:.1f}%")

# ML Filter 3 (Confidence-based)
mom_strong = momentum_5d > np.percentile(momentum_5d, 60)
mom_weak = momentum_5d < np.percentile(momentum_5d, 40)
ema_strong = ema_trend > 1.02
ema_weak = ema_trend < 0.98

ml_confidence = np.ones(len(signal_base))
ml_confidence[mom_strong & ema_strong] = 1.2
ml_confidence[mom_weak | ema_weak] = 0.7

signal_ml_3 = signal_s5ov * ml_confidence
pnl_ml_3 = backtest_simple(signal_ml_3, r.values)
sharpe_ml_3 = calc_sharpe(pnl_ml_3)
mdd_ml_3 = calc_mdd(pnl_ml_3)

print(f"Composite ML Filter 3: Sharpe {sharpe_ml_3:.3f}, MDD {mdd_ml_3:.1f}%")

# Comparison
print(f"\n" + "="*80)
print("NDX vs Composite Validation")
print("="*80)

ndx_base = 0.895  # From earlier
ndx_ml_1 = 3.987
ndx_ml_3 = 1.977

print(f"\nS5-OV Base:")
print(f"  NDX: {ndx_base:.3f} Sharpe")
print(f"  Composite: {sharpe_base:.3f} Sharpe")

print(f"\nML Filter 1 (Momentum>0 AND EMA>0.98):")
print(f"  NDX: {ndx_ml_1:.3f} Sharpe")
print(f"  Composite: {sharpe_ml_1:.3f} Sharpe")
consistency_1 = "✅" if 0.5 <= sharpe_ml_1 <= 5 else "❌"
print(f"  {consistency_1} Consistency: {'GOOD' if 0.5 <= sharpe_ml_1 else 'LIKELY OVERFIT'}")

print(f"\nML Filter 3 (Confidence-based):")
print(f"  NDX: {ndx_ml_3:.3f} Sharpe")
print(f"  Composite: {sharpe_ml_3:.3f} Sharpe")
consistency_3 = "✅" if 0.8 <= sharpe_ml_3 <= 3 else "❌"
print(f"  {consistency_3} Consistency: {'GOOD' if 0.8 <= sharpe_ml_3 else 'LIKELY OVERFIT'}")

print("\n✅ Validation complete\n")
