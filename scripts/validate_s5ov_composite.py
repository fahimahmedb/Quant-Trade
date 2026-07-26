#!/usr/bin/env python3
"""
Validate S5-OV (S5 + Vol Overlay) on Composite
===============================================
Breakthrough strategy discovered on NDX, now validate on independent Composite data
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
print("S5-OV (S5 + Vol Overlay) VALIDATION ON COMPOSITE")
print("="*80)

df_comp = load_ohlc('/home/user/Quant-Trade/data/nasdaq_composite_daily.txt')
r_comp = log_returns_pct(df_comp)

min_len = min(len(df_comp), len(r_comp))

# Buy & Hold
pnl_bh = backtest_simple(np.ones(min_len), r_comp.values[:min_len])
m_bh = {'sharpe': calc_sharpe(pnl_bh), 'mdd': calc_mdd(pnl_bh), 'ret': np.sum(pnl_bh)}

# S5 Base
ema50 = df_comp['close'].ewm(span=50).mean()
ema200 = df_comp['close'].ewm(span=200).mean()
sig_s5 = np.where(ema50 > ema200, 1.0, 0.0)
pnl_s5 = backtest_simple(sig_s5[:min_len], r_comp.values[:min_len])
m_s5 = {'sharpe': calc_sharpe(pnl_s5), 'mdd': calc_mdd(pnl_s5), 'ret': np.sum(pnl_s5)}

# S5-OV: S5 + Vol Overlay
print("\n[S5-OV] S5 + Vol-of-Vol overlay...")
vol_20 = r_comp.rolling(20).std()
vol_low = vol_20.quantile(0.25)
vol_high = vol_20.quantile(0.75)

overlay_mult = np.ones(min_len)
for i in range(min_len):
    if i < len(vol_20) and pd.notna(vol_20.iloc[i]):
        if vol_20.iloc[i] < vol_low:
            overlay_mult[i] = 1.2  # Amplify in low vol
        elif vol_20.iloc[i] > vol_high:
            overlay_mult[i] = 0.5  # Reduce in high vol

sig_s5_ov = sig_s5[:min_len] * overlay_mult
pnl_s5_ov = backtest_simple(sig_s5_ov, r_comp.values[:min_len])
m_ov = {'sharpe': calc_sharpe(pnl_s5_ov), 'mdd': calc_mdd(pnl_s5_ov), 'ret': np.sum(pnl_s5_ov)}

print(f"\nComposite BH:")
print(f"  Sharpe: {m_bh['sharpe']:.3f}, MDD: {m_bh['mdd']:.1f}%, Return: {m_bh['ret']:.1f}%")

print(f"\nComposite S5 (base):")
print(f"  Sharpe: {m_s5['sharpe']:.3f}, MDD: {m_s5['mdd']:.1f}%, Return: {m_s5['ret']:.1f}%")

print(f"\nComposite S5-OV:")
print(f"  Sharpe: {m_ov['sharpe']:.3f}, MDD: {m_ov['mdd']:.1f}%, Return: {m_ov['ret']:.1f}%")

edge_ov = m_ov['sharpe'] - m_bh['sharpe']
edge_vs_s5 = m_ov['sharpe'] - m_s5['sharpe']
print(f"\nEdge vs BH:")
print(f"  Sharpe: {edge_ov:+.3f} {'✅ PASS' if edge_ov > 0 else '❌ FAIL'}")
print(f"\nEdge vs S5 base:")
print(f"  Sharpe: {edge_vs_s5:+.3f}")

results = {
    'strategy': 'S5-OV (S5 + Vol Overlay)',
    'market': 'Composite',
    'period': '2021-2026',
    'bh': m_bh,
    's5_base': m_s5,
    'strategy_metrics': m_ov,
    'edge_vs_bh': edge_ov,
    'edge_vs_s5': edge_vs_s5,
    'passes_validation': edge_ov > 0 and edge_vs_s5 > 0
}

with open('/home/user/Quant-Trade/results/s5ov_composite_validation.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Saved\n")
