#!/usr/bin/env python3
"""
Hypothesis H11: Fractal Price Patterns
========================================

MOTIVATION:
  Most signals rely on indicators (RSI, MACD, EMA)
  Price patterns themselves might contain information
  Fractals: self-similar patterns at different scales

  Hypothesis: 3-bar patterns (HHH, LLL, HL, LH) signal reversals

PATTERNS:
  HHH: 3 consecutive higher highs → overbought, short
  LLL: 3 consecutive lower lows → oversold, long
  HL: high then low → whipsaw, revert
  LH: low then high → breakout, follow
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from data_loader import load_ohlc, log_returns_pct

def calc_sharpe(returns, ann=252):
    if len(returns) < 2:
        return 0.0
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    if sigma == 0:
        return 0.0
    return float(mu / sigma * np.sqrt(ann))

def calc_mdd(returns):
    cumsum = np.cumsum(returns)
    peak = np.maximum.accumulate(cumsum)
    dd = cumsum - peak
    return float(np.min(dd))

def calc_metrics(returns):
    sharpe = calc_sharpe(returns)
    mdd = calc_mdd(returns)
    total_ret = np.sum(returns) * 100
    if mdd < 0:
        calmar = total_ret / abs(mdd) if abs(mdd) > 0 else 0
    else:
        calmar = 0
    return {'sharpe': sharpe, 'mdd': mdd, 'return_pct': total_ret, 'calmar': calmar}

def backtest_simple(positions, returns, cost_bps=5):
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    pnl = pnl - turn * (cost_bps / 1e4)
    return pnl

def run_hypothesis_11(data_path, output_path):
    print("\n" + "=" * 70)
    print("HYPOTHESIS H11: FRACTAL PRICE PATTERNS")
    print("=" * 70)

    df = load_ohlc(data_path)
    r = log_returns_pct(df)

    print("[H11] Analyzing 3-bar patterns...")

    # Extract high/low
    highs = df['high'].values
    lows = df['low'].values

    positions = np.zeros(len(df))

    # Look for 3-bar patterns
    for i in range(2, len(df)):
        h0, h1, h2 = highs[i-2], highs[i-1], highs[i]
        l0, l1, l2 = lows[i-2], lows[i-1], lows[i]

        # HHH: 3 higher highs → overbought reversal
        if h0 < h1 < h2:
            positions[i] = -1  # Short (reversal expected)

        # LLL: 3 lower lows → oversold reversal
        elif l0 > l1 > l2:
            positions[i] = 1  # Long (reversal expected)

        # HL: high then low → whipsaw/revert
        elif h0 < h1 and l1 > l2:
            positions[i] = -1  # Short (expect revert down)

        # LH: low then high → follow (breakout)
        elif l0 > l1 and h1 < h2:
            positions[i] = 1  # Long (follow breakout)

    min_len = min(len(positions), len(r))
    pnl = backtest_simple(positions[:min_len], r.values[:min_len])
    metrics = calc_metrics(pnl)

    print(f"[H11] Sharpe: {metrics['sharpe']:.3f}")
    print(f"[H11] MDD: {metrics['mdd']:.1f}")

    results = {
        'hypothesis': 'Fractal Price Patterns (H11)',
        'sharpe': metrics['sharpe'],
        'mdd': metrics['mdd'],
        'return_pct': metrics['return_pct'],
        'interpretation': '3-bar pattern recognition (HHH, LLL, HL, LH)'
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✅ Results saved → {output_path}\n")


if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_11_fractal_patterns.json'
    run_hypothesis_11(data_path, output_path)
