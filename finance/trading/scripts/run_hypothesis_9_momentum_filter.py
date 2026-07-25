#!/usr/bin/env python3
"""
Hypothesis H9: Momentum + Multi-Timeframe Trend Filter
=======================================================

MOTIVATION:
  H2_Momentum showed Sharpe 0.308 (weak)
  R6_Multiframe showed Sharpe 0.453 (moderate)
  Insight: Combine weak HIGH-FREQ signal with strong TREND FILTER

  Theory: Momentum works for entries, but wrong timeframe causes whipsaws.
          Filter by longer-term trend to reduce false signals.

APPROACH:
  1. Generate H2_Momentum signal (12/26 EMA, 1 if up else -1)
  2. Generate R6_Multiframe signal (3-EMA confluence)
  3. Combine:
     - ONLY trade momentum when trend aligns
     - Reduce position when trend opposes (hedging)
     - Neutral when trend is unclear

MECHANISM:
  if momentum == 1 (bullish signal):
    if trend == 1: position = 1 (full long)
    elif trend == -1: position = -0.3 (hedge, reduce exposure)
    else: position = 0 (neutral)
  Similar for momentum == -1

EXPECTED:
  - Sharpe 0.35-0.40 (better than H2's 0.308)
  - Lower MDD (trend filter reduces whipsaws)
  - Should work because: weak signal + strong filter > weak signal alone
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

def run_hypothesis_9(data_path, output_path):
    """
    Momentum signal filtered by multi-timeframe trend
    """
    print("\n" + "=" * 70)
    print("HYPOTHESIS H9: MOMENTUM + TREND FILTER")
    print("=" * 70)

    # Load data
    print("\n[H9] Loading data...")
    df = load_ohlc(data_path)
    r = log_returns_pct(df)

    # Generate momentum signal (H2)
    print("[H9] Computing momentum signal (12/26 EMA)...")
    ema_12 = df['close'].ewm(span=12).mean()
    ema_26 = df['close'].ewm(span=26).mean()
    momentum = np.where(ema_12 > ema_26, 1, -1)

    # Generate multiframe trend signal (R6)
    print("[H9] Computing multi-timeframe trend filter...")
    ema_daily = df['close'].ewm(span=12).mean()
    ema_weekly = df['close'].ewm(span=60).mean()
    ema_monthly = df['close'].ewm(span=250).mean()

    # Trend score: how many EMAs align
    trend_alignment = (
        (ema_daily > ema_weekly).astype(int) +
        (ema_weekly > ema_monthly).astype(int)
    )  # 0-2 score
    trend = np.where(trend_alignment > 1, 1, np.where(trend_alignment < 1, -1, 0))

    # Combine with three strategies
    print("[H9] Testing combination strategies...")

    # Strategy 1: Simple filter (trade only when aligned)
    print("\n  Strategy 1: Simple Filter (align required)")
    positions_simple = momentum * (trend != 0).astype(int)
    # If trend is unclear (0), reduce to 0
    positions_simple = np.where(trend == 0, 0, positions_simple)

    min_len = min(len(positions_simple), len(r))
    pnl_simple = backtest_simple(positions_simple[:min_len], r.values[:min_len])
    metrics_simple = calc_metrics(pnl_simple)
    print(f"    Sharpe: {metrics_simple['sharpe']:.3f}")

    # Strategy 2: Hedge when opposed (reduce to -0.3 if trend opposes)
    print("\n  Strategy 2: Hedge when opposed")
    positions_hedge = np.zeros_like(momentum, dtype=float)
    for i in range(len(momentum)):
        if momentum[i] == trend[i]:  # Aligned
            positions_hedge[i] = momentum[i]  # Full position
        elif trend[i] == 0:  # Trend unclear
            positions_hedge[i] = momentum[i] * 0.5  # Half position
        else:  # Opposed
            positions_hedge[i] = momentum[i] * (-0.3)  # Hedge (reverse)

    min_len = min(len(positions_hedge), len(r))
    pnl_hedge = backtest_simple(positions_hedge[:min_len], r.values[:min_len])
    metrics_hedge = calc_metrics(pnl_hedge)
    print(f"    Sharpe: {metrics_hedge['sharpe']:.3f}")

    # Strategy 3: Weighted (momentum 70%, trend 30%)
    print("\n  Strategy 3: Weighted (70% momentum, 30% trend)")
    positions_weighted = 0.7 * momentum + 0.3 * trend
    positions_weighted = np.clip(positions_weighted, -1, 1)

    min_len = min(len(positions_weighted), len(r))
    pnl_weighted = backtest_simple(positions_weighted[:min_len], r.values[:min_len])
    metrics_weighted = calc_metrics(pnl_weighted)
    print(f"    Sharpe: {metrics_weighted['sharpe']:.3f}")

    # Compare to baselines
    print("\n[H9] Comparison to baselines:")
    print(f"  H2_Momentum alone:  0.308")
    print(f"  R6_Multiframe alone: 0.453")
    print(f"  H9_Simple filter:   {metrics_simple['sharpe']:.3f}")
    print(f"  H9_Hedge:           {metrics_hedge['sharpe']:.3f}")
    print(f"  H9_Weighted:        {metrics_weighted['sharpe']:.3f}")

    # Pick best
    best_metrics = max(
        ('Simple', metrics_simple),
        ('Hedge', metrics_hedge),
        ('Weighted', metrics_weighted),
        key=lambda x: x[1]['sharpe']
    )

    print(f"\n✓ Best variant: {best_metrics[0]} (Sharpe {best_metrics[1]['sharpe']:.3f})")

    # Save results
    results = {
        'hypothesis': 'Momentum + Trend Filter (H9)',
        'simple_filter': {'sharpe': metrics_simple['sharpe'], 'mdd': metrics_simple['mdd']},
        'hedge_strategy': {'sharpe': metrics_hedge['sharpe'], 'mdd': metrics_hedge['mdd']},
        'weighted_strategy': {'sharpe': metrics_weighted['sharpe'], 'mdd': metrics_weighted['mdd']},
        'best_variant': best_metrics[0],
        'best_sharpe': best_metrics[1]['sharpe'],
        'baseline_h2': 0.308,
        'baseline_r6': 0.453,
        'interpretation': 'Filter weak momentum signal by strong trend to reduce whipsaws'
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved → {output_path}\n")


if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_9_momentum_filter.json'
    run_hypothesis_9(data_path, output_path)
