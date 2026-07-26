#!/usr/bin/env python3
"""
S5-OV [Agg+] Cross-Indices Validation
======================================
Test on Russell 2000, S&P 500, DAX
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

def test_s5ov_on_market(name, data_path):
    """Test S5-OV [Agg+] on given market data"""
    try:
        df = load_ohlc(data_path)
        r = log_returns_pct(df)
    except Exception as e:
        print(f"❌ {name}: Failed to load data ({e})")
        return None

    min_len = min(len(df), len(r))

    # BH
    pnl_bh = backtest_simple(np.ones(min_len), r.values[:min_len])
    m_bh = {'sharpe': calc_sharpe(pnl_bh), 'mdd': calc_mdd(pnl_bh)}

    # S5-OV [Agg+]
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
                overlay_mult[i] = 1.5
            elif vol_20.iloc[i] > vol_high:
                overlay_mult[i] = 0.3

    sig_s5_ov = sig_s5[:min_len] * overlay_mult
    pnl_s5_ov = backtest_simple(sig_s5_ov, r.values[:min_len])
    m_ov = {'sharpe': calc_sharpe(pnl_s5_ov), 'mdd': calc_mdd(pnl_s5_ov), 'ret': np.sum(pnl_s5_ov)}

    return {
        'bh': m_bh,
        'strategy': m_ov,
        'edge_sharpe': m_ov['sharpe'] - m_bh['sharpe'],
        'obs': min_len,
        'period': f"{df['date'].iloc[0]} to {df['date'].iloc[-1]}"
    }

print("\n" + "="*80)
print("S5-OV [AGG+] CROSS-INDICES VALIDATION")
print("="*80)

indices = [
    ("Russell 2000", "/home/user/Quant-Trade/data/russell2000_daily.txt"),
    ("S&P 500", "/home/user/Quant-Trade/data/sp500_daily.txt"),
    ("DAX", "/home/user/Quant-Trade/data/dax_daily.txt"),
]

results = {}

for name, path in indices:
    print(f"\n[{name}]", end=" ")
    result = test_s5ov_on_market(name, path)

    if result:
        results[name] = result
        edge = result['edge_sharpe']
        status = "✅ PASS" if edge > 0 else "❌ FAIL"
        print(f"Sharpe {result['strategy']['sharpe']:.3f} vs BH {result['bh']['sharpe']:.3f} ({edge:+.3f}) {status}")
        print(f"  MDD: {result['strategy']['mdd']:.1f}% vs BH {result['bh']['mdd']:.1f}%")
        print(f"  Return: {result['strategy']['ret']:.1f}%")
        print(f"  Observations: {result['obs']}, Period: {result['period']}")

print(f"\n" + "="*80)
print("COMPARISON")
print("="*80)

print(f"\n{'Index':<20} {'S5-OV Sharpe':<15} {'BH Sharpe':<15} {'Edge':<10} {'Status':<10}")
print(f"{'-'*70}")

for name, result in results.items():
    edge = result['edge_sharpe']
    status = "✅" if edge > 0 else "❌"
    print(f"{name:<20} {result['strategy']['sharpe']:>7.3f} {result['bh']['sharpe']:>14.3f} {edge:>8.3f} {status:>9}")

# Compare to known baselines
print(f"\n" + "="*80)
print("REFERENCE: NDX & Composite Baseline")
print("="*80)
print(f"{'NDX (1985-2026)':<20} {'0.875':<15} {'0.529':<15} {'+0.346':<10} {'✅':<10}")
print(f"{'Composite (2021-26)':<20} {'0.895':<15} {'0.519':<15} {'+0.377':<10} {'✅':<10}")

with open('/home/user/Quant-Trade/results/s5ov_cross_indices.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n✅ Saved\n")
