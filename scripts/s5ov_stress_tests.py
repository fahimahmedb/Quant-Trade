#!/usr/bin/env python3
"""
S5-OV Stress Testing
====================
Market regime analysis: bull/bear/sideways performance
"""

import sys
import json
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
    return pnl - turn * (cost_bps / 1e4)

print("\n" + "="*80)
print("S5-OV STRESS TESTING (Market Regimes)")
print("="*80)

df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)

min_len = min(len(df), len(r))

# Build S5-OV strategy
ema50 = df['close'].ewm(span=50).mean()
ema200 = df['close'].ewm(span=200).mean()
sig_s5 = np.where(ema50 > ema200, 1.0, 0.0)

vol_20 = r.rolling(20).std()
vol_low = vol_20.quantile(0.25)
vol_high = vol_20.quantile(0.75)

overlay_mult = np.ones(min_len)
for i in range(min_len):
    if i < len(vol_20) and pd.notna(vol_20.iloc[i]):
        if vol_20.iloc[i] < vol_low:
            overlay_mult[i] = 1.2
        elif vol_20.iloc[i] > vol_high:
            overlay_mult[i] = 0.5

sig_s5_ov = sig_s5[:min_len] * overlay_mult

# Define regimes by rolling annual return
rolling_ret_1y = df['close'].pct_change().rolling(252).sum()
rolling_ret_1y = rolling_ret_1y.fillna(0)

# Percentile-based regimes
ret_30 = rolling_ret_1y.quantile(0.33)
ret_70 = rolling_ret_1y.quantile(0.67)

regimes = {}
results = {}

# Bull market (top 33% annual returns)
bull_mask = rolling_ret_1y >= ret_70
if bull_mask.sum() > 50:
    pnl_bh_bull = backtest_simple(np.ones(min_len)[bull_mask.values[:min_len]],
                                   r.values[:min_len][bull_mask.values[:min_len]])
    pnl_s5_bull = backtest_simple(sig_s5_ov[bull_mask.values[:min_len]],
                                  r.values[:min_len][bull_mask.values[:min_len]])
    results['bull'] = {
        'bh_sharpe': calc_sharpe(pnl_bh_bull),
        'bh_mdd': calc_mdd(pnl_bh_bull),
        's5ov_sharpe': calc_sharpe(pnl_s5_bull),
        's5ov_mdd': calc_mdd(pnl_s5_bull),
        'obs': bull_mask.sum()
    }
    print(f"\n[BULL Market] (top 33% annual returns, {bull_mask.sum()} obs)")
    print(f"  BH: {results['bull']['bh_sharpe']:.3f} Sharpe, {results['bull']['bh_mdd']:.1f}% MDD")
    print(f"  S5-OV: {results['bull']['s5ov_sharpe']:.3f} Sharpe, {results['bull']['s5ov_mdd']:.1f}% MDD")

# Bear market (bottom 33% annual returns)
bear_mask = rolling_ret_1y <= ret_30
if bear_mask.sum() > 50:
    pnl_bh_bear = backtest_simple(np.ones(min_len)[bear_mask.values[:min_len]],
                                  r.values[:min_len][bear_mask.values[:min_len]])
    pnl_s5_bear = backtest_simple(sig_s5_ov[bear_mask.values[:min_len]],
                                  r.values[:min_len][bear_mask.values[:min_len]])
    results['bear'] = {
        'bh_sharpe': calc_sharpe(pnl_bh_bear),
        'bh_mdd': calc_mdd(pnl_bh_bear),
        's5ov_sharpe': calc_sharpe(pnl_s5_bear),
        's5ov_mdd': calc_mdd(pnl_s5_bear),
        'obs': bear_mask.sum()
    }
    print(f"\n[BEAR Market] (bottom 33% annual returns, {bear_mask.sum()} obs)")
    print(f"  BH: {results['bear']['bh_sharpe']:.3f} Sharpe, {results['bear']['bh_mdd']:.1f}% MDD")
    print(f"  S5-OV: {results['bear']['s5ov_sharpe']:.3f} Sharpe, {results['bear']['s5ov_mdd']:.1f}% MDD")

# Sideways market (middle 33%)
sideways_mask = ~(bull_mask | bear_mask)
if sideways_mask.sum() > 50:
    pnl_bh_side = backtest_simple(np.ones(min_len)[sideways_mask.values[:min_len]],
                                  r.values[:min_len][sideways_mask.values[:min_len]])
    pnl_s5_side = backtest_simple(sig_s5_ov[sideways_mask.values[:min_len]],
                                  r.values[:min_len][sideways_mask.values[:min_len]])
    results['sideways'] = {
        'bh_sharpe': calc_sharpe(pnl_bh_side),
        'bh_mdd': calc_mdd(pnl_bh_side),
        's5ov_sharpe': calc_sharpe(pnl_s5_side),
        's5ov_mdd': calc_mdd(pnl_s5_side),
        'obs': sideways_mask.sum()
    }
    print(f"\n[SIDEWAYS Market] (middle 33% annual returns, {sideways_mask.sum()} obs)")
    print(f"  BH: {results['sideways']['bh_sharpe']:.3f} Sharpe, {results['sideways']['bh_mdd']:.1f}% MDD")
    print(f"  S5-OV: {results['sideways']['s5ov_sharpe']:.3f} Sharpe, {results['sideways']['s5ov_mdd']:.1f}% MDD")

# High volatility periods (top 25% rolling vol)
vol_high_pct = vol_20.quantile(0.75)
highvol_mask = vol_20.fillna(0) >= vol_high_pct
if highvol_mask.sum() > 50:
    pnl_bh_hvol = backtest_simple(np.ones(min_len)[highvol_mask.values[:min_len]],
                                  r.values[:min_len][highvol_mask.values[:min_len]])
    pnl_s5_hvol = backtest_simple(sig_s5_ov[highvol_mask.values[:min_len]],
                                  r.values[:min_len][highvol_mask.values[:min_len]])
    results['high_vol'] = {
        'bh_sharpe': calc_sharpe(pnl_bh_hvol),
        'bh_mdd': calc_mdd(pnl_bh_hvol),
        's5ov_sharpe': calc_sharpe(pnl_s5_hvol),
        's5ov_mdd': calc_mdd(pnl_s5_hvol),
        'obs': highvol_mask.sum()
    }
    print(f"\n[HIGH VOLATILITY] (top 25% rolling vol, {highvol_mask.sum()} obs)")
    print(f"  BH: {results['high_vol']['bh_sharpe']:.3f} Sharpe, {results['high_vol']['bh_mdd']:.1f}% MDD")
    print(f"  S5-OV: {results['high_vol']['s5ov_sharpe']:.3f} Sharpe, {results['high_vol']['s5ov_mdd']:.1f}% MDD")

with open('/home/user/Quant-Trade/results/s5ov_stress_tests.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n✅ Saved\n")
