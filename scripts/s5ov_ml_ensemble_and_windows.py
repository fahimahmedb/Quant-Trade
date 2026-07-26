#!/usr/bin/env python3
"""
S5-OV + ML Ensemble & Momentum Windows
========================================
Test:
1. Ensemble weighting (confidence-based combination of signals)
2. Alternative momentum lookback windows (3d, 10d, 20d)
3. Asymmetric momentum (different thresholds for bull/bear regimes)
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
print("S5-OV + ML ENSEMBLE & MOMENTUM WINDOW EXPLORATION")
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

def test_momentum_windows(df, r, dataset_name):
    """Test different momentum lookback windows"""
    print(f"\n{'='*80}")
    print(f"MOMENTUM WINDOW TESTING ON {dataset_name}")
    print(f"{'='*80}")

    ema50 = df['close'].ewm(span=50).mean().values
    ema200 = df['close'].ewm(span=200).mean().values
    ema_trend = ema50 / ema200

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

    results_windows = {}

    # Test different momentum windows
    for window in [3, 5, 10, 20]:
        momentum = np.array([np.sum(r.iloc[max(0,i-window):i+1]) if i > 0 else 0 for i in range(len(r))])

        # Use optimized thresholds from previous analysis
        filter_opt = (momentum > 0.3) & (ema_trend > 0.96)
        signal = signal_s5ov * filter_opt.astype(float)
        pnl = backtest_simple(signal, r.values)
        sharpe = calc_sharpe(pnl)
        mdd = calc_mdd(pnl)
        exposure = filter_opt.mean() * 100

        results_windows[window] = {
            'sharpe': sharpe,
            'mdd': mdd,
            'exposure': exposure
        }

        print(f"\nMomentum window {window}d (threshold > 0.3):")
        print(f"  Sharpe: {sharpe:.3f}, MDD: {mdd:.1f}%, Exposure: {exposure:.1f}%")

    return results_windows

def test_ensemble_approaches(df, r, dataset_name):
    """Test ensemble/confidence-weighted approaches"""
    print(f"\n{'='*80}")
    print(f"ENSEMBLE APPROACHES ON {dataset_name}")
    print(f"{'='*80}")

    ema50 = df['close'].ewm(span=50).mean().values
    ema200 = df['close'].ewm(span=200).mean().values
    ema_trend = ema50 / ema200

    momentum_5d = np.array([np.sum(r.iloc[max(0,i-5):i+1]) if i > 0 else 0 for i in range(len(r))])
    momentum_20d = np.array([np.sum(r.iloc[max(0,i-20):i+1]) if i > 0 else 0 for i in range(len(r))])

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

    results_ensemble = {}

    # Ensemble 1: Simple binary filter (Filter 1 optimized)
    filter_1 = (momentum_5d > 0.3) & (ema_trend > 0.96)
    signal_e1 = signal_s5ov * filter_1.astype(float)
    pnl_e1 = backtest_simple(signal_e1, r.values)
    results_ensemble['Binary Filter (opt)'] = {
        'sharpe': calc_sharpe(pnl_e1),
        'mdd': calc_mdd(pnl_e1),
        'exposure': filter_1.mean() * 100
    }

    # Ensemble 2: Confidence-weighted (normalize and combine)
    # Normalize momentum strength: 0 to 1 scale
    mom_norm = (momentum_5d - momentum_5d.min()) / (momentum_5d.max() - momentum_5d.min() + 1e-6)
    mom_norm = np.clip(mom_norm, 0, 1)

    # EMA trend strength
    ema_strength = np.abs(ema_trend - 1.0)
    ema_strength = np.clip(ema_strength / ema_strength.max(), 0, 1)

    # Combined confidence (average)
    confidence = 0.5 * mom_norm + 0.5 * ema_strength
    signal_e2 = signal_s5ov * confidence
    pnl_e2 = backtest_simple(signal_e2, r.values)
    results_ensemble['Confidence Weighted'] = {
        'sharpe': calc_sharpe(pnl_e2),
        'mdd': calc_mdd(pnl_e2),
        'exposure': confidence.mean()
    }

    # Ensemble 3: Dual momentum (agreement between 5d and 20d)
    momentum_5_norm = (momentum_5d - momentum_5d.min()) / (momentum_5d.max() - momentum_5d.min() + 1e-6)
    momentum_20_norm = (momentum_20d - momentum_20d.min()) / (momentum_20d.max() - momentum_20d.min() + 1e-6)
    dual_momentum = 0.7 * momentum_5_norm + 0.3 * momentum_20_norm  # Weight short-term more
    signal_e3 = signal_s5ov * dual_momentum
    pnl_e3 = backtest_simple(signal_e3, r.values)
    results_ensemble['Dual Momentum (5d+20d)'] = {
        'sharpe': calc_sharpe(pnl_e3),
        'mdd': calc_mdd(pnl_e3),
        'exposure': dual_momentum.mean()
    }

    # Ensemble 4: Boolean vote (2 out of 3 conditions)
    cond1 = momentum_5d > 0
    cond2 = ema_trend > 0.98
    cond3 = momentum_20d > 0
    votes = cond1.astype(int) + cond2.astype(int) + cond3.astype(int)
    filter_vote = votes >= 2
    signal_e4 = signal_s5ov * filter_vote.astype(float)
    pnl_e4 = backtest_simple(signal_e4, r.values)
    results_ensemble['Boolean Vote (2/3)'] = {
        'sharpe': calc_sharpe(pnl_e4),
        'mdd': calc_mdd(pnl_e4),
        'exposure': filter_vote.mean() * 100
    }

    # Display results
    for name, metrics in sorted(results_ensemble.items(), key=lambda x: x[1]['sharpe'], reverse=True):
        marker = "🥇" if metrics['sharpe'] == max(m['sharpe'] for m in results_ensemble.values()) else "  "
        print(f"\n{marker} {name}:")
        print(f"   Sharpe: {metrics['sharpe']:.3f}, MDD: {metrics['mdd']:.1f}%, Exposure: {metrics['exposure']:.1f}%")

    return results_ensemble

# Test on NDX
print("\n📊 NASDAQ-100 (40 years):")
wins_ndx = test_momentum_windows(df_ndx, r_ndx, "NDX")
ens_ndx = test_ensemble_approaches(df_ndx, r_ndx, "NDX")

# Test on Composite
print("\n\n📊 NASDAQ COMPOSITE (5 years, independent):")
wins_comp = test_momentum_windows(df_comp, r_comp, "COMPOSITE")
ens_comp = test_ensemble_approaches(df_comp, r_comp, "COMPOSITE")

# Summary
print("\n" + "="*80)
print("SUMMARY: BEST APPROACHES ACROSS BOTH DATASETS")
print("="*80)

# Momentum windows
print("\n🔍 Momentum Window Analysis:")
best_win_ndx = max(wins_ndx.items(), key=lambda x: x[1]['sharpe'])
best_win_comp = max(wins_comp.items(), key=lambda x: x[1]['sharpe'])
print(f"  NDX best: {best_win_ndx[0]}d window ({best_win_ndx[1]['sharpe']:.3f} Sharpe)")
print(f"  COMP best: {best_win_comp[0]}d window ({best_win_comp[1]['sharpe']:.3f} Sharpe)")

# Ensembles
print("\n🔀 Ensemble Analysis:")
for name in ens_ndx.keys():
    ndx_s = ens_ndx[name]['sharpe']
    comp_s = ens_comp[name]['sharpe']
    avg_s = (ndx_s + comp_s) / 2.0
    consistency = abs(ndx_s - comp_s)
    print(f"  {name:30s}: NDX {ndx_s:.3f} COMP {comp_s:.3f} (avg {avg_s:.3f}, cons {consistency:.3f})")

print("\n✅ Ensemble & momentum window exploration complete\n")
