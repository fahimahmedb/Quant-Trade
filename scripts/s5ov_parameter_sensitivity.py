#!/usr/bin/env python3
"""
S5-OV Parameter Sensitivity Testing
====================================
Test overlay parameters: amplification, reduction, percentiles
Declared a priori configurations only
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
print("S5-OV PARAMETER SENSITIVITY (A Priori Declared Configs)")
print("="*80)

df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)
min_len = min(len(df), len(r))

# Base S5 signal
ema50 = df['close'].ewm(span=50).mean()
ema200 = df['close'].ewm(span=200).mean()
sig_s5 = np.where(ema50 > ema200, 1.0, 0.0)

vol_20 = r.rolling(20).std()

# Declared a priori parameter configurations
configs = [
    # (name, amp_mult, red_mult, pct_low, pct_high)
    ("S5-OV [Base]", 1.2, 0.5, 25, 75),      # Original
    ("S5-OV [Agg+]", 1.5, 0.3, 25, 75),      # More aggressive amplification
    ("S5-OV [Cons]", 1.1, 0.6, 25, 75),      # More conservative
    ("S5-OV [Pct20]", 1.2, 0.5, 20, 80),     # Wider thresholds
    ("S5-OV [Pct30]", 1.2, 0.5, 30, 70),     # Tighter thresholds
]

results = {}

for name, amp, red, pct_low, pct_high in configs:
    vol_low = vol_20.quantile(pct_low / 100.0)
    vol_high = vol_20.quantile(pct_high / 100.0)

    overlay_mult = np.ones(min_len)
    for i in range(min_len):
        if i < len(vol_20) and pd.notna(vol_20.iloc[i]):
            if vol_20.iloc[i] < vol_low:
                overlay_mult[i] = amp
            elif vol_20.iloc[i] > vol_high:
                overlay_mult[i] = red

    sig = sig_s5[:min_len] * overlay_mult
    pnl = backtest_simple(sig, r.values[:min_len])

    sr = calc_sharpe(pnl)
    mdd = calc_mdd(pnl)
    ret = np.sum(pnl)

    results[name] = {'sharpe': sr, 'mdd': mdd, 'return': ret}
    print(f"{name:20s} | Sharpe {sr:.3f} | MDD {mdd:6.1f}% | Return {ret:6.1f}%")

print(f"\n{'='*80}")
print("RANKING")
print(f"{'='*80}")

for rank, (name, metrics) in enumerate(sorted(results.items(),
                                              key=lambda x: x[1]['sharpe'],
                                              reverse=True), 1):
    print(f"{rank}. {name:20s} — Sharpe {metrics['sharpe']:.3f}")

with open('/home/user/Quant-Trade/results/s5ov_parameter_sensitivity.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Saved\n")
