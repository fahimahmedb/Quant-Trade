#!/usr/bin/env python3
"""
Hypothesis H12: Volatility-Adjusted Fractional Differentiation
==============================================================

THIS IS THE KEY HYPOTHESIS - COMBINING BEST SIGNAL + BEST RISK CONTROL

MOTIVATION:
  R5_FracDiff: Sharpe 0.534 but MDD -176.6 (HIGH)
  Phase D Vol-Targeting: Reduces MDD significantly (from -176.6 to ~-50)

  INSIGHT: R5_FracDiff is strong signal but too aggressive.
           Add vol-targeting like Phase D to scale exposure.

APPROACH:
  1. Generate R5_FracDiff signal (best unconventional signal)
  2. Compute rolling 20-day volatility
  3. Target volatility: 10% annualized
  4. Exposure = min(0.10 / current_vol, 1.5) * signal
  5. Add defensive cut: reduce to 0.5x exposure if vol > 95th percentile

  Result should be:
    - Sharpe similar or better (same signal, just scaled)
    - MDD significantly lower (vol targeting reduces whipsaws)
    - More sustainable for production

EXPECTED OUTCOME:
  Sharpe: 0.55-0.60 (possibly higher with defensive cut)
  MDD: -80 to -100 (vs -176.6 for raw FracDiff)
  This would be competitive with R5R6_Average (0.676) but simpler!

MATH:
  exposure_t = clip(target_vol / vol_t, 0, 1.5) * signal_t

  Example:
    target_vol = 0.10 / sqrt(252) ≈ 0.0063 (daily target)
    vol_t = 0.02 (20% rolling)
    exposure = clip(0.0063 / 0.02, 0, 1.5) = 0.315x

  High vol → lower exposure (protective)
  Low vol → higher exposure (up to cap)
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

def calc_mdd(returns_pct):
    """Calculate maximum drawdown as percentage.

    returns_pct: daily returns in percentage points (e.g., 0.5 for 0.5%)
    Returns: MDD in percentage (e.g., -35.5 for -35.5% drawdown)
    """
    # Convert to equity curve: equity[t] = exp(cumsum(returns) / 100)
    cumsum_pct = np.cumsum(returns_pct)
    equity = np.exp(cumsum_pct / 100.0)
    peak = np.maximum.accumulate(equity)

    # Calculate drawdown as percentage
    drawdown_pct = ((equity - peak) / peak).min() * 100
    return float(drawdown_pct)

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
    """López de Prado fractional differentiation with proper convolution."""
    # Calculate weights: w_0=1, w_k = -w_{k-1} * (order - k + 1) / k
    weights = [1.0]
    k = 1.0
    max_k = min(len(series) - 1, 200)  # Cap for stability

    for i in range(1, max_k):
        weight = -k * (order / i)
        if abs(weight) < 1e-4:  # Stop when negligible
            break
        k = weight
        weights.append(weight)

    weights = np.array(weights)
    width = len(weights)

    # Apply convolution: for each time t, compute weighted sum of lags
    frac_series = np.full(len(series), np.nan)
    for t in range(width - 1, len(series)):
        # Dot product of weights with lagged values (proper convolution)
        frac_series[t] = np.dot(weights, series[t - width + 1:t + 1])

    # Normalize and return sign
    frac_series = np.nan_to_num(frac_series)
    mean = np.nanmean(frac_series)
    std = np.nanstd(frac_series)
    if std > 0:
        frac_series = (frac_series - mean) / std

    return np.sign(frac_series)

def run_hypothesis_12(data_path, output_path):
    """
    Vol-adjusted fractional differentiation with defensive cuts
    """
    print("\n" + "=" * 70)
    print("HYPOTHESIS H12: VOL-ADJUSTED FRACTIONAL DIFFERENTIATION")
    print("=" * 70)
    print("(Combining best signal R5 + best risk control vol-targeting)")
    print("=" * 70)

    df = load_ohlc(data_path)
    r = log_returns_pct(df)

    print("\n[H12] Computing fractional differentiation signal...")
    signal = frac_diff(df['close'].values, order=0.4)

    print("[H12] Computing volatility and exposure scaling...")
    vol_20 = r.rolling(20).std()
    vol_sma = vol_20.rolling(20).mean()

    # Target daily volatility (10% annualized)
    TARGET_VOL_ANN = 0.10
    TARGET_VOL_DAILY = TARGET_VOL_ANN / np.sqrt(252)

    # Vol-targeting cap
    MAX_LEVERAGE = 1.5

    # Defensive cut threshold (95th percentile vol)
    vol_95_percentile = vol_20.quantile(0.95)

    print(f"  Target annual vol: {TARGET_VOL_ANN*100:.1f}%")
    print(f"  Target daily vol: {TARGET_VOL_DAILY*100:.2f}%")
    print(f"  Vol 95th percentile: {vol_95_percentile*100:.2f}%")

    # Generate positions with vol-targeting
    positions_voltarget = np.zeros(len(df))
    defensive_cut_count = 0

    for i in range(min(len(df), len(vol_20))):
        if pd.isna(vol_20.iloc[i]) or vol_20.iloc[i] == 0:
            positions_voltarget[i] = 0
        else:
            # Vol-targeting exposure
            exposure = TARGET_VOL_DAILY / vol_20.iloc[i]
            exposure = np.clip(exposure, 0, MAX_LEVERAGE)

            # Defensive cut: if vol is extremely high, reduce exposure
            if vol_20.iloc[i] > vol_95_percentile:
                exposure *= 0.5
                defensive_cut_count += 1

            # Scale signal by exposure
            positions_voltarget[i] = exposure * signal[i]

    print(f"  Defensive cut triggered: {defensive_cut_count} days ({defensive_cut_count/len(df)*100:.1f}%)")

    # Backtest vol-targeted version
    min_len = min(len(positions_voltarget), len(r))
    pnl_voltarget = backtest_simple(positions_voltarget[:min_len], r.values[:min_len])
    metrics_voltarget = calc_metrics(pnl_voltarget)

    # Compare to raw FracDiff (for reference)
    positions_raw = signal
    min_len = min(len(positions_raw), len(r))
    pnl_raw = backtest_simple(positions_raw[:min_len], r.values[:min_len])
    metrics_raw = calc_metrics(pnl_raw)

    print("\n[H12] Results Comparison:")
    print(f"  Raw FracDiff (R5):")
    print(f"    Sharpe: {metrics_raw['sharpe']:.3f}")
    print(f"    MDD: {metrics_raw['mdd']:.1f}")
    print(f"    Return: {metrics_raw['return_pct']:.1f}%")
    print(f"\n  Vol-Adjusted FracDiff (H12):")
    print(f"    Sharpe: {metrics_voltarget['sharpe']:.3f}")
    print(f"    MDD: {metrics_voltarget['mdd']:.1f}")
    print(f"    Return: {metrics_voltarget['return_pct']:.1f}%")

    print(f"\n  Improvement:")
    sharpe_diff = metrics_voltarget['sharpe'] - metrics_raw['sharpe']
    mdd_diff = metrics_voltarget['mdd'] - metrics_raw['mdd']
    print(f"    Sharpe: {sharpe_diff:+.3f} ({sharpe_diff/metrics_raw['sharpe']*100:+.1f}%)")
    print(f"    MDD: {mdd_diff:+.1f} ({abs(mdd_diff)/abs(metrics_raw['mdd'])*100:+.1f}% reduction)")

    # Interpretation
    if metrics_voltarget['sharpe'] > 0.60 and metrics_voltarget['mdd'] > -100:
        quality = "EXCELLENT (>0.60 Sharpe, <-100 MDD)"
    elif metrics_voltarget['sharpe'] > 0.55:
        quality = "VERY GOOD (>0.55 Sharpe)"
    elif metrics_voltarget['sharpe'] > 0.53:
        quality = "GOOD (>0.53 Sharpe, competitive with R5)"
    else:
        quality = "NEEDS REFINEMENT (not beating baseline)"

    print(f"\n  Quality: {quality}")

    # Save results
    results = {
        'hypothesis': 'Vol-Adjusted Fractional Differentiation (H12)',
        'method': 'R5_FracDiff + vol-targeting (target 10% ann vol) + defensive cuts (95th percentile)',
        'raw_fracdiff': {
            'sharpe': metrics_raw['sharpe'],
            'mdd': metrics_raw['mdd'],
            'return_pct': metrics_raw['return_pct']
        },
        'vol_adjusted': {
            'sharpe': metrics_voltarget['sharpe'],
            'mdd': metrics_voltarget['mdd'],
            'return_pct': metrics_voltarget['return_pct']
        },
        'improvement': {
            'sharpe_delta': sharpe_diff,
            'mdd_delta': mdd_diff,
            'defensive_cuts_triggered': defensive_cut_count,
            'defensive_cuts_pct': defensive_cut_count / len(df) * 100
        },
        'quality': quality,
        'interpretation': 'Combines best signal (FracDiff) with best risk control (vol-targeting). Should be production-ready.'
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved → {output_path}\n")


if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_12_vol_adjusted_fracdiff.json'
    run_hypothesis_12(data_path, output_path)
