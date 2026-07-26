#!/usr/bin/env python3
"""
Validate S5v2 (EMA 60>250) on Composite
========================================
Best variant discovered on NDX, now validate on independent Composite data
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
print("S5v2 (EMA 60>250) VALIDATION ON COMPOSITE")
print("="*80)

df_comp = load_ohlc('/home/user/Quant-Trade/data/nasdaq_composite_daily.txt')
r_comp = log_returns_pct(df_comp)

min_len = min(len(df_comp), len(r_comp))

# Buy & Hold
pnl_bh = backtest_simple(np.ones(min_len), r_comp.values[:min_len])
m_bh = {'sharpe': calc_sharpe(pnl_bh), 'mdd': calc_mdd(pnl_bh), 'ret': np.sum(pnl_bh)}

# S5v2: EMA 60>250
print("\n[S5v2] EMA 60>250...")
ema60 = df_comp['close'].ewm(span=60).mean()
ema250 = df_comp['close'].ewm(span=250).mean()
sig_v2 = np.where(ema60 > ema250, 1.0, 0.0)
pnl_v2 = backtest_simple(sig_v2[:min_len], r_comp.values[:min_len])
m_v2 = {'sharpe': calc_sharpe(pnl_v2), 'mdd': calc_mdd(pnl_v2), 'ret': np.sum(pnl_v2)}

print(f"\nComposite BH:")
print(f"  Sharpe: {m_bh['sharpe']:.3f}, MDD: {m_bh['mdd']:.1f}%, Return: {m_bh['ret']:.1f}%")

print(f"\nComposite S5v2:")
print(f"  Sharpe: {m_v2['sharpe']:.3f}, MDD: {m_v2['mdd']:.1f}%, Return: {m_v2['ret']:.1f}%")

edge = m_v2['sharpe'] - m_bh['sharpe']
print(f"\nEdge:")
print(f"  Sharpe: {edge:+.3f} {'✅ PASS' if edge > 0 else '❌ FAIL'}")
print(f"  MDD improvement: {m_v2['mdd']-m_bh['mdd']:+.1f}%")

results = {
    'strategy': 'S5v2 (EMA 60>250)',
    'market': 'Composite',
    'period': '2021-2026',
    'bh': m_bh,
    'strategy_metrics': m_v2,
    'edge_sharpe': edge,
    'passes_validation': edge > 0
}

with open('/home/user/Quant-Trade/results/s5v2_composite_validation.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Saved\n")
