#!/usr/bin/env python3
"""
Validate Best S5-OV Configuration on Composite
===============================================
S5-OV [Agg+] (1.5x amp, 0.3x red) discovered as best on NDX
Now validate on independent Composite data
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
print("S5-OV [Agg+] (1.5x amp, 0.3x red) VALIDATION ON COMPOSITE")
print("="*80)

df_comp = load_ohlc('/home/user/Quant-Trade/data/nasdaq_composite_daily.txt')
r_comp = log_returns_pct(df_comp)
min_len = min(len(df_comp), len(r_comp))

# BH
pnl_bh = backtest_simple(np.ones(min_len), r_comp.values[:min_len])
m_bh = {'sharpe': calc_sharpe(pnl_bh), 'mdd': calc_mdd(pnl_bh), 'ret': np.sum(pnl_bh)}

# S5 Base
ema50 = df_comp['close'].ewm(span=50).mean()
ema200 = df_comp['close'].ewm(span=200).mean()
sig_s5 = np.where(ema50 > ema200, 1.0, 0.0)
pnl_s5 = backtest_simple(sig_s5[:min_len], r_comp.values[:min_len])
m_s5 = {'sharpe': calc_sharpe(pnl_s5), 'mdd': calc_mdd(pnl_s5)}

# S5-OV [Base]
vol_20 = r_comp.rolling(20).std()
vol_low_base = vol_20.quantile(0.25)
vol_high_base = vol_20.quantile(0.75)
overlay_base = np.ones(min_len)
for i in range(min_len):
    if i < len(vol_20) and pd.notna(vol_20.iloc[i]):
        if vol_20.iloc[i] < vol_low_base:
            overlay_base[i] = 1.2
        elif vol_20.iloc[i] > vol_high_base:
            overlay_base[i] = 0.5
sig_ov_base = sig_s5[:min_len] * overlay_base
pnl_ov_base = backtest_simple(sig_ov_base, r_comp.values[:min_len])
m_ov_base = {'sharpe': calc_sharpe(pnl_ov_base), 'mdd': calc_mdd(pnl_ov_base), 'ret': np.sum(pnl_ov_base)}

# S5-OV [Agg+]: 1.5x amp, 0.3x red
print("\n[S5-OV Agg+] 1.5x amplification, 0.3x reduction...")
vol_low_agg = vol_20.quantile(0.25)
vol_high_agg = vol_20.quantile(0.75)
overlay_agg = np.ones(min_len)
for i in range(min_len):
    if i < len(vol_20) and pd.notna(vol_20.iloc[i]):
        if vol_20.iloc[i] < vol_low_agg:
            overlay_agg[i] = 1.5  # More aggressive
        elif vol_20.iloc[i] > vol_high_agg:
            overlay_agg[i] = 0.3  # More protective
sig_ov_agg = sig_s5[:min_len] * overlay_agg
pnl_ov_agg = backtest_simple(sig_ov_agg, r_comp.values[:min_len])
m_ov_agg = {'sharpe': calc_sharpe(pnl_ov_agg), 'mdd': calc_mdd(pnl_ov_agg), 'ret': np.sum(pnl_ov_agg)}

print(f"\nComposite Results Summary:")
print(f"\n  BH:              Sharpe {m_bh['sharpe']:.3f}, MDD {m_bh['mdd']:.1f}%, Return {m_bh['ret']:.1f}%")
print(f"  S5 Base:         Sharpe {m_s5['sharpe']:.3f}, MDD {m_s5['mdd']:.1f}%")
print(f"  S5-OV [Base]:    Sharpe {m_ov_base['sharpe']:.3f}, MDD {m_ov_base['mdd']:.1f}%, Return {m_ov_base['ret']:.1f}%")
print(f"  S5-OV [Agg+]:    Sharpe {m_ov_agg['sharpe']:.3f}, MDD {m_ov_agg['mdd']:.1f}%, Return {m_ov_agg['ret']:.1f}%")

edge_agg = m_ov_agg['sharpe'] - m_bh['sharpe']
print(f"\nS5-OV [Agg+] Edge vs BH: {edge_agg:+.3f} {'✅ PASS' if edge_agg > 0 else '❌ FAIL'}")

# Cross-market comparison
print(f"\n" + "="*80)
print("CROSS-MARKET COMPARISON (NDX vs Composite)")
print("="*80)

print(f"\nS5-OV [Agg+] (Best configuration):")
print(f"  NDX:       Sharpe 0.875, MDD -25.4%, Return 567.1%")
print(f"  Composite: Sharpe {m_ov_agg['sharpe']:.3f}, MDD {m_ov_agg['mdd']:.1f}%, Return {m_ov_agg['ret']:.1f}%")
consistency = "✅ EXCELLENT" if abs(0.875 - m_ov_agg['sharpe']) < 0.15 else "⚠️ MODERATE"
print(f"  Consistency: {consistency}")

results = {
    'strategy': 'S5-OV [Agg+] (1.5x amp, 0.3x red)',
    'market': 'Composite',
    'period': '2021-2026',
    'bh': m_bh,
    's5_base': m_s5,
    's5ov_base': m_ov_base,
    's5ov_agg': m_ov_agg,
    'edge_vs_bh': edge_agg,
    'edge_vs_s5': m_ov_agg['sharpe'] - m_s5['sharpe'],
    'passes_validation': edge_agg > 0
}

with open('/home/user/Quant-Trade/results/s5ov_best_composite_validation.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n✅ Saved\n")
