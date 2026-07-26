#!/usr/bin/env python3
"""
S5-OV + ML Enhancement
======================
ML learns when S5-OV is profitable, filters/amplifies accordingly
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
print("S5-OV + ML ENHANCEMENT")
print("="*80)

# Load data
df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)
min_len = min(len(df), len(r))
df = df.iloc[:min_len].copy()
r = r.iloc[:min_len].copy()

# Build features
ema50 = df['close'].ewm(span=50).mean().values
ema200 = df['close'].ewm(span=200).mean().values
ema_trend = ema50 / ema200

momentum_5d = np.array([np.sum(r.iloc[max(0,i-5):i+1]) if i > 0 else 0 for i in range(len(r))])
momentum_20d = np.array([np.sum(r.iloc[max(0,i-20):i+1]) if i > 0 else 0 for i in range(len(r))])

sma20 = pd.Series(df['close']).rolling(20).mean().values
vol_20_series = pd.Series(r).rolling(20).std()
zscore = (df['close'].values - sma20) / (vol_20_series.values + 1e-6)

# S5-OV base
signal_base = np.where(ema50 > ema200, 1.0, 0.0)

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

print(f"Data: {len(df)} observations")
print(f"S5-OV base Sharpe: {calc_sharpe(backtest_simple(signal_s5ov, r.values)):.3f}")

# =============================================================================
# ML Filtering Strategy 1: Simple Rule-Based (from feature importance)
# "Trade S5-OV only when momentum_5d > 0 AND ema_trend > 0.98"
# =============================================================================

ml_filter_1 = (momentum_5d > 0) & (ema_trend > 0.98)
signal_ml_1 = signal_s5ov * ml_filter_1.astype(float)
pnl_ml_1 = backtest_simple(signal_ml_1, r.values)

print(f"\n[ML Filter 1] Momentum>0 AND EMA_trend>0.98:")
print(f"  Sharpe: {calc_sharpe(pnl_ml_1):.3f}")
print(f"  MDD: {calc_mdd(pnl_ml_1):.1f}%")
print(f"  Exposure: {(ml_filter_1).mean()*100:.1f}% of days")

# =============================================================================
# ML Filtering Strategy 2: Dynamic Exposure (learned strength)
# Expose = S5-OV * (momentum_5d normalized + ema_trend_quality)
# =============================================================================

# Normalize momentum
mom_norm = (momentum_5d - momentum_5d.min()) / (momentum_5d.max() - momentum_5d.min() + 1e-6)
mom_norm = np.clip(mom_norm, 0, 1)

# EMA quality (how strong the trend)
ema_quality = np.abs(ema_trend - 1.0)  # 1.0 is neutral, away from 1.0 is stronger
ema_quality = np.clip(ema_quality, 0, 1)

# Combine
ml_exposure = 0.5 * mom_norm + 0.5 * ema_quality
signal_ml_2 = signal_base * overlay * ml_exposure

pnl_ml_2 = backtest_simple(signal_ml_2, r.values)

print(f"\n[ML Filter 2] Dynamic exposure (0.5*momentum + 0.5*ema_quality):")
print(f"  Sharpe: {calc_sharpe(pnl_ml_2):.3f}")
print(f"  MDD: {calc_mdd(pnl_ml_2):.1f}%")
print(f"  Avg exposure: {ml_exposure.mean():.3f}x")

# =============================================================================
# ML Filtering Strategy 3: Confidence-based
# Reduce to 0.5x when both momentum & ema are weak
# Amplify to 1.2x when both strong
# =============================================================================

mom_strong = momentum_5d > np.percentile(momentum_5d, 60)
mom_weak = momentum_5d < np.percentile(momentum_5d, 40)
ema_strong = ema_trend > 1.02
ema_weak = ema_trend < 0.98

ml_confidence = np.ones(len(signal_base))
ml_confidence[mom_strong & ema_strong] = 1.2
ml_confidence[mom_weak | ema_weak] = 0.7

signal_ml_3 = signal_s5ov * ml_confidence

pnl_ml_3 = backtest_simple(signal_ml_3, r.values)

print(f"\n[ML Filter 3] Confidence-based (1.2x strong, 0.7x weak):")
print(f"  Sharpe: {calc_sharpe(pnl_ml_3):.3f}")
print(f"  MDD: {calc_mdd(pnl_ml_3):.1f}%")
print(f"  Return: {np.sum(pnl_ml_3):.1f}%")

# =============================================================================
# Comparison
# =============================================================================

print(f"\n" + "="*80)
print("SUMMARY")
print("="*80)

results = {
    'S5-OV Base': calc_sharpe(backtest_simple(signal_s5ov, r.values)),
    'S5-OV + ML Filter 1': calc_sharpe(pnl_ml_1),
    'S5-OV + ML Filter 2': calc_sharpe(pnl_ml_2),
    'S5-OV + ML Filter 3': calc_sharpe(pnl_ml_3),
}

for name, sharpe in sorted(results.items(), key=lambda x: x[1], reverse=True):
    marker = "✅" if sharpe > 0.875 else ("⚠️" if sharpe > 0.700 else "❌")
    print(f"{marker} {name:25s}: {sharpe:.3f}")

best = max(results, key=results.get)
print(f"\n🏆 Best: {best} (Sharpe {results[best]:.3f})")

print("\n✅ Complete\n")
