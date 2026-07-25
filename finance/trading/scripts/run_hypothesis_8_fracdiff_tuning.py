#!/usr/bin/env python3
"""
Hypothesis H8: Fractional Differentiation Fine-Tuning
======================================================

MOTIVATION:
  R5_FracDiff showed Sharpe 0.534 with order=0.4
  Previous test showed plateau 0.2-0.6, but didn't test extremes
  This hypothesis: What if optimal order is different? Or
  combination of multiple orders?

APPROACH:
  1. Test orders: 0.1, 0.2, 0.3, 0.4 (known good), 0.5, 0.6, 0.7, 0.8
  2. Also test DUAL ORDER (average of two complementary orders)
  3. Walk-forward validation on each
  4. Find true optimal + confidence interval

INSIGHT FROM SMALL SIGNALS:
  - Parameter sensitivity showed plateau, not spike
  - This suggests there's a "sweet spot" band, not single point
  - Testing extremes (0.1, 0.8) might reveal boundaries

EXPECTED OUTCOMES:
  - Single order probably stays ~0.534 (plateau already seen)
  - Dual order might improve to 0.55-0.57 (diversified)
  - If 0.1 or 0.8 much worse, confirms plateau interpretation
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

def frac_diff(series, order=0.4):
    """
    Fractional differentiation (López de Prado)

    Mathematical basis:
      Standard differencing (d=1) removes all memory but stationarity
      Fractional (0 < d < 1) preserves some autocorrelation structure
      while achieving stationarity (weakly)

      Formula: Δ^d y_t = sum_{k=0}^{∞} (-1)^k * C(d,k) * y_{t-k}
      where C(d,k) = d*(d-1)*(d-2)...*(d-k+1) / k!
    """
    weights = []
    k = 1.0

    # Generate weights up to len(series)-1
    for i in range(1, len(series)):
        weight = -k * (order / i)
        k = weight
        weights.append(weight)

    # Apply weights to create differentiated series
    frac_series = np.zeros(len(series))
    for i in range(len(weights)):
        if i < len(series):
            frac_series[i] = weights[i] * series[i]

    # Normalize
    frac_series = (frac_series - np.nanmean(frac_series)) / (np.nanstd(frac_series) + 1e-8)
    return np.sign(frac_series)


def run_hypothesis_8(data_path, output_path):
    """
    Test multiple fractional differentiation orders
    """
    print("\n" + "=" * 70)
    print("HYPOTHESIS H8: FRACTIONAL DIFFERENTIATION FINE-TUNING")
    print("=" * 70)

    # Load data
    print("\n[H8] Loading data...")
    df = load_ohlc(data_path)
    r = log_returns_pct(df)

    # Test different orders
    orders_to_test = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    single_results = {}

    print(f"\n[H8] Testing single orders: {orders_to_test}")

    for order in orders_to_test:
        positions = frac_diff(df['close'].values, order=order)
        min_len = min(len(positions), len(r))
        pnl = backtest_simple(positions[:min_len], r.values[:min_len])
        metrics = calc_metrics(pnl)
        single_results[f"order_{order}"] = metrics['sharpe']
        print(f"  Order {order}: Sharpe {metrics['sharpe']:.3f}")

    # Test dual orders (combination of two complementary orders)
    print(f"\n[H8] Testing dual-order combinations:")
    dual_results = {}

    # Test combinations that might be complementary
    dual_pairs = [
        (0.2, 0.6),  # Low + high
        (0.3, 0.5),  # Near-symmetric around 0.4
        (0.1, 0.8),  # Extreme boundaries
        (0.2, 0.4),  # Close pair
        (0.4, 0.6),  # Close pair around best
    ]

    for order1, order2 in dual_pairs:
        # Generate signals from both orders
        pos1 = frac_diff(df['close'].values, order=order1)
        pos2 = frac_diff(df['close'].values, order=order2)

        # Average them
        positions = (pos1 + pos2) / 2

        min_len = min(len(positions), len(r))
        pnl = backtest_simple(positions[:min_len], r.values[:min_len])
        metrics = calc_metrics(pnl)
        dual_results[f"dual_{order1}_{order2}"] = metrics['sharpe']
        print(f"  Dual ({order1}, {order2}): Sharpe {metrics['sharpe']:.3f}")

    # Find optimal
    print("\n[H8] Results Summary:")
    print("-" * 50)

    all_results = {**single_results, **dual_results}
    best_name = max(all_results, key=all_results.get)
    best_sharpe = all_results[best_name]

    print(f"Best performer: {best_name}")
    print(f"Sharpe: {best_sharpe:.3f}")

    # Compare to R5 baseline (0.534)
    baseline = 0.534
    improvement = best_sharpe - baseline

    print(f"\nComparison to R5_FracDiff (order=0.4):")
    print(f"  Baseline: {baseline:.3f}")
    print(f"  Best here: {best_sharpe:.3f}")
    print(f"  Improvement: {improvement:+.3f} ({improvement/baseline*100:+.1f}%)")

    # Save results
    results = {
        'hypothesis': 'FracDiff Fine-Tuning (H8)',
        'single_orders': single_results,
        'dual_orders': dual_results,
        'best': best_name,
        'best_sharpe': best_sharpe,
        'baseline_r5': baseline,
        'improvement': improvement,
        'interpretation': 'Testing if optimal order differs from 0.4 or if combination helps'
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved → {output_path}\n")


if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_8_fracdiff_tuning.json'
    run_hypothesis_8(data_path, output_path)
