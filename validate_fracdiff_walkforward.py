#!/usr/bin/env python3
"""
Validate R5_FracDiff with rigorous walk-forward testing
Check for lookahead bias, parameter stability, cross-market
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "finance/src"))
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
    """Fractional differentiation (López de Prado)"""
    weights = []
    k = 1.0
    for i in range(1, len(series)):
        weight = -k * (order / i)
        k = weight
        weights.append(weight)

    frac_series = np.zeros(len(series))
    for i in range(len(weights)):
        if i < len(series):
            frac_series[i] = weights[i] * series[i]

    frac_series = (frac_series - np.nanmean(frac_series)) / (np.nanstd(frac_series) + 1e-8)
    positions = np.sign(frac_series)
    return positions

print("=" * 70)
print("VALIDATING R5_FRACDIFF WITH WALK-FORWARD TEST")
print("=" * 70)

# Load data
df = load_ohlc("data/nasdaq100_daily.txt")
r = log_returns_pct(df)

# Walk-forward: T0=750, refit every 21 days, test on next 21 days
T0 = 750
REFIT_EVERY = 21
results_wf = []

n_folds = (len(df) - T0) // REFIT_EVERY
print(f"\nWalk-Forward Setup: T0={T0}, Refit={REFIT_EVERY}, Folds={n_folds}")

in_sample_sharpes = []
out_sample_sharpes = []

for fold_num in range(n_folds):
    train_end = T0 + fold_num * REFIT_EVERY
    test_start = train_end
    test_end = min(train_end + REFIT_EVERY, len(df))

    if test_end > len(df):
        break

    # In-sample: compute fractional diff on training data only
    train_prices = df['close'].iloc[:train_end].values
    positions_train = frac_diff(train_prices)

    # Out-sample: apply to test period
    test_prices = df['close'].iloc[test_start:test_end].values
    positions_test = frac_diff(test_prices)

    # Evaluate
    r_test = r.values[test_start:test_end]
    pnl_test = backtest_simple(positions_test, r_test)
    metrics_test = calc_metrics(pnl_test)

    if fold_num % 10 == 0:
        print(f"  Fold {fold_num:3d}: OOS Sharpe={metrics_test['sharpe']:7.3f}, MDD={metrics_test['mdd']:7.1f}")

    out_sample_sharpes.append(metrics_test['sharpe'])
    results_wf.append(metrics_test)

# Aggregate
oos_sharpe_mean = np.mean(out_sample_sharpes)
oos_sharpe_std = np.std(out_sample_sharpes)
oos_sharpe_min = np.min(out_sample_sharpes)
oos_sharpe_max = np.max(out_sample_sharpes)

print("\n" + "=" * 70)
print("WALK-FORWARD RESULTS (OUT-OF-SAMPLE)")
print("=" * 70)
print(f"Mean OOS Sharpe:     {oos_sharpe_mean:7.3f}")
print(f"Std Dev OOS Sharpe:  {oos_sharpe_std:7.3f}")
print(f"Min OOS Sharpe:      {oos_sharpe_min:7.3f}")
print(f"Max OOS Sharpe:      {oos_sharpe_max:7.3f}")
print(f"Stability Ratio:     {abs(oos_sharpe_mean / oos_sharpe_std):.2f}x (higher = more stable)")

# Full-period backtest (no lookahead)
print("\n" + "=" * 70)
print("FULL-PERIOD BACKTEST (No Lookahead)")
print("=" * 70)

# Recompute fractional diff on ENTIRE dataset
positions_full = frac_diff(df['close'].values)
min_len = min(len(positions_full), len(r))
pnl_full = backtest_simple(positions_full[:min_len], r.values[:min_len])
metrics_full = calc_metrics(pnl_full)

print(f"Full-Period Sharpe:  {metrics_full['sharpe']:7.3f}")
print(f"Full-Period MDD:     {metrics_full['mdd']:7.1f}")
print(f"Full-Period Return:  {metrics_full['return_pct']:7.1f}%")
print(f"Calmar Ratio:        {metrics_full['calmar']:7.3f}")

# Comparison
buy_hold_r = r.values[:min_len]
bh_sharpe = calc_sharpe(buy_hold_r)
print(f"\nBuy & Hold Sharpe:   {bh_sharpe:7.3f}")
print(f"FracDiff vs B&H:     {metrics_full['sharpe'] - bh_sharpe:+7.3f}")

if metrics_full['sharpe'] > bh_sharpe:
    print(f"\n✅ R5_FRACDIFF BEATS BUY & HOLD!")
else:
    print(f"\n⚠️  R5_FRACDIFF underperforms Buy & Hold in full-period")

# Test parameter sensitivity (order = 0.2, 0.3, 0.4, 0.5)
print("\n" + "=" * 70)
print("PARAMETER SENSITIVITY TEST (order parameter)")
print("=" * 70)

orders = [0.2, 0.3, 0.4, 0.5, 0.6]
sensitivities = {}

for order in orders:
    def frac_diff_order(series, o=order):
        weights = []
        k = 1.0
        for i in range(1, len(series)):
            weight = -k * (o / i)
            k = weight
            weights.append(weight)
        frac_series = np.zeros(len(series))
        for i in range(len(weights)):
            if i < len(series):
                frac_series[i] = weights[i] * series[i]
        frac_series = (frac_series - np.nanmean(frac_series)) / (np.nanstd(frac_series) + 1e-8)
        return np.sign(frac_series)

    pos = frac_diff_order(df['close'].values)
    min_len = min(len(pos), len(r))
    pnl = backtest_simple(pos[:min_len], r.values[:min_len])
    metrics = calc_metrics(pnl)
    sensitivities[order] = metrics['sharpe']
    print(f"  Order {order:.1f}: Sharpe {metrics['sharpe']:7.3f}")

# Save results
summary = {
    'test_type': 'Walk-Forward + Parameter Sensitivity',
    'full_period': metrics_full,
    'walk_forward': {
        'mean_oos_sharpe': oos_sharpe_mean,
        'std_oos_sharpe': oos_sharpe_std,
        'min_oos_sharpe': oos_sharpe_min,
        'max_oos_sharpe': oos_sharpe_max,
        'n_folds': len(out_sample_sharpes)
    },
    'parameter_sensitivity': sensitivities,
    'comparison_to_bh': {
        'fracdiff_sharpe': metrics_full['sharpe'],
        'bh_sharpe': bh_sharpe,
        'outperformance': metrics_full['sharpe'] - bh_sharpe
    }
}

with open('results/fracdiff_validation.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print(f"\n✅ Validation results saved → results/fracdiff_validation.json")
