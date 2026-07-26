#!/usr/bin/env python3
"""
S5 + O5 Overlay Combination
============================
S5-OV: S5 signal + O5 vol-of-vol overlay (amplify in low-vol, reduce in high-vol)
S5-LS: Long/Short version of S5 (not just long-only)
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
print("S5 OVERLAY COMBINATIONS")
print("="*80)

df = load_ohlc('/home/user/Quant-Trade/data/nasdaq100_daily.txt')
r = log_returns_pct(df)

min_len = min(len(df), len(r))

# Base S5
ema50 = df['close'].ewm(span=50).mean()
ema200 = df['close'].ewm(span=200).mean()
sig_s5 = np.where(ema50 > ema200, 1.0, 0.0)
pnl_s5 = backtest_simple(sig_s5[:min_len], r.values[:min_len])

print("\nS5 Base: Sharpe {:.3f}, MDD {:.1f}%".format(calc_sharpe(pnl_s5), calc_mdd(pnl_s5)))

# O5: Vol-of-Vol overlay
# When vol is low (< 25th %ile) → amplify to 1.2x
# When vol is high (> 75th %ile) → reduce to 0.5x
# Otherwise → 1.0x
print("\n[S5-OV] S5 + Vol-of-Vol overlay...")
vol_20 = r.rolling(20).std()
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
pnl_s5_ov = backtest_simple(sig_s5_ov, r.values[:min_len])

print("S5-OV: Sharpe {:.3f}, MDD {:.1f}%, Return {:.1f}%".format(
    calc_sharpe(pnl_s5_ov), calc_mdd(pnl_s5_ov), np.sum(pnl_s5_ov)))

# S5-LS: Long/Short version
# EMA50 > EMA200 → Long (+1.0)
# EMA50 < EMA200 → Short (-0.5, less aggressive)
print("\n[S5-LS] S5 Long/Short...")
sig_s5_ls = np.where(ema50 > ema200, 1.0, -0.5)
pnl_s5_ls = backtest_simple(sig_s5_ls[:min_len], r.values[:min_len])

print("S5-LS: Sharpe {:.3f}, MDD {:.1f}%, Return {:.1f}%".format(
    calc_sharpe(pnl_s5_ls), calc_mdd(pnl_s5_ls), np.sum(pnl_s5_ls)))

# Summary
results = {
    'S5': {'sharpe': calc_sharpe(pnl_s5), 'mdd': calc_mdd(pnl_s5), 'ret': np.sum(pnl_s5)},
    'S5-OV': {'sharpe': calc_sharpe(pnl_s5_ov), 'mdd': calc_mdd(pnl_s5_ov), 'ret': np.sum(pnl_s5_ov)},
    'S5-LS': {'sharpe': calc_sharpe(pnl_s5_ls), 'mdd': calc_mdd(pnl_s5_ls), 'ret': np.sum(pnl_s5_ls)}
}

print("\n" + "="*80)
print("RANKING")
print("="*80)
for k, v in sorted(results.items(), key=lambda x: x[1]['sharpe'], reverse=True):
    print(f"{k}: Sharpe {v['sharpe']:.3f}, MDD {v['mdd']:.1f}%, Return {v['ret']:.1f}%")

with open('/home/user/Quant-Trade/results/s5_overlays.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Saved\n")
