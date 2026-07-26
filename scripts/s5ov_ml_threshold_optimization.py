#!/usr/bin/env python3
"""
S5-OV + ML Threshold Optimization
==================================
Fine-tune parameters for Filter 1 and Filter 6 to find optimal thresholds.
Goal: Maximize Sharpe while maintaining robustness across NDX and Composite.
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
print("S5-OV + ML THRESHOLD OPTIMIZATION")
print("="*80)

# Load data
df_ndx = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r_ndx = log_returns_pct(df_ndx)
min_len_ndx = min(len(df_ndx), len(r_ndx))
df_ndx = df_ndx.iloc[:min_len_ndx].copy()
r_ndx = r_ndx.iloc[:min_len_ndx].copy()

df_comp = load_ohlc('/home/user/Quant-Trade/data/nasdaq_composite_daily.txt')
r_comp = log_returns_pct(df_comp)
min_len_comp = min(len(df_comp), len(r_comp))
df_comp = df_comp.iloc[:min_len_comp].copy()
r_comp = r_comp.iloc[:min_len_comp].copy()

def build_features(df, r):
    ema50 = df['close'].ewm(span=50).mean().values
    ema200 = df['close'].ewm(span=200).mean().values
    ema_trend = ema50 / ema200

    momentum_5d = np.array([np.sum(r.iloc[max(0,i-5):i+1]) if i > 0 else 0 for i in range(len(r))])

    vol_20_series = pd.Series(r).rolling(20).std()
    vol_low = vol_20_series.quantile(0.25)
    vol_high = vol_20_series.quantile(0.75)

    signal_base = np.where(ema50 > ema200, 1.0, 0.0)
    overlay = np.ones(len(signal_base))
    for i in range(len(overlay)):
        if pd.notna(vol_20_series.iloc[i]):
            if vol_20_series.iloc[i] < vol_low:
                overlay[i] = 1.5
            elif vol_20_series.iloc[i] > vol_high:
                overlay[i] = 0.3

    signal_s5ov = signal_base * overlay

    return {
        'ema_trend': ema_trend,
        'momentum_5d': momentum_5d,
        'signal_s5ov': signal_s5ov,
        'returns': r
    }

features_ndx = build_features(df_ndx, r_ndx)
features_comp = build_features(df_comp, r_comp)

# ============================================================================
# FILTER 1 OPTIMIZATION: (momentum > mom_thresh) & (ema_trend > ema_thresh)
# ============================================================================

print("\n" + "="*80)
print("FILTER 1 PARAMETER GRID SEARCH")
print("="*80)

mom_thresholds = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3]
ema_thresholds = [0.96, 0.97, 0.98, 0.99, 1.00, 1.01, 1.02]

best_config_f1 = None
best_score_f1 = -np.inf

print(f"\nGrid search: {len(mom_thresholds)} x {len(ema_thresholds)} = {len(mom_thresholds)*len(ema_thresholds)} configs")
print("\nTop 10 configurations (by average Sharpe across NDX + Composite):\n")

results_f1 = []

for mom_t in mom_thresholds:
    for ema_t in ema_thresholds:
        # Test on NDX
        filter_1_ndx = (features_ndx['momentum_5d'] > mom_t) & (features_ndx['ema_trend'] > ema_t)
        signal_1_ndx = features_ndx['signal_s5ov'] * filter_1_ndx.astype(float)
        pnl_1_ndx = backtest_simple(signal_1_ndx, features_ndx['returns'].values)
        sharpe_1_ndx = calc_sharpe(pnl_1_ndx)

        # Test on Composite
        filter_1_comp = (features_comp['momentum_5d'] > mom_t) & (features_comp['ema_trend'] > ema_t)
        signal_1_comp = features_comp['signal_s5ov'] * filter_1_comp.astype(float)
        pnl_1_comp = backtest_simple(signal_1_comp, features_comp['returns'].values)
        sharpe_1_comp = calc_sharpe(pnl_1_comp)

        # Average score (prefer stability across both datasets)
        avg_sharpe = (sharpe_1_ndx + sharpe_1_comp) / 2.0
        consistency = abs(sharpe_1_ndx - sharpe_1_comp)

        results_f1.append({
            'mom_t': mom_t,
            'ema_t': ema_t,
            'sharpe_ndx': sharpe_1_ndx,
            'sharpe_comp': sharpe_1_comp,
            'avg_sharpe': avg_sharpe,
            'consistency': consistency,
            'exposure_pct': (filter_1_ndx).mean() * 100
        })

        if avg_sharpe > best_score_f1:
            best_score_f1 = avg_sharpe
            best_config_f1 = (mom_t, ema_t)

# Sort and display top 10
results_f1_sorted = sorted(results_f1, key=lambda x: x['avg_sharpe'], reverse=True)

for i, r in enumerate(results_f1_sorted[:10], 1):
    marker = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "  "))
    print(f"{marker} mom>{r['mom_t']:+.1f} & ema>{r['ema_t']:.2f} | "
          f"NDX {r['sharpe_ndx']:.3f} COMP {r['sharpe_comp']:.3f} | "
          f"AVG {r['avg_sharpe']:.3f} (cons {r['consistency']:.3f}, "
          f"exp {r['exposure_pct']:.1f}%)")

print(f"\n✅ Best Filter 1 config: mom>{best_config_f1[0]:+.1f} & ema>{best_config_f1[1]:.2f} "
      f"(avg Sharpe {best_score_f1:.3f})")

# ============================================================================
# FILTER 6 OPTIMIZATION: (momentum > mom_thresh) | (trend_strength > ts_thresh)
# ============================================================================

print("\n" + "="*80)
print("FILTER 6 PARAMETER GRID SEARCH")
print("="*80)

mom_thresholds_6 = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2]
ts_thresholds = [0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04]

best_config_f6 = None
best_score_f6 = -np.inf

print(f"\nGrid search: {len(mom_thresholds_6)} x {len(ts_thresholds)} = {len(mom_thresholds_6)*len(ts_thresholds)} configs")
print("\nTop 10 configurations (by average Sharpe across NDX + Composite):\n")

results_f6 = []

for mom_t in mom_thresholds_6:
    for ts_t in ts_thresholds:
        # Trend strength
        ema50_ndx = df_ndx['close'].ewm(span=50).mean().values
        ema200_ndx = df_ndx['close'].ewm(span=200).mean().values
        trend_strength_ndx = np.abs((ema50_ndx / ema200_ndx) - 1.0)

        ema50_comp = df_comp['close'].ewm(span=50).mean().values
        ema200_comp = df_comp['close'].ewm(span=200).mean().values
        trend_strength_comp = np.abs((ema50_comp / ema200_comp) - 1.0)

        # Test on NDX
        filter_6_ndx = (features_ndx['momentum_5d'] > mom_t) | (trend_strength_ndx > ts_t)
        signal_6_ndx = features_ndx['signal_s5ov'] * filter_6_ndx.astype(float)
        pnl_6_ndx = backtest_simple(signal_6_ndx, features_ndx['returns'].values)
        sharpe_6_ndx = calc_sharpe(pnl_6_ndx)

        # Test on Composite
        filter_6_comp = (features_comp['momentum_5d'] > mom_t) | (trend_strength_comp > ts_t)
        signal_6_comp = features_comp['signal_s5ov'] * filter_6_comp.astype(float)
        pnl_6_comp = backtest_simple(signal_6_comp, features_comp['returns'].values)
        sharpe_6_comp = calc_sharpe(pnl_6_comp)

        avg_sharpe = (sharpe_6_ndx + sharpe_6_comp) / 2.0
        consistency = abs(sharpe_6_ndx - sharpe_6_comp)

        results_f6.append({
            'mom_t': mom_t,
            'ts_t': ts_t,
            'sharpe_ndx': sharpe_6_ndx,
            'sharpe_comp': sharpe_6_comp,
            'avg_sharpe': avg_sharpe,
            'consistency': consistency,
            'exposure_pct': (filter_6_ndx).mean() * 100
        })

        if avg_sharpe > best_score_f6:
            best_score_f6 = avg_sharpe
            best_config_f6 = (mom_t, ts_t)

results_f6_sorted = sorted(results_f6, key=lambda x: x['avg_sharpe'], reverse=True)

for i, r in enumerate(results_f6_sorted[:10], 1):
    marker = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "  "))
    print(f"{marker} mom>{r['mom_t']:+.1f} | ts>{r['ts_t']:.3f} | "
          f"NDX {r['sharpe_ndx']:.3f} COMP {r['sharpe_comp']:.3f} | "
          f"AVG {r['avg_sharpe']:.3f} (cons {r['consistency']:.3f}, "
          f"exp {r['exposure_pct']:.1f}%)")

print(f"\n✅ Best Filter 6 config: mom>{best_config_f6[0]:+.1f} | ts>{best_config_f6[1]:.3f} "
      f"(avg Sharpe {best_score_f6:.3f})")

# ============================================================================
# COMPARISON: Which performs better?
# ============================================================================

print("\n" + "="*80)
print("FINAL COMPARISON")
print("="*80)

print(f"\n📊 Filter 1 (Strict AND):")
print(f"   Best config: mom>{best_config_f1[0]:+.1f} & ema>{best_config_f1[1]:.2f}")
print(f"   Average Sharpe: {best_score_f1:.3f}")

print(f"\n📊 Filter 6 (Loose OR):")
print(f"   Best config: mom>{best_config_f6[0]:+.1f} | ts>{best_config_f6[1]:.3f}")
print(f"   Average Sharpe: {best_score_f6:.3f}")

if best_score_f1 > best_score_f6:
    print(f"\n🏆 Filter 1 wins by {best_score_f1 - best_score_f6:.3f} Sharpe")
else:
    print(f"\n🏆 Filter 6 wins by {best_score_f6 - best_score_f1:.3f} Sharpe")

print("\n✅ Threshold optimization complete\n")
