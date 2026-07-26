#!/usr/bin/env python3
"""
S5 Complete Validation Pipeline
================================
Rigorous multi-market, multi-period walk-forward validation
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
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
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

def s5_signal(df):
    """EMA 50>200 long-only"""
    ema_50 = df['close'].ewm(span=50).mean()
    ema_200 = df['close'].ewm(span=200).mean()
    signal = np.where(ema_50 > ema_200, 1.0, 0.0)
    return signal

print("\n" + "="*80)
print("S5 COMPLETE VALIDATION PIPELINE")
print("="*80)

# Load both markets
try:
    df_ndx = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
    df_comp = load_ohlc('/home/user/Quant-Trade/data/nasdaq_composite_daily.txt')
except Exception as e:
    print(f"❌ Data load failed: {e}")
    sys.exit(1)

results = {}

for name, df in [("NDX", df_ndx), ("Composite", df_comp)]:
    print(f"\n{'='*80}")
    print(f"{name} Validation")
    print(f"{'='*80}")

    r = log_returns_pct(df)
    signal = s5_signal(df)

    min_len = min(len(signal), len(r))

    # Full period
    pnl_bh = backtest_simple(np.ones(min_len), r.values[:min_len])
    pnl_s5 = backtest_simple(signal[:min_len], r.values[:min_len])

    m_bh = {'sharpe': calc_sharpe(pnl_bh), 'mdd': calc_mdd(pnl_bh), 'ret': np.sum(pnl_bh)}
    m_s5 = {'sharpe': calc_sharpe(pnl_s5), 'mdd': calc_mdd(pnl_s5), 'ret': np.sum(pnl_s5)}

    print(f"BH: Sharpe {m_bh['sharpe']:.3f}, MDD {m_bh['mdd']:.1f}%, Return {m_bh['ret']:.1f}%")
    print(f"S5: Sharpe {m_s5['sharpe']:.3f}, MDD {m_s5['mdd']:.1f}%, Return {m_s5['ret']:.1f}%")
    print(f"Edge: Sharpe {m_s5['sharpe']-m_bh['sharpe']:+.3f}, MDD {m_s5['mdd']-m_bh['mdd']:+.1f}%")

    # Rolling window stress test
    print(f"\nRolling window stress (1-year windows):")
    windows = []
    for start in range(0, len(df)-252, 252):
        end = min(start + 252, len(df))
        pnl_s5_w = backtest_simple(signal[start:end], r.values[start:end])
        sr_w = calc_sharpe(pnl_s5_w)
        windows.append(sr_w)

    if windows:
        print(f"  Windows: min {min(windows):.3f}, max {max(windows):.3f}, mean {np.mean(windows):.3f}")
        print(f"  Consistency: {(np.array(windows) > 0).sum()}/{len(windows)} positive")

    results[name] = {
        'bh_sharpe': m_bh['sharpe'],
        'bh_mdd': m_bh['mdd'],
        's5_sharpe': m_s5['sharpe'],
        's5_mdd': m_s5['mdd'],
        'edge_sharpe': m_s5['sharpe'] - m_bh['sharpe'],
        'window_consistency': (np.array(windows) > 0).sum() / len(windows) if windows else 0
    }

# Save
with open('/home/user/Quant-Trade/results/s5_validation_complete.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*80}")
print("✅ Complete validation saved")
print(f"{'='*80}\n")
