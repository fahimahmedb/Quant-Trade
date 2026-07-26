#!/usr/bin/env python3
"""
S5 Variants Testing (Declared A Priori)
========================================
S5v1: EMA 40>180 (reactive)
S5v2: EMA 60>250 (smooth)
S5v3: EMA 50>200+filter (confirm with RSI)
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

def calc_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100.0 - 100.0 / (1.0 + rs)

    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.0
        else:
            upval = 0.0
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100.0 - 100.0 / (1.0 + rs)
    return rsi

print("\n" + "="*80)
print("S5 VARIANTS TESTING (A Priori Declaration)")
print("="*80)

df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)

variants = {}

# S5v1: EMA 40>180 (reactive)
print("\n[S5v1] EMA 40>180 (Reactive)...")
ema40 = df['close'].ewm(span=40).mean()
ema180 = df['close'].ewm(span=180).mean()
sig_v1 = np.where(ema40 > ema180, 1.0, 0.0)
min_len = min(len(sig_v1), len(r))
pnl_v1 = backtest_simple(sig_v1[:min_len], r.values[:min_len])
variants['S5v1'] = {'sharpe': calc_sharpe(pnl_v1), 'mdd': calc_mdd(pnl_v1), 'ret': np.sum(pnl_v1)}

# S5v2: EMA 60>250 (smooth)
print("[S5v2] EMA 60>250 (Smooth)...")
ema60 = df['close'].ewm(span=60).mean()
ema250 = df['close'].ewm(span=250).mean()
sig_v2 = np.where(ema60 > ema250, 1.0, 0.0)
pnl_v2 = backtest_simple(sig_v2[:min_len], r.values[:min_len])
variants['S5v2'] = {'sharpe': calc_sharpe(pnl_v2), 'mdd': calc_mdd(pnl_v2), 'ret': np.sum(pnl_v2)}

# S5v3: EMA 50>200 + RSI confirmation (30-70 oversold/overbought)
print("[S5v3] EMA 50>200 + RSI(14) > 30 (Confirm)...")
ema50 = df['close'].ewm(span=50).mean()
ema200 = df['close'].ewm(span=200).mean()
rsi = calc_rsi(df['close'].values)
sig_v3 = np.where((ema50 > ema200) & (rsi > 30), 1.0, 0.0)
pnl_v3 = backtest_simple(sig_v3[:min_len], r.values[:min_len])
variants['S5v3'] = {'sharpe': calc_sharpe(pnl_v3), 'mdd': calc_mdd(pnl_v3), 'ret': np.sum(pnl_v3)}

# S5 Base (reference)
ema50 = df['close'].ewm(span=50).mean()
ema200 = df['close'].ewm(span=200).mean()
sig_base = np.where(ema50 > ema200, 1.0, 0.0)
pnl_base = backtest_simple(sig_base[:min_len], r.values[:min_len])
variants['S5'] = {'sharpe': calc_sharpe(pnl_base), 'mdd': calc_mdd(pnl_base), 'ret': np.sum(pnl_base)}

print("\n" + "="*80)
print("RESULTS")
print("="*80)
for var, metrics in sorted(variants.items(), key=lambda x: x[1]['sharpe'], reverse=True):
    print(f"{var}: Sharpe {metrics['sharpe']:.3f}, MDD {metrics['mdd']:.1f}%, Return {metrics['ret']:.1f}%")

# Save
with open('/home/user/Quant-Trade/results/s5_variants.json', 'w') as f:
    json.dump(variants, f, indent=2)

print(f"\n✅ Saved\n")
