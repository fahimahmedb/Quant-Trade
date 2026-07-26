#!/usr/bin/env python3
"""
S5-OV + ML Advanced Filters (Beyond Conventional)
===================================================
Testing unconventional filter combinations to find better hypotheses:
- Filter 2a: Mean reversion entry (zscore)
- Filter 2b: Momentum + Mean reversion combined
- Filter 4: Trend strength (only strong trends)
- Filter 5: Volatility regime filtering
- Filter 6: Asymmetric (dynamic thresholds based on regime)
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
print("S5-OV + ML ADVANCED FILTER EXPLORATION")
print("="*80)

# Load data (NDX)
df_ndx = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r_ndx = log_returns_pct(df_ndx)
min_len_ndx = min(len(df_ndx), len(r_ndx))
df_ndx = df_ndx.iloc[:min_len_ndx].copy()
r_ndx = r_ndx.iloc[:min_len_ndx].copy()

# Load data (Composite - independent)
df_comp = load_ohlc('/home/user/Quant-Trade/data/nasdaq_composite_daily.txt')
r_comp = log_returns_pct(df_comp)
min_len_comp = min(len(df_comp), len(r_comp))
df_comp = df_comp.iloc[:min_len_comp].copy()
r_comp = r_comp.iloc[:min_len_comp].copy()

def build_features_and_filters(df, r):
    """Build features and test filters on given dataset"""
    # Features
    ema50 = df['close'].ewm(span=50).mean().values
    ema200 = df['close'].ewm(span=200).mean().values
    ema_trend = ema50 / ema200

    momentum_5d = np.array([np.sum(r.iloc[max(0,i-5):i+1]) if i > 0 else 0 for i in range(len(r))])
    momentum_20d = np.array([np.sum(r.iloc[max(0,i-20):i+1]) if i > 0 else 0 for i in range(len(r))])

    sma20 = pd.Series(df['close']).rolling(20).mean().values
    vol_20_series = pd.Series(r).rolling(20).std()
    zscore = (df['close'].values - sma20) / (vol_20_series.values + 1e-6)

    # S5-OV base (Agg+)
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

    return {
        'ema_trend': ema_trend,
        'momentum_5d': momentum_5d,
        'momentum_20d': momentum_20d,
        'zscore': zscore,
        'signal_s5ov': signal_s5ov,
        'vol_20': vol_20_series,
        'returns': r
    }

def test_filters(features, dataset_name):
    """Test all advanced filters on dataset"""
    print(f"\n{'='*80}")
    print(f"Testing on {dataset_name}")
    print(f"{'='*80}")

    ema_trend = features['ema_trend']
    momentum_5d = features['momentum_5d']
    momentum_20d = features['momentum_20d']
    zscore = features['zscore']
    signal_s5ov = features['signal_s5ov']
    vol_20 = features['vol_20']
    r = features['returns']

    # Filter 2a: Mean reversion (zscore < -0.5, price oversold)
    # Trade S5-OV when price is below SMA (mean reversion setup)
    filter_2a = zscore < -0.5
    signal_2a = signal_s5ov * filter_2a.astype(float)
    pnl_2a = backtest_simple(signal_2a, r.values)

    print(f"\n[Filter 2a] Mean Reversion (zscore < -0.5):")
    print(f"  Sharpe: {calc_sharpe(pnl_2a):.3f}")
    print(f"  MDD: {calc_mdd(pnl_2a):.1f}%")
    print(f"  Exposure: {(filter_2a).mean()*100:.1f}% of days")

    # Filter 2b: Momentum + Mean reversion (both conditions)
    filter_2b = (momentum_5d > 0) & (zscore < 0.5) & (zscore > -1.0)
    signal_2b = signal_s5ov * filter_2b.astype(float)
    pnl_2b = backtest_simple(signal_2b, r.values)

    print(f"\n[Filter 2b] Momentum + Mean Reversion (mom>0 AND -1<zscore<0.5):")
    print(f"  Sharpe: {calc_sharpe(pnl_2b):.3f}")
    print(f"  MDD: {calc_mdd(pnl_2b):.1f}%")
    print(f"  Exposure: {(filter_2b).mean()*100:.1f}% of days")

    # Filter 4: Trend strength (only strong trends)
    # ema_trend far from 1.0 indicates strong trend
    trend_strength = np.abs(ema_trend - 1.0)
    filter_4 = trend_strength > 0.04  # Top quartile of trend strength
    signal_4 = signal_s5ov * filter_4.astype(float)
    pnl_4 = backtest_simple(signal_4, r.values)

    print(f"\n[Filter 4] Trend Strength (|ema_trend - 1.0| > 0.04):")
    print(f"  Sharpe: {calc_sharpe(pnl_4):.3f}")
    print(f"  MDD: {calc_mdd(pnl_4):.1f}%")
    print(f"  Exposure: {(filter_4).mean()*100:.1f}% of days")

    # Filter 5: Volatility regime (only in normal/high volatility, avoid dead periods)
    vol_median = vol_20.median()
    filter_5 = vol_20 >= vol_median  # Trade in higher vol regime
    signal_5 = signal_s5ov * filter_5.astype(float)
    pnl_5 = backtest_simple(signal_5, r.values)

    print(f"\n[Filter 5] Volatility Regime (vol_20 >= median):")
    print(f"  Sharpe: {calc_sharpe(pnl_5):.3f}")
    print(f"  MDD: {calc_mdd(pnl_5):.1f}%")
    print(f"  Exposure: {(filter_5).mean()*100:.1f}% of days")

    # Filter 6: Asymmetric (momentum > 0 OR strong trend)
    # More lenient entry: either momentum is positive OR trend is very strong
    filter_6 = (momentum_5d > 0) | (trend_strength > 0.03)
    signal_6 = signal_s5ov * filter_6.astype(float)
    pnl_6 = backtest_simple(signal_6, r.values)

    print(f"\n[Filter 6] Asymmetric (mom>0 OR trend_strength>0.03):")
    print(f"  Sharpe: {calc_sharpe(pnl_6):.3f}")
    print(f"  MDD: {calc_mdd(pnl_6):.1f}%")
    print(f"  Exposure: {(filter_6).mean()*100:.1f}% of days")

    # Reference: Filter 1 (baseline)
    filter_1 = (momentum_5d > 0) & (ema_trend > 0.98)
    signal_1 = signal_s5ov * filter_1.astype(float)
    pnl_1 = backtest_simple(signal_1, r.values)

    print(f"\n[Filter 1] Reference Baseline (mom>0 AND ema>0.98):")
    print(f"  Sharpe: {calc_sharpe(pnl_1):.3f}")
    print(f"  MDD: {calc_mdd(pnl_1):.1f}%")

    # Summary ranking
    print(f"\n{'─'*80}")
    print(f"RANKING BY SHARPE ({dataset_name}):")
    results = {
        'Filter 1 (Baseline)': calc_sharpe(pnl_1),
        'Filter 2a (Mean Reversion)': calc_sharpe(pnl_2a),
        'Filter 2b (Momentum+MR)': calc_sharpe(pnl_2b),
        'Filter 4 (Trend Strength)': calc_sharpe(pnl_4),
        'Filter 5 (Vol Regime)': calc_sharpe(pnl_5),
        'Filter 6 (Asymmetric)': calc_sharpe(pnl_6),
    }

    for i, (name, sharpe) in enumerate(sorted(results.items(), key=lambda x: x[1], reverse=True), 1):
        marker = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "  "))
        print(f"{marker} {name:30s}: {sharpe:.3f}")

    return results

# Test on NDX
features_ndx = build_features_and_filters(df_ndx, r_ndx)
results_ndx = test_filters(features_ndx, "NDX (40 years)")

# Test on Composite
features_comp = build_features_and_filters(df_comp, r_comp)
results_comp = test_filters(features_comp, "COMPOSITE (5 years, independent)")

# Cross-validation check
print(f"\n" + "="*80)
print("CROSS-VALIDATION: NDX vs COMPOSITE")
print("="*80)

for filter_name in results_ndx.keys():
    ndx_sharpe = results_ndx[filter_name]
    comp_sharpe = results_comp[filter_name]
    diff = comp_sharpe - ndx_sharpe
    consistency = "✅" if abs(diff) < 0.5 else "⚠️"
    print(f"{consistency} {filter_name:30s}: NDX {ndx_sharpe:.3f} vs COMP {comp_sharpe:.3f} (diff {diff:+.3f})")

print("\n✅ Advanced ML filter exploration complete\n")
